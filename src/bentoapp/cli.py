import importlib
from pathlib import Path
from typing import Optional

import typer
import uvicorn

from .app import create_app

app = typer.Typer(help="bentoapp CLI")


@app.command()
def dev(
    module: str = "bentoapp.examples.demo.main:app",
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = True,
) -> None:
    """
    Run a bentoapp FastAPI server in development mode.
    """
    uvicorn.run(module, host=host, port=port, reload=reload, factory=False)


@app.command()
def new(name: str) -> None:
    """
    Scaffold a new project with a starter page.
    """
    target = Path(name)
    if target.exists():
        typer.echo(f"Directory {target} already exists.")
        raise typer.Exit(code=1)
    target.mkdir(parents=True)
    app_py = f"""from fastapi import Request
from bentoapp.app import create_app
from bentoapp import ui
from bentoapp.ui import page_route


@page_route("/")
async def home(request: Request):
    metrics = [
        ui.metric("Throughput (req/s)", "1,240", "+6.2%"),
        ui.metric("Latency p95 (ms)", "42", "-3.1%"),
        ui.metric("Active sessions", "312", "+12"),
    ]
    return ui.page(
        "Hello from {name}",
        ui.text("Starter page using bentoapp."),
        ui.grid(metrics, min_col=240),
    )


app = create_app(pages=[home], title="{name}")
"""
    (target / "app.py").write_text(app_py, encoding="utf-8")
    readme = f"# {name}\n\nRun with:\n\n```bash\nuvicorn app:app --reload\n```\n"
    (target / "README.md").write_text(readme, encoding="utf-8")
    (target / ".gitignore").write_text("__pycache__/\n.env\n*.pyc\n", encoding="utf-8")
    typer.echo(f"Created project scaffold at {target}\nNext: cd {name} && uvicorn app:app --reload")


@app.command("demo")
def run_demo(host: str = "127.0.0.1", port: int = 8000, reload: bool = True) -> None:
    """
    Run the bundled demo app.
    """
    uvicorn.run("bentoapp.examples.demo.main:app", host=host, port=port, reload=reload, factory=False)


@app.command("build-css")
def build_css() -> None:
    """
    Placeholder for CSS build (prebuilt CSS is shipped).
    """
    typer.echo("Prebuilt CSS is already included. Add a build step here if you customize styles.")
