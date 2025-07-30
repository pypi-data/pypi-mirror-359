from pathlib import Path


class PathProvider:
    def __init__(self, output_uri: Path, run_id: str):
        self.output_uri = output_uri
        self.run_id = run_id

    def get_run_output_uri(self, run_id: str) -> Path:
        return self.output_uri / run_id

    @property
    def run_output_uri(self) -> Path:
        return self.get_run_output_uri(run_id=self.run_id)

    @property
    def tracker_output_uri(self) -> Path:
        return self.run_output_uri / "tracker"

    def get_checkpoint_uri(self, run_id: str) -> Path:
        return self.get_run_output_uri(run_id=run_id) / "checkpoints"

    @property
    def checkpoint_uri(self) -> Path:
        return self.get_checkpoint_uri(run_id=self.run_id)
