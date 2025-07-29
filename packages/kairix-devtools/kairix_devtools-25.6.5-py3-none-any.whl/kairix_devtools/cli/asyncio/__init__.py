"""
Asyncio CLI commands module.
"""

import click

from .check_await import check_await


@click.group()
def asyncio_commands() -> None:
    """Asyncio development tools."""


# Register commands
asyncio_commands.add_command(check_await)


__all__ = ["asyncio_commands"]
