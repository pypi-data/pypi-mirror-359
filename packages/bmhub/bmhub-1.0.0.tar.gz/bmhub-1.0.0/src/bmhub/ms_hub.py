import shutil
from fnmatch import fnmatch
from operator import attrgetter
from pathlib import Path

from modelscope.hub.snapshot_download import snapshot_download
from modelscope.utils.file_utils import get_model_cache_root

from bmhub.schema import ModelInfo


def get_ms_cache_dir() -> Path:
    cache_dir: Path = Path(get_model_cache_root()).expanduser().resolve()
    assert cache_dir.exists() and cache_dir.is_dir()
    return cache_dir


def _list_cached_ms_models() -> list[ModelInfo]:
    cache_dir: Path = Path(get_model_cache_root()).expanduser().resolve()
    if not cache_dir.exists() or cache_dir.is_file():
        raise ValueError(
            f"Cache directory not found: {cache_dir}. Please set `MODELSCOPE_CACHE` environment variable."  # noqa: E501
        )
    return _list_local_ms_models(local_dir=get_ms_cache_dir())


def _list_local_ms_models(*, local_dir: Path) -> list[ModelInfo]:
    models: list[ModelInfo] = []
    for organization_path in sorted(local_dir.iterdir()):
        if not organization_path.is_dir():
            continue
        if "___" in organization_path.name:
            continue
        for model_path in sorted(organization_path.iterdir()):
            if not model_path.is_dir():
                continue
            if "___" in model_path.name:
                continue
            if not (model_path / "config.json").exists():
                continue
            models.append(ModelInfo.from_local_path(model_path=model_path))
    return models


def list_ms_models(*, pattern: str | None, local_dir: Path | None) -> list[ModelInfo]:
    models: list[ModelInfo]
    if local_dir is None:
        models = _list_cached_ms_models()
    else:
        models = _list_local_ms_models(local_dir=local_dir)
    if pattern is not None:
        models = [model for model in models if fnmatch(name=model.id, pat=pattern)]
    return sorted(models, key=attrgetter("id"))


def download_ms_model(*, model_id: str, model_path: Path | None) -> None:
    if model_path is None:
        snapshot_download(repo_id=model_id)
        return
    snapshot_download(repo_id=model_id, local_dir=str(object=model_path))


def update_ms_model(*, model: ModelInfo) -> None:
    if model.path.is_relative_to(get_ms_cache_dir()):
        snapshot_download(repo_id=model.id)
        return
    snapshot_download(repo_id=model.id, local_dir=str(object=model.path))


def remove_ms_model(*, model: ModelInfo) -> None:
    if model.path.is_relative_to(get_ms_cache_dir()):
        if model.path.is_symlink():
            origin_path: Path = model.path.readlink()
            model.path.unlink()
            shutil.rmtree(origin_path)
        else:
            shutil.rmtree(model.path)
        return
    shutil.rmtree(model.path)
