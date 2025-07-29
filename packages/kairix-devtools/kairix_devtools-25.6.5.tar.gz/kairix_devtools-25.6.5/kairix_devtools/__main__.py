"""
Main CLI entry point for kairix devtools.
"""

import click

from .cli import asyncio_commands


@click.group()
@click.version_option()
def main() -> None:
    """Kairix development tools CLI."""


# Add command groups
main.add_command(asyncio_commands, name="asyncio")


if __name__ == "__main__":
    main()
