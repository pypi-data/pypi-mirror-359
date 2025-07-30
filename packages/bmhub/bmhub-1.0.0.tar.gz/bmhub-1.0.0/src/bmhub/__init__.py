import shutil
from os import terminal_size
from pathlib import Path
from typing import Annotated, Any

import typer
from rich import box
from rich.console import Console
from rich.markup import escape
from rich.table import Table

from bmhub.backend import HubBackend
from bmhub.schema import ModelInfo
from bmhub.utils import format_size

app = typer.Typer(no_args_is_help=True, help="BigModel Hub CLI Toolkit")

BACKEND_ARGUMENT: Any = typer.Argument(help="Model hub backend", show_default=False)
MODEL_ID_ARGUMENT: Any = typer.Argument(help="Model ID", show_default=False)
MODEL_ID_PATTERN_ARGUMENT: Any = typer.Argument(
    help="Glob pattern to match model IDs", show_default=False
)
LOCAL_DIR_OPTION: Any = typer.Option(
    "--local-dir",
    help="The local model directory",
    show_default=False,
    exists=True,
    file_okay=False,
    dir_okay=True,
    resolve_path=True,
)
YES_OPTION: Any = typer.Option(
    "--yes", "-y", help="Confirm the action without prompting", show_default=False
)


def get_console() -> Console:
    size: terminal_size = shutil.get_terminal_size()
    return Console(width=size.columns)


def print_model_table(console: Console, models: list[ModelInfo]) -> None:
    table = Table(box=box.SIMPLE)
    table.add_column(header="MODEL ID", no_wrap=True)
    table.add_column(header="SIZE ON DISK", justify="right", no_wrap=True)
    table.add_column(header="NB FILES", justify="right", no_wrap=True)
    table.add_column(header="LAST ACCESSED", no_wrap=True)
    table.add_column(header="LAST MODIFIED", no_wrap=True)
    table.add_column(header="MODEL PATH", no_wrap=True)
    for model in models:
        table.add_row(
            model.id,
            model.size_on_disk_str,
            str(object=model.num_files),
            model.last_accessed_str,
            model.last_modified_str,
            str(object=model.path),
        )
    num_models: int = len(models)
    size_on_disk_str: str = format_size(
        size=sum(model.size_on_disk for model in models)
    )
    console.print(table)
    console.print(f"Scanned {num_models} repo(s) for a total of {size_on_disk_str}.")


@app.command(name="list")
def list_(
    backend: Annotated[HubBackend, BACKEND_ARGUMENT],
    pattern: Annotated[str | None, MODEL_ID_PATTERN_ARGUMENT] = None,
    *,
    local_dir: Annotated[Path | None, LOCAL_DIR_OPTION] = None,
) -> None:
    """List downloaded models."""
    models: list[ModelInfo] = backend.list_models(pattern=pattern, local_dir=local_dir)
    console: Console = get_console()
    print_model_table(console=console, models=models)


@app.command()
def download(
    backend: Annotated[HubBackend, BACKEND_ARGUMENT],
    model_id: Annotated[str, MODEL_ID_ARGUMENT],
    *,
    local_dir: Annotated[Path | None, LOCAL_DIR_OPTION] = None,
) -> None:
    """Download a model from the model hub."""
    model_path: Path | None = None if local_dir is None else local_dir / model_id
    model_path_str: str = "cache" if model_path is None else f"<{model_path}>"
    console: Console = get_console()
    console.print(f"Downloading <{model_id}> to {model_path_str}...")
    backend.download_model(model_id=model_id, model_path=model_path)


@app.command()
def update(
    backend: Annotated[HubBackend, BACKEND_ARGUMENT],
    pattern: Annotated[str | None, MODEL_ID_PATTERN_ARGUMENT] = None,
    *,
    local_dir: Annotated[Path | None, LOCAL_DIR_OPTION] = None,
    yes: Annotated[bool, YES_OPTION] = False,
) -> None:
    """Update downloaded models."""
    models: list[ModelInfo] = backend.list_models(pattern=pattern, local_dir=local_dir)
    count: int = len(models)
    console: Console = get_console()
    console.print(f"The following {count} models will be updated:")
    print_model_table(console=console, models=models)
    console.print(
        escape(markup=f"Do you want to update the {count} models? [y/N] "), end=""
    )
    if not yes and not console.input().lower() == "y":
        return
    for i, m in enumerate(iterable=models):
        console.print(
            escape(markup=f"[{i + 1}/{count}] Updating <{m.id}> in <{m.path}>...")
        )
        backend.update_model(model=m)


@app.command()
def remove(
    backend: Annotated[HubBackend, BACKEND_ARGUMENT],
    pattern: Annotated[str | None, MODEL_ID_PATTERN_ARGUMENT] = None,
    *,
    local_dir: Annotated[Path | None, LOCAL_DIR_OPTION] = None,
    yes: Annotated[bool, YES_OPTION] = False,
) -> None:
    """Remove downloaded models."""
    models: list[ModelInfo] = backend.list_models(pattern=pattern, local_dir=local_dir)
    count: int = len(models)
    console: Console = get_console()
    console.print(f"The following {count} models will be removed:")
    print_model_table(console=console, models=models)
    console.print(
        escape(markup=f"Do you want to remove the {count} models? [y/N] "), end=""
    )
    if not yes and not console.input().lower() == "y":
        return
    for i, m in enumerate(iterable=models):
        console.print(
            escape(markup=f"[{i + 1}/{count}] Removing <{m.id}> from <{m.path}>...")
        )
        backend.remove_model(model=m)
