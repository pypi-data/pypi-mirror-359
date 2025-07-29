"""Miniature utilities."""

import os
from pathlib import Path

from loguru import logger

from mps._typing import PathLike
from mps.core.errors import MiniatureNotFoundError, UnknownMiniatureError
from mps.models import Miniature, MiniatureKind, MiniatureName


def _firstmatch(
    miniature_name: str,
    miniature_kind: MiniatureKind = MiniatureKind.CONTEXT,
    mps_base_dir: PathLike | None = None,
) -> tuple[str, str]:
    """Locate a context miniature by first match search.

    Args:
        miniature_name: the name of the miniature
        miniature_kind: the type of the minature
        mps_base_dir:
            the home of all minatures usually located at `path/to/project/mps/`
    Raises:
        MiniatureNotFoundError: if miniature with {miniature_name} was not found

    Returns:
        pair of title and suffix

    Note:
        This is especially required for miniatures of kind context as they have no known
        extension, therefore a first match algorithm is needed.

    """
    if not mps_base_dir:
        from mps import get_config

        mps_base_dir = get_config().base_dir

    mps_base_dir = Path(mps_base_dir)

    miniature_name = miniature_name.lower()

    # TODO: optimize the search algorithm
    # * make this more modular (ext) move somewhere, only miniatures with no parent
    # * need this _firstmatch() function since it's not directory based
    from mps.core.constants import EXTENSION_PREFIX

    search_dir = mps_base_dir / EXTENSION_PREFIX / miniature_kind

    try:
        ls = os.listdir(search_dir)
    except FileNotFoundError as e:
        raise MiniatureNotFoundError(
            f"Directory not found: {search_dir} for miniature kind: {miniature_kind}"
        ) from e

    for f in ls:
        curr_name = Path(f).stem
        if curr_name != miniature_name:
            continue

        file = Path(f)
        return file.stem, file.suffix

    raise MiniatureNotFoundError(
        f"No match found for miniature: {miniature_kind} with name: {miniature_name}"
    )


def get_miniature_cmdname(minikind: MiniatureKind, mininame: MiniatureName) -> str:
    """Command name of a miniature.

    Args:
        minikind: The kind of the miniature
        mininame: The name of the miniature


    Returns:
        The title of a miniature's command.

        e.g.,
        "teacher-assistant-generator.md" (meta)
        | "system.md" (pattern)
        | "cot.json" (strategy)
        | "my-resume.md"  (context)

    Raises:
        UnknownMiniatureError:
            If the minikind is not a part of MiniatureKind enums

    """
    suffix = ".md"
    title = ""
    match minikind:
        case x if x in MiniatureKind.extensions():
            title, suffix = _firstmatch(
                str(mininame),
                minikind,
            )
        case MiniatureKind.PATTERN | MiniatureKind.META:
            title = "system"
        case MiniatureKind.STRATEGY:
            suffix = ".json"
            title = str(mininame).lower()
        case _:
            raise UnknownMiniatureError

    return title + suffix


def miniature_exists(mininame: MiniatureName, minikind: MiniatureKind) -> bool:
    """Check whether or not a miniature exist.

    Args:
        mininame: the name of a miniature
        minikind: the kind of a miniature
        homeland: the base directory where all minature kinds live

    Returns:
        true if the miniature exist, false otherwise

    """
    minipath = Miniature.from_miniature_name(
        mininame=mininame, minikind=minikind
    ).cmdpath
    logger.debug(minipath)
    return minipath.exists()


def get_miniature_kind_from_path(path: PathLike) -> MiniatureKind:
    """Get a miniature kind from path.

    Args:
        path: the path in which the search algorithm look for the miniature in.

    Raises:
        MiniatureNotFoundError: if the path provided does not follow the MPS structure

    """
    parts = Path(path).parts

    allowed_minihomes = MiniatureKind.iterable()
    while parts[-1] not in allowed_minihomes:
        parts = parts[:-1]
        if not parts:
            raise MiniatureNotFoundError(
                f"Miniature with path: {path} was not found. make sure it was located "
                f"inside any of the following miniature homes {allowed_minihomes}"
            )

    return MiniatureKind(parts[-1])


def get_miniature_name_from_path(path: PathLike) -> MiniatureName:
    """Get a name of a minature from path.

    Args:
        path: the path of a miniature

    Raises:
        UnknownMiniatureError:
            If the minikind is not a part of MiniatureKind enums
    Note:
        this does not actually check for the existence of the miniature it just
        validates the path pattern.

    """
    path = Path(path)

    try:
        minikind = get_miniature_kind_from_path(path)
    except MiniatureNotFoundError as e:
        logger.error(e)
        raise

    parts = path.parts

    name: str
    match minikind:
        case m if m == MiniatureKind.STRATEGY or m in MiniatureKind.extensions():
            name = Path(parts[-1]).stem
        case MiniatureKind.META | MiniatureKind.PATTERN:
            idx = -1
            vals = (MiniatureKind.META.value, MiniatureKind.PATTERN.value)
            while parts[idx] not in vals:
                idx -= 1
            name = parts[idx + 1]
        case _:
            raise UnknownMiniatureError

    return MiniatureName(name=name)
