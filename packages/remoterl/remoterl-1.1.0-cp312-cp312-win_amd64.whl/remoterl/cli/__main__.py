#!/usr/bin/env python3
"""remoterl.cli
================
Cleaned-up CLI with the following fixes applied:

1️⃣ **Config consistency** - The CLI now documents the use of *JSON* (not YAML)
   for the persistent config file `config.json` living under
   `~/.config/remoterl/` (unless overridden by `REMOTERL_CONFIG_PATH`).
2️⃣ **Register retry loop** - Counts attempts correctly and aborts after three
   invalid entries.
3️⃣ **Invalid backend aborts** - `train` exits immediately with code 1 when the
   backend name is unrecognised.
5️⃣ **Extra args passthrough** - Typer’s native `ctx.args` is forwarded to the
   backend instead of the custom `parse_extra` helper.
6️⃣ **Uniform UX helpers** - `success()`, `warn()`, `fail()` colour helpers plus
   consistent non-zero exit codes on error paths.

The rest of the logic is unchanged.
"""
from __future__ import annotations

import os
import sys
from typing import List
import webbrowser
import typer

# ----------------------------------------------------------------------------
# Config helpers import (shared with existing module)
# ----------------------------------------------------------------------------
from ..config import load_config, save_config, resolve_api_key, validate_api_key, DEFAULT_CONFIG_PATH   
DASHBOARD_URL = "https://remoterl.com/user/dashboard"

# ----------------------------------------------------------------------------
# Typer application
# ----------------------------------------------------------------------------
app = typer.Typer(
    add_completion=False,
    help="RemoteRL - spin up remote trainers & simulators from one CLI.",
)

# ----------------------------------------------------------------------------
# Root – show help & --version flag
# ----------------------------------------------------------------------------
from importlib.metadata import version as _pkg_version, PackageNotFoundError

def _resolve_version() -> str:
    try:
        return _pkg_version("remoterl")
    except PackageNotFoundError:
        return "unknown"

@app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        is_flag=True,
        help="Show CLI version and exit.",
    ),
) -> None:
    """Root command - prints help when no sub-command is given."""
    if version:
        typer.echo(_resolve_version())
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()

# ----------------------------------------------------------------------------
# Style helpers – keep colouring uniform across commands
# ----------------------------------------------------------------------------

def _style(msg: str, fg: typer.colors.Color) -> str:  # internal
    return typer.style(msg, fg=fg)

def success(msg: str) -> None:
    typer.echo(_style(msg, typer.colors.GREEN))

def warn(msg: str) -> None:
    typer.echo(_style(msg, typer.colors.YELLOW))

def fail(msg: str) -> None:
    typer.echo(_style(msg, typer.colors.RED), err=True)


# ----------------------------------------------------------------------------
# Misc helpers
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# register – save API key
# ----------------------------------------------------------------------------
@app.command(help="Save (or update) your RemoteRL API key in the config file.")
def register(
    open_browser: bool = typer.Option(
        True,
        "--open-browser/--no-open-browser",
        "-o",
        help="Open your dashboard in a browser so you can copy the key quickly.",
    ),
) -> None:
    cfg = load_config()

    # Existing key?
    if (cur := cfg.get("api_key")):
        warn(f"Current API key: {cur[:8]}... (resolved)")

    # Browser helper
    if open_browser and hasattr(sys, "stdout"):
        warn(f"Opening {DASHBOARD_URL} ...")
        try:
            webbrowser.open(DASHBOARD_URL)
        except Exception:
            pass  # silent – browser may not be available

    # Prompt user (with retries)
    attempts = 0
    api_key = typer.prompt("Please enter your RemoteRL API key")
    while not validate_api_key(api_key):
        attempts += 1
        if attempts >= 3:
            fail("Too many invalid attempts – aborting.")
            raise typer.Exit(code=1)
        api_key = typer.prompt("Please enter a *valid* RemoteRL API key")

    # Persist
    cfg["api_key"] = api_key
    save_config(cfg)
    success(
        f"API key saved to {DEFAULT_CONFIG_PATH}."
    )

# ----------------------------------------------------------------------------
# simulate – unchanged except for cohesive error handling
# ----------------------------------------------------------------------------
@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def simulate(ctx: typer.Context) -> None:
    """
    Start a simulator and wait for remote training jobs to connect via the
    RemoteRL server.\n
    You can point any Gym-compatible trainer at the server URL once it is
    running.\n\n

    Examples\n
    --------\n
    remoterl train\n
    remoterl train sb3 --algo ppo\n
    remoterl train rllib --batch-size 64\n
    """
    from ..pipelines.simulate import simulate as remote_simulate  # type: ignore

    api_key = resolve_api_key()
    if not api_key:
        fail("No RemoteRL API key found. Run `remoterl register` first or set REMOTERL_API_KEY.")
        raise typer.Exit(code=1)

    os.environ["REMOTERL_API_KEY"] = api_key
    remote_simulate(list(ctx.args))

# ----------------------------------------------------------------------------
# train – backend selection + passthrough args
# ----------------------------------------------------------------------------
BACKENDS = {
    "gym",
    "gymnasium",  # alias – normalised to "gym"
    "ray",
    "rllib",
    "sb3",
    "stable_baselines3",
}

@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def train(
    ctx: typer.Context,
    backend: str = typer.Argument(
        "gym",
        metavar="BACKEND",
        case_sensitive=False,
        help=f"Training backend: {', '.join(sorted(BACKENDS))}",
    ),
) -> None:
    """
    Run a training job with your chosen backend\n
    (gym | rllib | stable-baselines3).\n
    You can pass backend-specific arguments after the '--' separator.\n\n    
    
    Examples\n
    --------\n
    remoterl train\n
    remoterl train sb3 --algo ppo\n
    remoterl train rllib --batch-size 64\n
    """    
    from ..pipelines.train import train as _train  # type: ignore

    api_key = resolve_api_key()
    if not api_key:
        fail("No RemoteRL API key found. Run `remoterl register` first or set REMOTERL_API_KEY.")
        raise typer.Exit(code=1)

    os.environ["REMOTERL_API_KEY"] = api_key

    selected = backend.lower().replace("-", "_")
    if selected not in BACKENDS:
        fail(f"Invalid backend '{selected}'. Valid choices: {', '.join(sorted(BACKENDS))}.")
        raise typer.Exit(code=1)

    # Hand raw tail straight through (Typer already ignored unknown options)
    extra_args: List[str] = list(ctx.args)

    # Forward to the real trainer – signature: train(backend: str, args: List[str])
    _train(selected, extra_args)  # type: ignore[arg-type]

# ----------------------------------------------------------------------------
# Entrypoint for console-script
# ----------------------------------------------------------------------------

def main() -> None:  # pragma: no cover – thin wrapper for console-scripts
    DEFAULT_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    app()

if __name__ == "__main__":
    main()
