"""Loads MPS and populate miniatures."""

from functools import singledispatch
from pathlib import Path
from typing import Any

from loguru import logger
from pydantic import AnyUrl

from mps._typing import PathLike
from mps.models import (
    Configuration,
    Context,
    Meta,
    Miniature,
    MiniatureKind,
    Mps,
    MpsHierarchy,
    Pattern,
    Preference,
    Strategy,
)
from mps.utils.decorators import future
from mps.utils.io import Markdown

# async def read_file(abspath: PathLike) -> str:
#     async with aiofiles.open(abspath) as content:
#         return await content.read()


# def _ensure_locator(locator: Any | None, miniature: Miniatures):
#     if not locator:
#         locator = mps_settings.MPS_CONTEXT_DIR
#
#     locator = Path(locator)
#     dir = getattr(MPSLocatorDefaults, f"{miniature.value}_dir")
#     assert dir in locator.parts


@singledispatch
def read_miniature(from_: Miniature | PathLike | AnyUrl) -> str:
    """Read the miniature command (content).

    Args:
        from_: the miniature location to read from can be miniature object / path / url

    """
    raise NotImplementedError


@read_miniature.register
def _(from_: Miniature) -> str:
    mini = Miniature.model_validate(from_)
    logger.debug(mini.cmdpath)
    md = Markdown(mini.cmdpath)
    return md(mini.minikind).content


@read_miniature.register
def _(from_: PathLike) -> str:
    mini = Miniature.from_path(from_)
    return read_miniature(mini)


@read_miniature.register
def _(from_: AnyUrl) -> str:
    mini = Miniature.from_url(from_)
    return read_miniature(mini)


@future(
    message=(
        "Loading an mps/ directory into Mps component is planned for a future release."
    )
)
@singledispatch
def _load(location: MpsHierarchy | PathLike) -> Mps:
    """Engine generic loader.

    Args:
        location: the homeland of all miniatures mps_base_dir

    """
    raise NotImplementedError


@_load.register
def _(location: MpsHierarchy) -> Mps:
    if not location:
        location = MpsHierarchy()

    raise NotImplementedError


@_load.register
def _(location: PathLike) -> Mps:
    hierarchy = MpsHierarchy()

    if not location:
        location = str(hierarchy.base_dir)

    location = Path(location).absolute()
    print(location)

    # dirs = await aioos.listdir(location)
    # print(dirs)

    raise NotImplementedError


def _load_miniature(location: PathLike | AnyUrl, kind: MiniatureKind) -> dict[str, Any]:
    md = Markdown(location=location)
    return md(kind).model_dump()


def _load_context(location: PathLike | AnyUrl) -> Context:
    return Context(**_load_miniature(location, MiniatureKind.CONTEXT))


def _load_pattern(location: PathLike) -> Pattern:
    return Pattern(**_load_miniature(location, MiniatureKind.PATTERN))


def _load_meta(location: PathLike) -> Meta:
    return Meta(**_load_miniature(location, MiniatureKind.META))


def _load_strategy(location: PathLike) -> Strategy:
    return Strategy(**_load_miniature(location, MiniatureKind.STRATEGY))


def _load_preference(location: PathLike) -> Preference:
    return Preference(**_load_miniature(location, MiniatureKind.PREFERENCE))


def _load_configuration(location: PathLike) -> Configuration:
    return Configuration(**_load_miniature(location, MiniatureKind.CONFIGURATION))
