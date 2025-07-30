import shutil
from fnmatch import fnmatch
from operator import attrgetter
from pathlib import Path

from huggingface_hub import snapshot_download
from huggingface_hub.constants import HF_HUB_CACHE
from huggingface_hub.utils._cache_manager import (
    CachedRepoInfo,
    HFCacheInfo,
    scan_cache_dir,
)

from bmhub.schema import ModelInfo


def get_hf_cache_dir() -> Path:
    cache_dir: Path = Path(HF_HUB_CACHE).expanduser().resolve()
    assert cache_dir.exists() and cache_dir.is_dir()
    return cache_dir


def _list_cached_hf_models() -> list[ModelInfo]:
    return [
        ModelInfo(
            id=repo.repo_id,
            path=repo.repo_path,
            size_on_disk=repo.size_on_disk,
            num_files=repo.nb_files,
            last_accessed_timestamp=repo.last_accessed,
            last_modified_timestamp=repo.last_modified,
        )
        for repo in scan_cache_dir().repos
    ]


def _list_local_hf_models(*, local_dir: Path) -> list[ModelInfo]:
    models: list[ModelInfo] = []
    for organization_path in local_dir.iterdir():
        if not organization_path.is_dir():
            continue
        for model_path in organization_path.iterdir():
            if not model_path.is_dir():
                continue
            if not (model_path / "config.json").exists():
                continue
            models.append(ModelInfo.from_local_path(model_path=model_path))
    return models


def list_hf_models(*, pattern: str | None, local_dir: Path | None) -> list[ModelInfo]:
    models: list[ModelInfo]
    if local_dir is None:
        models = _list_cached_hf_models()
    else:
        models = _list_local_hf_models(local_dir=local_dir)
    if pattern is not None:
        models = [model for model in models if fnmatch(name=model.id, pat=pattern)]
    return sorted(models, key=attrgetter("id"))


def download_hf_model(*, model_id: str, model_path: Path | None) -> None:
    if model_path is None:
        snapshot_download(repo_id=model_id)
        return
    snapshot_download(repo_id=model_id, local_dir=model_path)


def update_hf_model(*, model: ModelInfo) -> None:
    if model.path.is_relative_to(get_hf_cache_dir()):
        snapshot_download(repo_id=model.id)
        return
    snapshot_download(repo_id=model.id, local_dir=model.path)


def remove_hf_model(*, model: ModelInfo) -> None:
    if model.path.is_relative_to(get_hf_cache_dir()):
        cache: HFCacheInfo = scan_cache_dir()
        repos: dict[str, CachedRepoInfo] = {repo.repo_id: repo for repo in cache.repos}
        assert model.id in repos
        revisions: list[str] = [
            revision.commit_hash for revision in repos[model.id].revisions
        ]
        cache.delete_revisions(*revisions).execute()
        return
    shutil.rmtree(model.path)
