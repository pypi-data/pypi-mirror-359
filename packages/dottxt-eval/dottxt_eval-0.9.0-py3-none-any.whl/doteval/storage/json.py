import base64
import io
import json
import time
from pathlib import Path
from typing import Any, Optional

from PIL import Image

from doteval.metrics import registry
from doteval.models import Evaluation, EvaluationStatus, Record, Result, Score
from doteval.storage.base import Storage, _registry

__all__ = ["JSONStorage"]


class JSONStorage(Storage):
    def __init__(self, storage_path: str):
        self.root_dir = Path(storage_path)
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def create_experiment(self, experiment_name: str):
        experiment_path = self.root_dir / experiment_name
        experiment_path.mkdir(parents=True, exist_ok=True)

    def delete_experiment(self, experiment_name: str):
        experiment_path = self.root_dir / experiment_name

        if experiment_path.exists() and experiment_path.is_dir():
            # Delete all files in the experiment directory
            for file in experiment_path.iterdir():
                if file.is_file():
                    file.unlink()
            # Delete the directory
            experiment_path.rmdir()
        else:
            raise ValueError(f"Experiment '{experiment_name}' not found.")

    def rename_experiment(self, old_name: str, new_name: str):
        old_dir = self.root_dir / old_name
        new_dir = self.root_dir / new_name

        if not old_dir.exists():
            raise ValueError(f"Experiment '{old_name}' not found")

        if new_dir.exists():
            raise ValueError(f"Experiment '{new_name}' already exists")

        old_dir.rename(new_dir)

    def list_experiments(self):
        return [p.name for p in self.root_dir.iterdir() if p.is_dir()]

    def create_evaluation(self, experiment_name: str, evaluation: Evaluation):
        file_path = (
            self.root_dir / experiment_name / f"{evaluation.evaluation_name}.jsonl"
        )

        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        data: dict = {
            "evaluation_name": evaluation.evaluation_name,
            "metadata": evaluation.metadata,
            "started_at": evaluation.started_at,
            "status": evaluation.status.value,
            "completed_at": evaluation.completed_at,
        }

        with open(file_path, "w") as f:
            json.dump(data, f)

    def list_evaluations(self, experiment_name: str) -> list[str]:
        path = self.root_dir / experiment_name
        return [f.stem for f in path.glob("*.jsonl")]

    def add_results(
        self,
        experiment_name: str,
        evaluation_name: str,
        results: list[Record],
    ):
        file_path = self.root_dir / experiment_name / f"{evaluation_name}.jsonl"

        if not file_path.exists():
            raise ValueError(
                f"Evaluation '{evaluation_name}' not found. Create evaluation first."
            )

        with open(file_path, "a") as f:
            data = serialize(results)
            for result in data:
                f.write("\n")
                json.dump(result, f)

    def get_results(self, experiment_name: str, evaluation_name: str) -> list[Record]:
        file_path = self.root_dir / experiment_name / f"{evaluation_name}.jsonl"
        if not file_path.exists():
            return []

        try:
            results = []
            with open(file_path) as f:
                # Skip the first line (evaluation metadata)
                f.readline()
                # Read all result lines
                for line in f:
                    if line.strip():  # Skip empty lines
                        results.append(json.loads(line))
            return deserialize(results)
        except json.JSONDecodeError:
            return []

    def load_evaluation(
        self, experiment_name: str, evaluation_name: str
    ) -> Optional[Evaluation]:
        file_path = self.root_dir / experiment_name / f"{evaluation_name}.jsonl"
        if not file_path.exists():
            return None

        with open(file_path) as f:
            first_line = f.readline()
            if first_line:
                data = json.loads(first_line)
                return Evaluation(
                    evaluation_name=data["evaluation_name"],
                    status=EvaluationStatus(data["status"]),
                    started_at=data["started_at"],
                    metadata=data["metadata"],
                    completed_at=data.get("completed_at"),
                )
        return None

    def update_evaluation_status(
        self, experiment_name: str, evaluation_name: str, status
    ):
        file_path = self.root_dir / experiment_name / f"{evaluation_name}.jsonl"
        if not file_path.exists():
            raise ValueError(f"Evaluation '{evaluation_name}' not found")

        # Read all lines
        with open(file_path) as f:
            lines = f.readlines()

        # Update the first line
        if lines:
            eval_data = json.loads(lines[0])
            eval_data["status"] = status.value
            eval_data["completed_at"] = (
                time.time() if status == EvaluationStatus.COMPLETED else None
            )
            lines[0] = json.dumps(eval_data) + "\n"

            # Write back
            with open(file_path, "w") as f:
                f.writelines(lines)

    def remove_error_result(
        self, experiment_name: str, evaluation_name: str, item_id: int
    ):
        """Remove an errored result for a specific item that will be retried."""
        file_path = self.root_dir / experiment_name / f"{evaluation_name}.jsonl"
        if not file_path.exists():
            return

        # Read all lines
        with open(file_path) as f:
            lines = f.readlines()

        if len(lines) <= 1:  # Only metadata, no results
            return

        # Filter out the error result for the specified item_id
        new_lines = [lines[0]]  # Keep metadata
        for line in lines[1:]:
            if line.strip():
                result = json.loads(line)
                # Only keep results that are not the error result for this item
                if result.get("item_id") != item_id or result.get("error") is None:
                    new_lines.append(line)

        # Write back the filtered lines
        with open(file_path, "w") as f:
            f.writelines(new_lines)

    def remove_error_results_batch(
        self, experiment_name: str, evaluation_name: str, item_ids: list[int]
    ):
        """Remove multiple errored results efficiently in a single pass."""
        if not item_ids:
            return

        file_path = self.root_dir / experiment_name / f"{evaluation_name}.jsonl"
        if not file_path.exists():
            return

        item_ids_set = set(item_ids)

        # Read all lines
        with open(file_path) as f:
            lines = f.readlines()

        if len(lines) <= 1:  # Only metadata, no results
            return

        # Filter out error results for all specified item_ids in one pass
        new_lines = [lines[0]]  # Keep metadata
        for line in lines[1:]:
            if line.strip():
                result = json.loads(line)
                # Only keep results that are not error results for the specified items
                if (
                    result.get("item_id") not in item_ids_set
                    or result.get("error") is None
                ):
                    new_lines.append(line)

        # Write back the filtered lines once
        with open(file_path, "w") as f:
            f.writelines(new_lines)

    def completed_items(self, experiment_name: str, evaluation_name: str) -> list[int]:
        file_path = self.root_dir / experiment_name / f"{evaluation_name}.jsonl"
        if not file_path.exists():
            return []

        with open(file_path) as f:
            # Skip first line (metadata)
            f.readline()
            # Collect item IDs from results, excluding errored items
            item_ids = []
            for line in f:
                if line.strip():
                    result = json.loads(line)
                    # Only include items that completed successfully (no error)
                    if result.get("error") is None:
                        item_ids.append(result["item_id"])
            return item_ids


def _serialize_value(value: Any) -> Any:
    """Recursively serialize values, converting PIL Images to base64."""
    if isinstance(value, Image.Image):
        # Convert PIL Image to base64
        buffered = io.BytesIO()
        value.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        return {
            "__type__": "PIL.Image",
            "data": img_base64,
            "mode": value.mode,
            "size": value.size,
        }
    elif isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_serialize_value(item) for item in value]
    elif isinstance(value, tuple):
        return {"__type__": "tuple", "data": [_serialize_value(item) for item in value]}
    else:
        return value


def _deserialize_value(value: Any) -> Any:
    """Recursively deserialize values, converting base64 back to PIL Images."""
    if isinstance(value, dict):
        if value.get("__type__") == "PIL.Image":
            # Convert base64 back to PIL Image
            img_data = base64.b64decode(value["data"])
            img = Image.open(io.BytesIO(img_data))
            return img
        elif value.get("__type__") == "tuple":
            return tuple(_deserialize_value(item) for item in value["data"])
        else:
            return {k: _deserialize_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_deserialize_value(item) for item in value]
    else:
        return value


def serialize(results: list[Record]) -> list[dict]:
    data = [
        {
            "item_id": r.item_id,
            "result": {
                "prompt": r.result.prompt,
                "scores": [
                    {
                        "name": s.name,
                        "value": s.value,
                        "metrics": [metric.__name__ for metric in s.metrics],
                        "metadata": s.metadata,
                    }
                    for s in r.result.scores
                ],
            },
            "dataset_row": _serialize_value(r.dataset_row),
            "error": r.error,
            "timestamp": r.timestamp,
        }
        for r in results
    ]

    return data


def deserialize(data: list[dict]) -> list[Record]:
    results = []
    for r_data in data:
        scores = [
            Score(
                s["name"],
                s["value"],
                [registry[name] for name in s["metrics"]],
                s["metadata"],
            )
            for s in r_data["result"]["scores"]
        ]
        result = Result(prompt=r_data["result"]["prompt"], scores=scores)

        record = Record(
            result=result,
            item_id=r_data["item_id"],
            dataset_row=_deserialize_value(r_data["dataset_row"]),
            error=r_data["error"],
            timestamp=r_data["timestamp"],
        )
        results.append(record)

    return results


# Register the JSON backend
_registry.register("json", JSONStorage)
