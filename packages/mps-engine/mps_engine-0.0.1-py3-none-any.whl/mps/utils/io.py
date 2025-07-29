"""Input/Output utilities."""

from dataclasses import dataclass
from pathlib import Path

from loguru import logger
from markitdown import MarkItDown
from pydantic import AnyUrl, BaseModel

from mps._typing import PathLike
from mps.models import Miniature, MiniatureKind, MiniatureName
from mps.utils.miniatures import miniature_exists
from mps.utils.uri import is_url


def _get_title(source: PathLike | AnyUrl) -> str:
    return Path(str(source)).stem


def _get_markdown(source: str) -> tuple[str | None, str]:
    md = MarkItDown()
    content = md.convert(source)
    markdown = content.markdown
    title = content.title
    return title, markdown


def persist_new(mininame: MiniatureName, content: str, minikind: MiniatureKind) -> Path:
    """Persist markdown.

    Args:
        mininame: The name of a miniature
        content: the miniature command content
        minikind: The kind of a miniature

    Return:
        The path of the newly created miniature

    """
    mini = Miniature.from_miniature_name(mininame=mininame, minikind=minikind)
    mini.cmdpath.parent.mkdir(parents=True, exist_ok=True)
    mini.cmdpath.write_text(content)
    return mini.cmdpath


def persist(
    mininame: MiniatureName,
    content: str,
    minikind: MiniatureKind,
) -> Path:
    """Ensure markdown persisted somewhere at homeland.

    Depending on the MiniatureKind, the markdown is placed.

    Args:
        mininame: the miniature name
        content: the miniature command
        minikind: the miniature kind

    Returns:
        A path of existing miniature or newly created one if it did not exist.

    """
    if miniature_exists(mininame=mininame, minikind=minikind):
        logger.debug(
            f"{minikind} miniature of name `{mininame}` already exists, skipping persistance."
        )
        return Miniature.from_miniature_name(mininame=mininame, minikind=minikind).home

    return persist_new(mininame, content, minikind)


class MD(BaseModel):
    """DTO object holding markdown information."""

    title: str
    content: str
    source_path: Path


@dataclass
class Markdown:
    """Load a source as markdown."""

    location: PathLike | AnyUrl

    # PERF: Optimize this
    def __call__(self, minikind: MiniatureKind) -> MD:
        """Get the markdown of any source url/local while ensuring persistance."""
        # TODO: write the link of insurance Philosophy

        source = str(self.location)
        if is_url(source):
            # TODO: search if it already exist before fetching by _get_markdown
            logger.debug(f"Found a url source: {source}")
            title, content = _get_markdown(source)
            mininame = MiniatureName(name=str(title))
            source = persist(mininame, content, minikind)
            # FIXME: Add logic if already persisted load as if it was path from miniature
            return MD(title=str(title), content=content, source_path=Path(source))

        # WRONG since its not always location path its usually name of miniature passed
        # if (s := Path(str(self.location))).exists():
        #     mini = Miniature.from_path(s)
        #     mininame = mini.mininame
        #     source = mini.cmdpath
        # else:
        #     mininame = MiniatureName(name=str(source))
        #     source = Miniature.from_miniature_name(mininame, minikind).cmdpath

        mininame = MiniatureName(name=str(source))
        source = Miniature.from_miniature_name(mininame, minikind).cmdpath
        title, content = _get_markdown(str(source))
        title = title or _get_title(str(source))
        return MD(title=title, content=content, source_path=source)
