from typing import Any, Literal

import wandb

from ksuit.core.trackers import Tracker


class WandbTracker(Tracker):
    def __init__(
        self,
        entity: str,
        project: str,
        mode: Literal["online", "offline", "disabled"] | None = None,
        wandb_init_kwargs: dict[str, Any] | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.entity = entity
        self.project = project
        self.mode = mode
        self.wandb_init_kwargs = wandb_init_kwargs

    def _initialize(self, config: dict[str, Any], run_id: str) -> None:
        super()._initialize(config=config, run_id=run_id)
        wandb.login()
        wandb_init_kwargs = self.wandb_init_kwargs or {}
        tags = ["new"] + wandb_init_kwargs.get("tags", [])
        wandb.init(
            entity=self.entity,
            project=self.project,
            name=config.get("name"),
            dir=self.path_provider.tracker_output_uri,
            save_code=False,
            config=config,
            mode=self.mode,
            id=run_id,
            tags=tags,
            **wandb_init_kwargs,
        )

    def _flush(self) -> None:
        wandb.log(self._cache)

    def _set_summary(self, key: str, value: int | float) -> None:
        super()._set_summary(key=key, value=value)
        wandb.run.summary[key] = value

    def _cleanup(self) -> None:
        wandb.finish()
