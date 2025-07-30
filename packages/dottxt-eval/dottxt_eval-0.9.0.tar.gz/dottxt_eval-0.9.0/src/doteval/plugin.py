import asyncio
import inspect

import pytest

from doteval.core import run_evaluation
from doteval.sessions import SessionManager


@pytest.hookimpl
def pytest_addoption(parser):
    """Add command line options that are specific to doteval"""
    parser.addoption(
        "--samples", type=int, help="Maximum number of dataset samples to evaluate"
    )
    parser.addoption("--experiment", type=str, help="Name of the experiment")
    parser.addoption("--storage", type=str, help="Path of the session storage")
    parser.addoption(
        "--max-concurrency", type=int, help="Maximum number of concurrent requests"
    )
    parser.addoption(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum number of retry attempts for connection errors (default: 3)",
    )
    parser.addoption(
        "--retry-delay",
        type=float,
        default=1.0,
        help="Initial delay between retries in seconds (default: 1.0)",
    )


@pytest.hookimpl
def pytest_configure(config):
    """Configure pytest.

    We configure pytest to also collect files prefixed by `eval_` and
    functions also prefixed by `eval_`.

    """
    config.addinivalue_line("markers", "doteval: mark test as LLM evaluation")
    config.addinivalue_line("python_files", "eval_*.py")
    config.addinivalue_line("python_functions", "eval_*")
    config._evaluation_results = {}


@pytest.hookimpl
def pytest_pyfunc_call(pyfuncitem):
    """Intercept function calls for doteval functions"""
    if hasattr(pyfuncitem.function, "_metadata"):
        # For doteval functions, return True to indicate we handled the call
        # This prevents the RuntimeError from the wrapper
        return True


@pytest.hookimpl
def pytest_generate_tests(metafunc):
    """Handle doteval functions - minimal parametrization to prevent fixture errors"""
    if hasattr(metafunc.function, "_metadata"):
        metadata = metafunc.function._metadata
        columns = [col.strip() for col in metadata.column_spec.split(",")]

        # Only parametrize dataset columns that pytest thinks are fixtures
        for column in columns:
            if column in metafunc.fixturenames:
                metafunc.parametrize(column, [None])


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    """Mark evaluations and enable output for progress bars.

    This allows users to only run evals or regular tests with:

        >>> pytest -m "doteval"
        >>> pytest -m "not doteval"

    """
    for item in items:
        if hasattr(item.function, "_metadata"):
            item.add_marker(pytest.mark.doteval)

    # Note: Users should use -s flag to see progress bars
    # Future: Could auto-enable output for better UX


@pytest.hookimpl
def pytest_runtest_setup(item):
    """Setup phase.

    For doteval functions, we skip normal pytest setup since
    we handle everything in pytest_runtest_call.
    """
    if hasattr(item.function, "_metadata"):
        # Collect options for later use
        samples = item.config.getoption("--samples")
        item._samples = samples
        experiment = item.config.getoption("--experiment")
        item._experiment = experiment
        storage = item.config.getoption("--storage")
        item._storage = storage
        max_concurrency = item.config.getoption("--max-concurrency")
        item._max_concurrency = max_concurrency if max_concurrency is not None else 10
        max_retries = item.config.getoption("--max-retries")
        item._max_retries = max_retries
        retry_delay = item.config.getoption("--retry-delay")
        item._retry_delay = retry_delay

        # Skip normal pytest fixture resolution by not calling fixtures
        # pytest_runtest_call will handle everything


@pytest.hookimpl
def pytest_sessionstart(session):
    experiment_name = session.config.getoption("--experiment")
    storage_path = session.config.getoption("--storage")

    # Always create a session manager - it will handle ephemeral experiments if no name
    session_manager = SessionManager(storage_path, experiment_name)
    session.config._session_manager = session_manager


@pytest.hookimpl
def pytest_sessionfinish(session, exitstatus):
    """Finish the evaluation session when pytest completes."""
    session_manager = getattr(session.config, "_session_manager", None)
    if session_manager:
        # Finish with success=True only if all tests passed (exitstatus == 0)
        session_manager.finish_all(success=(exitstatus == 0))


@pytest.hookimpl
def pytest_runtest_call(item):
    """Execute the evaluation function"""
    if hasattr(item.function, "_metadata"):
        metadata = item.function._metadata
        samples = getattr(item, "_samples", None)
        session_manager = getattr(item.config, "_session_manager", None)
        max_concurrency = getattr(item, "_max_concurrency", None)
        max_retries = getattr(item, "_max_retries", 3)
        retry_delay = getattr(item, "_retry_delay", 1.0)

        # Get the evaluation function signature
        sig = inspect.signature(metadata.eval_fn)
        expected_params = set(sig.parameters.keys())

        # Remove dataset columns from expected params
        columns = {col.strip() for col in metadata.column_spec.split(",")}
        expected_fixture_params = expected_params - columns

        # Get fixture values that the function actually expects
        fixture_kwargs = {}
        if hasattr(item, "funcargs"):
            for param_name in expected_fixture_params:
                if param_name in item.funcargs:
                    fixture_kwargs[param_name] = item.funcargs[param_name]

        evaluation_name = item.name

        # Call run_evaluation - it returns a coroutine for async functions
        result = run_evaluation(
            metadata.eval_fn,
            metadata.column_spec,
            metadata.dataset,
            evaluation_name,
            max_concurrency,
            samples,
            session_manager,
            max_retries,
            retry_delay,
            **fixture_kwargs,
        )

        # If it's a coroutine, run it with asyncio.run
        if asyncio.iscoroutine(result):
            result = asyncio.run(result)

        item.config._evaluation_results[evaluation_name] = result
