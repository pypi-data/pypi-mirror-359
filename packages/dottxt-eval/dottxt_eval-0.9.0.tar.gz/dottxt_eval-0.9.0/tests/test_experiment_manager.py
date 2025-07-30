import re
import tempfile
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from doteval.models import Evaluation, EvaluationStatus, Record, Result, Score
from doteval.sessions import SessionManager, get_git_commit
from doteval.storage import JSONStorage


@pytest.fixture
def temp_storage_dir(tmp_path):
    """Create a temporary directory for storage tests."""
    return tmp_path


def test_session_manager_init_without_experiment():
    """Test SessionManager initialization without experiment creates ephemeral experiment."""
    manager = SessionManager()
    assert manager.storage is not None
    assert manager.current_experiment is not None  # Should create ephemeral experiment
    assert ".doteval/" in manager.current_experiment
    assert manager.evaluation_progress is None
    assert manager.active_evaluations == set()


def test_session_manager_init_with_experiment(temp_storage_dir):
    """Test SessionManager initialization with experiment."""
    storage_path = f"json://{temp_storage_dir}"
    experiment_name = "test_experiment"

    manager = SessionManager(storage_path, experiment_name)

    assert manager.current_experiment == experiment_name
    # Check that experiment was created
    experiments = manager.storage.list_experiments()
    assert experiment_name in experiments


@patch("doteval.sessions.get_git_commit")
def test_start_evaluation(mock_git_commit, temp_storage_dir):
    """Test starting a new evaluation."""
    mock_git_commit.return_value = "abc123"
    storage_path = f"json://{temp_storage_dir}"

    manager = SessionManager(storage_path, "test_exp")
    manager.start_evaluation("test_eval")

    assert manager.evaluation_progress is not None
    assert manager.evaluation_progress.evaluation_name == "test_eval"
    assert "test_eval" in manager.active_evaluations

    # Check that evaluation was created in storage
    loaded_eval = manager.storage.load_evaluation("test_exp", "test_eval")
    assert loaded_eval is not None
    assert loaded_eval.status == EvaluationStatus.RUNNING
    assert loaded_eval.metadata["git_commit"] == "abc123"


def test_resume_evaluation(temp_storage_dir):
    """Test resuming an existing evaluation."""
    storage_path = f"json://{temp_storage_dir}"

    # First, create an evaluation with some results
    manager1 = SessionManager(storage_path, "test_exp")
    manager1.start_evaluation("test_eval")

    # Add some results
    score = Score("test_evaluator", True, [], {})
    result = Result(prompt="test prompt", scores=[score])
    record = Record(result=result, item_id=0, dataset_row={})
    manager1.add_results("test_eval", [record])

    # Create a new manager and resume
    manager2 = SessionManager(storage_path, "test_exp")
    manager2.start_evaluation("test_eval")

    # Should detect it's resuming
    # (In real usage, this would print a message about resuming)


def test_add_results(temp_storage_dir):
    """Test adding results through SessionManager."""
    storage_path = f"json://{temp_storage_dir}"
    manager = SessionManager(storage_path, "test_exp")
    manager.start_evaluation("test_eval")

    score = Score("test_evaluator", True, [], {})
    result = Result(prompt="test prompt", scores=[score])
    record = Record(result=result, item_id=0, dataset_row={})

    manager.add_results("test_eval", [record])

    # Check that results were added
    results = manager.get_results("test_eval")
    assert len(results) == 1
    assert results[0].item_id == 0

    # Check progress tracking
    assert manager.evaluation_progress.completed_count == 1
    assert manager.evaluation_progress.error_count == 0


def test_add_results_with_errors(temp_storage_dir):
    """Test adding results with errors."""
    storage_path = f"json://{temp_storage_dir}"
    manager = SessionManager(storage_path, "test_exp")
    manager.start_evaluation("test_eval")

    score = Score("test_evaluator", False, [], {})
    result = Result(prompt="test prompt", scores=[score])

    # Create one successful and one failed record
    record1 = Record(result=result, item_id=0, dataset_row={})
    record2 = Record(result=result, item_id=1, dataset_row={}, error="Test error")

    manager.add_results("test_eval", [record1, record2])

    # Check progress tracking
    assert manager.evaluation_progress.completed_count == 2
    assert manager.evaluation_progress.error_count == 1


def test_finish_evaluation(temp_storage_dir):
    """Test finishing an evaluation."""
    storage_path = f"json://{temp_storage_dir}"
    manager = SessionManager(storage_path, "test_exp")
    manager.start_evaluation("test_eval")

    # Finish successfully
    manager.finish_evaluation("test_eval", success=True)

    # Check that status was updated
    loaded_eval = manager.storage.load_evaluation("test_exp", "test_eval")
    assert loaded_eval.status == EvaluationStatus.COMPLETED
    assert loaded_eval.completed_at is not None

    # Start another evaluation and finish with failure
    manager.start_evaluation("test_eval2")
    manager.finish_evaluation("test_eval2", success=False)

    loaded_eval2 = manager.storage.load_evaluation("test_exp", "test_eval2")
    assert loaded_eval2.status == EvaluationStatus.FAILED


def test_finish_all_evaluations(temp_storage_dir):
    """Test finishing all active evaluations."""
    storage_path = f"json://{temp_storage_dir}"
    manager = SessionManager(storage_path, "test_exp")

    # Start multiple evaluations
    manager.start_evaluation("eval1")
    manager.start_evaluation("eval2")
    manager.start_evaluation("eval3")

    assert len(manager.active_evaluations) == 3

    # Finish all
    manager.finish_all(success=True)

    # Check all were marked as completed
    for eval_name in ["eval1", "eval2", "eval3"]:
        loaded = manager.storage.load_evaluation("test_exp", eval_name)
        assert loaded.status == EvaluationStatus.COMPLETED


@patch("subprocess.check_output")
def test_get_git_commit_success(mock_check_output):
    """Test getting git commit when git is available."""
    mock_check_output.return_value = b"abc123def456\n"

    commit = get_git_commit()

    assert commit == "abc123de"  # First 8 characters


@patch("subprocess.check_output")
def test_get_git_commit_failure(mock_check_output):
    """Test getting git commit when git fails."""
    import subprocess

    mock_check_output.side_effect = subprocess.CalledProcessError(1, "git")

    commit = get_git_commit()

    assert commit is None


# Additional tests to increase sessions.py coverage are included above


def test_session_manager_operations_with_ephemeral_experiment():
    """Test SessionManager operations with ephemeral experiment."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create session manager without experiment name - creates ephemeral
        session_manager = SessionManager(f"json://{temp_dir}")

        # Should have created ephemeral experiment
        assert session_manager.current_experiment is not None
        assert ".doteval/" in session_manager.current_experiment

        # All operations should work with ephemeral experiment
        session_manager.start_evaluation("test_eval")

        result = Result(prompt="test", scores=[])
        record = Record(result=result, item_id=0, dataset_row={})
        session_manager.add_results("test_eval", [record])

        results = session_manager.get_results("test_eval")
        assert len(results) == 1

        session_manager.finish_evaluation("test_eval")


def test_session_manager_add_results_without_progress():
    """Test adding results when evaluation_progress is None."""
    with tempfile.TemporaryDirectory() as temp_dir:
        session_manager = SessionManager(
            f"json://{temp_dir}", experiment_name="test_exp"
        )

        # Don't call start_evaluation, so evaluation_progress remains None
        session_manager.evaluation_progress = None

        # Create evaluation manually to avoid the start_evaluation logic
        evaluation = Evaluation(
            evaluation_name="test_eval",
            status=EvaluationStatus.RUNNING,
            started_at=time.time(),
        )
        session_manager.storage.create_evaluation("test_exp", evaluation)

        # Add results without evaluation_progress
        result = Result(prompt="test", scores=[])
        record = Record(result=result, item_id=0, dataset_row={})

        # This should work even without evaluation_progress
        session_manager.add_results("test_eval", [record])

        # Verify results were added
        results = session_manager.get_results("test_eval")
        assert len(results) == 1


def test_ephemeral_experiment_created_when_no_name():
    """Test that ephemeral experiment is created with timestamp when no name provided."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = f"json://{temp_dir}"

        # Create session manager without experiment name
        session_manager = SessionManager(storage_path)

        # Should have created an ephemeral experiment
        assert session_manager.current_experiment is not None
        assert ".doteval/" in session_manager.current_experiment

        # Extract timestamp and verify format
        timestamp = session_manager.current_experiment.split("/")[-1]
        assert re.match(r"\d{8}_\d{6}", timestamp)

        # Verify experiment was created in storage
        storage = JSONStorage(temp_dir)
        experiments = storage.list_experiments()
        # The root storage sees ".doteval" as an experiment directory
        assert ".doteval" in experiments

        # Check the actual ephemeral experiments inside .doteval
        doteval_storage = JSONStorage(str(Path(temp_dir) / ".doteval"))
        ephemeral_experiments = doteval_storage.list_experiments()
        assert len(ephemeral_experiments) == 1
        assert ephemeral_experiments[0] == timestamp


def test_ephemeral_experiment_in_doteval_directory():
    """Test ephemeral experiments are created in .doteval subdirectory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        doteval_dir = Path(temp_dir) / ".doteval"
        storage_path = f"json://{doteval_dir}"

        # Create session manager without experiment name
        session_manager = SessionManager(storage_path)

        # Should create experiment directly with timestamp (not .doteval/.doteval/timestamp)
        timestamp_pattern = re.compile(r"^\d{8}_\d{6}$")
        assert timestamp_pattern.match(session_manager.current_experiment)

        # Verify directory structure
        assert doteval_dir.exists()
        exp_dir = doteval_dir / session_manager.current_experiment
        assert exp_dir.exists()


def test_ephemeral_experiment_timestamp_format():
    """Test that ephemeral experiment timestamp matches expected format."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = f"json://{temp_dir}"

        # Create session manager
        before_time = datetime.now()
        session_manager = SessionManager(storage_path)
        after_time = datetime.now()

        # Extract timestamp
        timestamp_str = session_manager.current_experiment.split("/")[-1]

        # Parse timestamp
        timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")

        # Verify timestamp is within expected range (ignoring microseconds)
        assert before_time.replace(microsecond=0) <= timestamp <= after_time


def test_multiple_ephemeral_experiments():
    """Test creating multiple ephemeral experiments."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = f"json://{temp_dir}"

        # Create multiple session managers with small delays to ensure different timestamps
        managers = []
        for i in range(3):
            if i > 0:
                time.sleep(
                    1.1
                )  # Sleep just over 1 second to ensure different timestamp
            manager = SessionManager(storage_path)
            managers.append(manager)

        # All should have different experiment names
        experiment_names = [m.current_experiment for m in managers]
        assert len(set(experiment_names)) == 3

        # Verify all experiments exist in .doteval directory
        doteval_storage = JSONStorage(str(Path(temp_dir) / ".doteval"))
        ephemeral_experiments = doteval_storage.list_experiments()
        assert len(ephemeral_experiments) == 3

        # All should have timestamp format
        for exp in ephemeral_experiments:
            assert re.match(r"\d{8}_\d{6}", exp)
