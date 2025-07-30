import asyncio
import functools
import itertools
from dataclasses import dataclass
from typing import Callable, Iterable, Optional

from tenacity import (
    AsyncRetrying,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from doteval.datasets.base import _registry
from doteval.models import EvaluationSummary, Record, Result
from doteval.progress import EvaluationProgress, get_dataset_info
from doteval.sessions import SessionManager


@dataclass
class EvaluationMetadata:
    """Consolidated metadata for evaluation functions"""

    column_spec: str
    dataset: Iterable
    eval_fn: Callable
    loader: Optional[object] = None
    dataset_name: Optional[str] = None


# Default retry configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0  # Initial delay in seconds
DEFAULT_MAX_DELAY = 30.0  # Maximum delay between retries

# Common connection-related exceptions to retry on
CONNECTION_ERRORS = (
    ConnectionError,
    ConnectionResetError,
    ConnectionAbortedError,
    ConnectionRefusedError,
    TimeoutError,
    OSError,  # Covers network-related OS errors
)


class ForEach:
    def __call__(self, column_spec: str, dataset: Iterable):
        def core_foreach(column_spec: str, dataset: Iterable):
            """
            Decorator that marks a function for running against each item in a dataset.

            When used with `pytest`, the decorated function will be automatically
            executed against all dataset items as part of the evaluation suite.
            Functions decorated by `foreach` can also be executed as normal Python
            functions.

            Args:
                column_spec: Comma-separated list of column names
                dataset: An iterator of tuples or lists, each representing a row of data

            Returns:
                A decorated function that can be used as a regular function or as a `pytest` test

            """

            def decorator(eval_fn: Callable) -> Callable:
                if asyncio.iscoroutinefunction(eval_fn):
                    # Create async wrapper for async eval functions
                    @functools.wraps(eval_fn)
                    async def async_wrapper(*args, **kwargs):
                        # Extract retry parameters if provided
                        max_retries = kwargs.pop("max_retries", DEFAULT_MAX_RETRIES)
                        retry_delay = kwargs.pop("retry_delay", DEFAULT_RETRY_DELAY)
                        return await run_evaluation(
                            eval_fn,
                            column_spec,
                            dataset,
                            eval_fn.__name__,
                            max_retries=max_retries,
                            retry_delay=retry_delay,
                            **kwargs,
                        )

                    # Store consolidated metadata
                    async_wrapper._metadata = EvaluationMetadata(  # type: ignore
                        column_spec=column_spec, dataset=dataset, eval_fn=eval_fn
                    )

                    return async_wrapper
                else:
                    # Create sync wrapper for sync eval functions
                    @functools.wraps(eval_fn)
                    def wrapper(*args, **kwargs):
                        # Extract retry parameters if provided
                        max_retries = kwargs.pop("max_retries", DEFAULT_MAX_RETRIES)
                        retry_delay = kwargs.pop("retry_delay", DEFAULT_RETRY_DELAY)
                        return run_evaluation(
                            eval_fn,
                            column_spec,
                            dataset,
                            eval_fn.__name__,
                            max_retries=max_retries,
                            retry_delay=retry_delay,
                            **kwargs,
                        )

                    # Store consolidated metadata
                    wrapper._metadata = EvaluationMetadata(  # type: ignore
                        column_spec=column_spec, dataset=dataset, eval_fn=eval_fn
                    )

                    return wrapper

            return decorator

        return core_foreach(column_spec, dataset)

    def __getattr__(self, dataset_name: str):
        def dataset_foreach(split: Optional[str] = None, **kwargs):
            dataset_class = _registry.get_dataset_class(dataset_name)
            dataset_instance = (
                dataset_class(split, **kwargs)
                if split is not None
                else dataset_class(**kwargs)
            )
            column_spec = ",".join(dataset_class.columns)

            # Create the decorator
            def decorator(eval_fn: Callable):
                if asyncio.iscoroutinefunction(eval_fn):
                    # Create async wrapper for async eval functions
                    @functools.wraps(eval_fn)
                    async def async_wrapper(*args, **kwargs):
                        # Extract retry parameters if provided
                        max_retries = kwargs.pop("max_retries", DEFAULT_MAX_RETRIES)
                        retry_delay = kwargs.pop("retry_delay", DEFAULT_RETRY_DELAY)
                        return await run_evaluation(
                            eval_fn,
                            column_spec,
                            dataset_instance,
                            eval_fn.__name__,
                            max_retries=max_retries,
                            retry_delay=retry_delay,
                            **kwargs,
                        )

                    # Store consolidated metadata
                    async_wrapper._metadata = EvaluationMetadata(  # type: ignore
                        column_spec=column_spec,
                        dataset=dataset_instance,  # type: ignore
                        eval_fn=eval_fn,
                        loader=dataset_instance,
                        dataset_name=dataset_name,
                    )

                    return async_wrapper
                else:
                    # Create sync wrapper for sync eval functions
                    @functools.wraps(eval_fn)
                    def wrapper(*args, **kwargs):
                        # Extract retry parameters if provided
                        max_retries = kwargs.pop("max_retries", DEFAULT_MAX_RETRIES)
                        retry_delay = kwargs.pop("retry_delay", DEFAULT_RETRY_DELAY)
                        return run_evaluation(
                            eval_fn,
                            column_spec,
                            dataset_instance,
                            eval_fn.__name__,
                            max_retries=max_retries,
                            retry_delay=retry_delay,
                            **kwargs,
                        )

                    # Store consolidated metadata
                    wrapper._metadata = EvaluationMetadata(  # type: ignore
                        column_spec=column_spec,
                        dataset=dataset_instance,  # type: ignore
                        eval_fn=eval_fn,
                        loader=dataset_instance,
                        dataset_name=dataset_name,
                    )

                    return wrapper

            # Add metadata for introspection
            decorator._dataset_name = dataset_name  # type: ignore
            decorator._split = split  # type: ignore
            return decorator

        return dataset_foreach


foreach = ForEach()


def run_evaluation(
    eval_fn: Callable,
    column_spec: str,
    dataset: Iterable,
    evaluation_name: str,
    max_concurrency: int = 10,
    samples: Optional[int] = None,
    session_manager: Optional[SessionManager] = None,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_delay: float = DEFAULT_RETRY_DELAY,
    **kwargs,
) -> EvaluationSummary:
    """
    Run an evaluation function against each item in a dataset.

    Args:
        eval_fn: The function to run for each dataset item
        column_spec: Comma-separated list of column names
        dataset: An iterator of tuples or lists, each representing a row of data
        max_concurrency: The maximum number of concurrent requests
        samples: Maximum number of dataset samples to evaluate (None for all)
        session_manager: The current session's session manager
        max_retries: Maximum number of retry attempts for connection errors (default: 3)
        retry_delay: Initial delay between retries in seconds (default: 1.0)
        **kwargs: Additional arguments to pass to the evaluation function

    Returns:
        An EvaluationSummary containing all results

    """
    if session_manager:
        session_manager.start_evaluation(evaluation_name)

    columns = [col.strip() for col in column_spec.split(",")]

    # Get dataset info for progress tracking
    dataset_info = get_dataset_info(dataset)

    # Adjust total count if samples parameter is specified
    if samples is not None and dataset_info.get("total_rows") is not None:
        dataset_info["total_rows"] = min(samples, dataset_info["total_rows"])

    # Batch remove from storage all the elements that errored out in the
    # previous run
    completed_ids: set[int] = set()
    items_to_retry: set[int] = set()
    if session_manager and session_manager.current_experiment:
        # Get successfully completed items
        completed_items = session_manager.storage.completed_items(
            session_manager.current_experiment, evaluation_name
        )
        completed_ids = set(completed_items)

        all_results = session_manager.storage.get_results(
            session_manager.current_experiment, evaluation_name
        )
        all_item_ids = {r.item_id for r in all_results}
        items_to_retry = all_item_ids - completed_ids

        if items_to_retry:
            session_manager.storage.remove_error_results_batch(
                session_manager.current_experiment,
                evaluation_name,
                list(items_to_retry),
            )

    dataset = itertools.islice(dataset, None, samples)
    dataset = (
        (item_id, row_data)
        for item_id, row_data in enumerate(dataset)
        if item_id not in completed_ids
    )

    if asyncio.iscoroutinefunction(eval_fn):
        return _run_evaluation_async(
            evaluation_name,
            eval_fn,
            columns,
            dataset,
            max_concurrency,
            session_manager,
            samples,
            dataset_info,
            max_retries,
            retry_delay,
            **kwargs,
        )
    else:
        return _run_evaluation_sync(
            evaluation_name,
            eval_fn,
            columns,
            dataset,
            session_manager,
            samples,
            dataset_info,
            max_retries,
            retry_delay,
            **kwargs,
        )


def _run_evaluation_sync(
    evaluation_name,
    eval_fn,
    columns,
    dataset,
    session_manager,
    samples,
    dataset_info,
    max_retries,
    retry_delay,
    **kwargs,
):
    """
    Run the evaluation when `eval_fn` is a Python function, against
    each item in the dataset.

    Args:
        evaluation_name: The name of the evaluation currently being run
        eval_fn: The function to run for each dataset item
        column_spec: List of column names
        dataset: An iterator of tuples or lists, each representing a row of data
        session_manager: The current session's session manager
        **kwargs: Additional arguments to pass to the evaluation function

    Returns:
        An EvaluationSummary containing all results

    """
    if not session_manager:
        raise ValueError("Session manager is required for evaluation")

    with EvaluationProgress(evaluation_name, dataset_info) as progress:
        for item_id, row_data in dataset:
            row_dict = {col: data for col, data in zip(columns, row_data)}

            try:
                # Apply retry logic for connection errors
                if max_retries > 0:
                    retrying = Retrying(
                        stop=stop_after_attempt(
                            max_retries + 1
                        ),  # +1 for initial attempt
                        wait=wait_exponential(
                            multiplier=retry_delay, max=DEFAULT_MAX_DELAY
                        ),
                        retry=retry_if_exception_type(CONNECTION_ERRORS),
                        reraise=True,
                    )
                    sample = retrying(eval_fn, **row_dict, **kwargs)
                else:
                    sample = eval_fn(**row_dict, **kwargs)

                if not isinstance(sample, Result):
                    raise ValueError("Evaluation functions must return a Result object")

                result = Record(sample, item_id, row_dict)
            except Exception as e:
                # Create a Result with False scores for error cases
                # We'll determine the correct scores structure from successful results
                error_result = Result(prompt="", scores=[])
                error_msg = f"{type(e).__name__}: {str(e)}"
                result = Record(error_result, item_id, row_dict, error_msg)

            progress.update_progress(result)
            session_manager.add_results(evaluation_name, [result])

    results = session_manager.get_results(evaluation_name)

    return EvaluationSummary(results)


async def _run_evaluation_async(
    evaluation_name,
    eval_fn,
    columns,
    dataset,
    max_concurrency,
    session_manager,
    samples,
    dataset_info,
    max_retries,
    retry_delay,
    **kwargs,
):
    """
    Run the evaluation when `eval_fn` is a coroutine, against each item in the
    dataset.

    Args:
        evaluation_name: The name of the current evaluation
        eval_fn: The function to run for each dataset item
        column_spec: List of column names
        dataset: An iterator of tuples or lists, each representing a row of data
        max_concurrency: The maximum number of concurrent requests
        session_manager: The current session's session manager
        **kwargs: Additional arguments to pass to the evaluation function

    Returns:
        An EvaluationSummary containing all results

    """

    async def process_item(item_id, row_data):
        row_dict = {col: data for col, data in zip(columns, row_data)}

        try:
            # Apply retry logic for connection errors
            if max_retries > 0:
                async_retrying = AsyncRetrying(
                    stop=stop_after_attempt(max_retries + 1),  # +1 for initial attempt
                    wait=wait_exponential(
                        multiplier=retry_delay, max=DEFAULT_MAX_DELAY
                    ),
                    retry=retry_if_exception_type(CONNECTION_ERRORS),
                    reraise=True,
                )
                sample = await async_retrying(eval_fn, **row_dict, **kwargs)
            else:
                sample = await eval_fn(**row_dict, **kwargs)

            if not isinstance(sample, Result):
                raise ValueError("Evaluation functions must return a Result object")

            result = Record(sample, item_id, row_dict)

        except Exception as e:
            # Create empty Result for error cases
            empty_result = Result(prompt="", scores=[])
            error_msg = f"{type(e).__name__}: {str(e)}"
            result = Record(empty_result, item_id, row_dict, error_msg)

        session_manager.add_results(evaluation_name, [result])
        return result

    if not session_manager:
        raise ValueError("Session manager is required for evaluation")

    # To keep processing `max_concurrency` items at all times we use a sliding window
    pending_tasks = set()

    with EvaluationProgress(
        evaluation_name, dataset_info, show_individual_tasks=True
    ) as progress:
        try:
            # FIll the initial window to `max_concurrency`
            for _ in range(max_concurrency):
                try:
                    item_id, row_data = next(dataset)
                    task = asyncio.create_task(process_item(item_id, row_data))
                    pending_tasks.add(task)
                except StopIteration:
                    break

            while pending_tasks:
                done, pending_tasks = await asyncio.wait(
                    pending_tasks, return_when=asyncio.FIRST_COMPLETED
                )

                for task in done:
                    result = await task
                    progress.update_progress(result)

                for _ in range(len(done)):
                    try:
                        item_id, row_data = next(dataset)
                        task = asyncio.create_task(process_item(item_id, row_data))
                        pending_tasks.add(task)
                    except StopIteration:
                        break

        except Exception:
            # Cancel remaining tasks on error
            for task in pending_tasks:
                task.cancel()
            raise

    results = session_manager.get_results(evaluation_name)

    return EvaluationSummary(results)
