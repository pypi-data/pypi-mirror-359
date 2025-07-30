"""Shared CLI functionality for the Agent CLI tools."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import typer

from .config_loader import load_config
from .utils import console

if TYPE_CHECKING:
    from logging import Handler


app = typer.Typer(
    name="agent-cli",
    help="A suite of AI-powered command-line tools for text correction, audio transcription, and voice assistance.",
    add_completion=True,
)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
) -> None:
    """A suite of AI-powered tools."""
    if ctx.invoked_subcommand is None:
        console.print("[bold red]No command specified.[/bold red]")
        console.print("[bold yellow]Running --help for your convenience.[/bold yellow]")
        console.print(ctx.get_help())
        raise typer.Exit


def set_config_defaults(ctx: typer.Context, config_file: str | None) -> None:
    """Set the default values for the CLI based on the config file."""
    config = load_config(config_file)
    wildcard_config = config.get("defaults", {})

    # If there's no subcommand, we can just set the default map for the main command
    if not ctx.invoked_subcommand:
        ctx.default_map = wildcard_config
        return

    command_config = config.get(ctx.invoked_subcommand, {})
    # Merge wildcard and command-specific configs, with command-specific taking precedence
    defaults = dict(wildcard_config, **command_config)

    # The recommended way to set defaults dynamically is to update the command's parameters
    if ctx.invoked_subcommand in ctx.command.commands:
        command = ctx.command.commands[ctx.invoked_subcommand]
        for param in command.params:
            if param.name in defaults:
                # This callback runs before parsing for the subcommand,
                # so we can set the default value for the parameter.
                param.default = defaults[param.name]


def setup_logging(log_level: str, log_file: str | None, *, quiet: bool) -> None:
    """Sets up logging based on parsed arguments."""
    handlers: list[Handler] = []
    if not quiet:
        handlers.append(logging.StreamHandler())
    if log_file:
        handlers.append(logging.FileHandler(log_file, mode="w"))

    logging.basicConfig(
        level=log_level.upper(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


# Import commands from other modules to register them
from .agents import autocorrect, interactive, speak, transcribe, voice_assistant  # noqa: E402, F401
