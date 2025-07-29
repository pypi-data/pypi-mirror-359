"""Command Line Interface of MPS."""

from collections.abc import Callable

cli_main: Callable | None

try:
    from mps_cli.cli import main as cli_main
except ImportError:
    cli_main = None


def main() -> None:
    """MPS Engine entry point."""
    if not cli_main:
        message = 'To use mps command, please install "mps[standard]"\n\n\t'
        'pip install "mps[standard]"\n'
        print(message)
        raise RuntimeError(message)
    cli_main()
