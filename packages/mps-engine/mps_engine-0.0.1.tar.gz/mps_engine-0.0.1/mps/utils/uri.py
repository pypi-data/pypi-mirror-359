"""Path/Urls utilities."""

import contextlib

from pydantic import AnyUrl, ValidationError

from mps._typing import PathLike


def is_url(source: PathLike | AnyUrl) -> bool:
    """Check wheather a source is a url or not."""
    with contextlib.suppress(ValidationError):
        AnyUrl(str(source))
        return True

    return False


def is_path(source: PathLike | AnyUrl) -> bool:
    """Check wheather a source is a path or not."""
    return not is_url(source)


def main() -> None:
    """Test."""
    samples = [
        "https://docs.pydantic.dev/2.0/usage/types/urls/",
        "/home/mghali/Documents/tmp.txt",
        # "https://github.com/microsoft/markitdown/blob/main/README.md",  # remote md
    ]
    print(is_url(samples[-1]))


if __name__ == "__main__":
    main()
