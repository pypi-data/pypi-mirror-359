from enum import Enum
from pathlib import Path

from bmhub.hf_hub import (
    download_hf_model,
    get_hf_cache_dir,
    list_hf_models,
    remove_hf_model,
    update_hf_model,
)
from bmhub.ms_hub import (
    download_ms_model,
    get_ms_cache_dir,
    list_ms_models,
    remove_ms_model,
    update_ms_model,
)
from bmhub.schema import ModelInfo


class HubBackend(Enum):
    HUGGING_FACE = "hf"
    MODEL_SCOPE = "ms"

    def get_cache_dir(self) -> Path:
        match self:
            case HubBackend.HUGGING_FACE:
                return get_hf_cache_dir()
            case HubBackend.MODEL_SCOPE:
                return get_ms_cache_dir()

    def list_models(
        self, *, pattern: str | None, local_dir: Path | None
    ) -> list[ModelInfo]:
        match self:
            case HubBackend.HUGGING_FACE:
                return list_hf_models(pattern=pattern, local_dir=local_dir)
            case HubBackend.MODEL_SCOPE:
                return list_ms_models(pattern=pattern, local_dir=local_dir)

    def download_model(self, *, model_id: str, model_path: Path | None) -> None:
        match self:
            case HubBackend.HUGGING_FACE:
                return download_hf_model(model_id=model_id, model_path=model_path)
            case HubBackend.MODEL_SCOPE:
                return download_ms_model(model_id=model_id, model_path=model_path)

    def update_model(self, *, model: ModelInfo) -> None:
        match self:
            case HubBackend.HUGGING_FACE:
                return update_hf_model(model=model)
            case HubBackend.MODEL_SCOPE:
                return update_ms_model(model=model)

    def remove_model(self, *, model: ModelInfo) -> None:
        match self:
            case HubBackend.HUGGING_FACE:
                return remove_hf_model(model=model)
            case HubBackend.MODEL_SCOPE:
                return remove_ms_model(model=model)
