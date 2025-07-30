#!/usr/bin/env python3
import json
import os
from pathlib import Path

import typer
import yaml
from rich.console import Console

from nanoswea import package_dir
from nanoswea.agent import Agent, AgentConfig
from nanoswea.environment import LocalEnvironment, LocalEnvironmentConfig
from nanoswea.model import LitellmModel, ModelConfig

DEFAULT_CONFIG = Path(os.getenv("NSWEA_LOCAL_CONFIG_PATH", package_dir / "config" / "local.yaml"))
console = Console(highlight=False)
app = typer.Typer()


def get_multiline_problem_statement() -> str:
    """Get a multiline problem statement from the user."""
    console.print(
        "[bold yellow]What do you want to do?[/bold yellow] (press [bold red]Ctrl+D[/bold red] in a [red]new line[/red] to finish)"
    )
    lines = []
    while True:
        try:
            lines.append(console.input("[bold green]>[/bold green] "))
        except EOFError:
            break

    return "\n".join(lines).strip()

@app.command()
def main(
    config: str = typer.Option(str(DEFAULT_CONFIG), "--config", help="Path to config file"),
    model: str | None = typer.Option(
        None,
        "--model",
        help="Model to use",
    ),
    problem: str | None = typer.Option(None, "--problem", help="Problem statement", show_default=False),
    yolo: bool = typer.Option(False, "--yolo", help="Run without confirmation"),
) -> Agent:
    """Run nano-SWE-agent right here, right now."""
    _config = yaml.safe_load(Path(config).read_text())
    _model = _config.get("model", {}).get("model_name")
    if model:
        _model = model
    if not _model:
        _model = os.getenv("NSWEA_MODEL_NAME")
    if not _model:
        _model = console.input("[bold yellow]Enter your model name: [/bold yellow]")

    if not problem:
        problem = get_multiline_problem_statement()

    agent = Agent(
        AgentConfig(**(_config["agent"] | {"confirm_actions": not yolo})),
        LitellmModel(ModelConfig(**(_config.get("model", {}) | {"model_name": _model}))),
        LocalEnvironment(LocalEnvironmentConfig()),
        problem,
    )

    try:
        result = agent.run()
    except KeyboardInterrupt:
        console.print("\n[bold red]KeyboardInterrupt -- goodbye[/bold red]")
    else:
        Path("patch.txt").write_text(result)
    finally:
        Path("traj.json").write_text(
            json.dumps(agent.history, indent=2),
        )
        console.print(f"Total cost: [bold green]${agent.model.cost:.4f}[/bold green]")
        console.print(f"Total steps: [bold green]{agent.model.n_calls}[/bold green]")
    return agent


if __name__ == "__main__":
    app()
