"""
Check await command for asyncio CLI.
"""

import json
import sys
from pathlib import Path
from typing import Any, Optional

import click

from kairix_devtools.asyncio import (
    AsyncChecker,
    AsyncCheckResult,
    get_async_check_result_schema,
)


@click.command("check-await")
@click.argument(
    "path", type=click.Path(exists=True, path_type=Path), required=False
)
@click.option(
    "--exclude",
    multiple=True,
    help="Patterns to exclude from checking (can be used multiple times)",
)
@click.option(
    "--output-format",
    type=click.Choice(["human", "json"]),
    default="human",
    help="Output format",
)
@click.option(
    "--get-json-schema",
    is_flag=True,
    help="Output the JSON schema instead of running the check",
)
def check_await(
    path: Optional[Path],
    exclude: tuple[str, ...],
    output_format: str,
    get_json_schema: bool,
) -> None:
    """
    Check for async functions called without await or proper asyncio handling.

    PATH can be a file or directory to check. Not required when using --get-json-schema.
    """
    # Validate that --get-json-schema is not used with other options
    if get_json_schema:
        if path is not None or exclude or output_format != "human":
            click.echo(
                "Error: --get-json-schema cannot be used with other options or arguments",
                err=True,
            )
            sys.exit(1)

        # Output the JSON schema
        schema = get_async_check_result_schema()
        click.echo(json.dumps(schema, indent=2))
        return

    # PATH is required when not using --get-json-schema
    if path is None:
        click.echo(
            "Error: PATH argument is required when not using --get-json-schema",
            err=True,
        )
        sys.exit(1)
    checker = AsyncChecker()

    try:
        if path.is_file():
            result = checker.check_file(path)
        else:
            result = checker.check_directory(
                path, exclude_patterns=list(exclude)
            )

        # Convert to dict for JSON output using Pydantic
        result_dict = result.model_dump()

        if output_format == "json":
            click.echo(json.dumps(result_dict, indent=2))
        else:
            # Human-readable output
            _print_human_output(result, path)

        # Exit with error code if violations found
        if not result.passed:
            sys.exit(1)

    except Exception as e:
        if output_format == "json":
            error_result: dict[str, Any] = {
                "error": str(e),
                "total_files": 0,
                "violations": [],
                "passed": False,
                "violation_count": 0,
            }
            click.echo(json.dumps(error_result, indent=2))
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def _print_human_output(result: AsyncCheckResult, path: Path) -> None:
    """Print human-readable output formatted like Python stack traces."""
    if result.violations:
        # Header with error icon and message
        click.echo("❌ Async/await violations found!")
        click.echo()
        for violation in result.violations:
            # Error info first
            click.echo(
                f"AsyncViolationError: Function '{violation.function_name}' called without proper async handling"
            )
            click.echo(f"  Type: {violation.violation_type}")

            # Fix suggestion
            if violation.violation_type == "missing_await":
                click.echo("  💡 Fix: Add 'await' before the function call")
            else:
                click.echo(
                    "  💡 Fix: Wrap with 'asyncio.run()' or call from async context"
                )

            click.echo()  # Empty line

            # Icon and file location
            icon = (
                "🔄" if violation.violation_type == "missing_await" else "⚡"
            )
            click.echo(
                f'{icon} File "{violation.file_path}", line {violation.line_number}'
            )
            click.echo(f"    {violation.source_line}")

            # Show pointer covering the function call
            func_start = violation.source_line.find(violation.function_name)
            if func_start != -1:
                # Find the end of the function call (including parentheses)
                line = violation.source_line
                paren_start = line.find("(", func_start)
                if paren_start != -1:
                    # Find matching closing parenthesis
                    paren_count = 1
                    paren_end = paren_start + 1
                    while paren_end < len(line) and paren_count > 0:
                        if line[paren_end] == "(":
                            paren_count += 1
                        elif line[paren_end] == ")":
                            paren_count -= 1
                        paren_end += 1

                    # Cover the entire function call
                    func_call_length = paren_end - func_start
                    pointer_line = (
                        "    " + " " * func_start + "^" * func_call_length
                    )
                else:
                    # Just cover the function name
                    pointer_line = (
                        "    "
                        + " " * func_start
                        + "^" * len(violation.function_name)
                    )
            else:
                # Fallback to original position
                pointer_line = f"    {' ' * violation.column_number}^"
            click.echo(pointer_line)

            # Clear separator between errors
            click.echo()
            click.echo("─" * 80)
            click.echo()

        # Summary at the end with counters by type
        missing_await_count = sum(
            1 for v in result.violations if v.violation_type == "missing_await"
        )
        missing_asyncio_count = sum(
            1
            for v in result.violations
            if v.violation_type == "missing_asyncio"
        )

        click.echo(f"📁 Files checked: {result.total_files}")

        summary_parts: list[str] = []
        if missing_await_count > 0:
            summary_parts.append(f"🔄 missing_await: {missing_await_count}")
        if missing_asyncio_count > 0:
            summary_parts.append(
                f"⚡ missing_asyncio: {missing_asyncio_count}"
            )

        click.echo(f"Violations found: {', '.join(summary_parts)}")
        click.echo("❌ Check failed!")
    else:
        click.echo(f"📁 Files checked: {result.total_files}")
        click.echo(
            "✅ No violations found! All async functions are properly awaited. 🎉"
        )
        click.echo("🌟 Your async code looks great!")


__all__ = ["check_await"]
