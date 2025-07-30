import typer
from pathlib import Path
from mulch.workspace_factory import WorkspaceFactory

HELP_TEXT = "Workspace Manager CLI for scaffolding project workspaces."

app = typer.Typer(help=HELP_TEXT, no_args_is_help=True)

@app.callback()
def main():
    f"""
    {HELP_TEXT}
    """
    pass
@app.command()
def init(
    target_dir: Path = typer.Argument(
        Path.cwd(),
        help="Target project root. Defaults to current directory."
    ),
    name: str = typer.Option("default", "--name", "-n", help="Name of the workspace to create."),
    set_default: bool = typer.Option(True, "--set-default/--no-set-default", help="Write default-workspace.toml")
    ):
    """
    Initialize a new workspace inside the given target directory.
    """
    target_dir = target_dir.resolve()
    wm = WorkspaceFactory(base_path=target_dir, workspace_name=name)
    wm.check_and_create_dirs_from_scaffold()

    if set_default:
        wm.create_default_workspace_toml(target_dir / "workspaces", name)

    typer.echo(f"Workspace '{name}' initialized at {wm.workspace_dir}")

@app.command("render-workspace-manager")
def render_workspace_manager(
    target_dir: Path = typer.Argument(
        Path.cwd(),
        help="Target project root (containing scaffold.json). Defaults to current directory."
    ),
    ):
    """
    Render the workspace_manager.py file from Jinja2 template using scaffold.json.
    """
    wf = WorkspaceFactory(base_path=target_dir, workspace_name="placeholder")  # workspace_name not used for rendering
    wf.render_workspace_manager()
    ##project_name = Path.cwd()
    #typer.echo(f"workspace_manager.py created in src/{project_name}/")

if __name__ == "__main__":
    app()
