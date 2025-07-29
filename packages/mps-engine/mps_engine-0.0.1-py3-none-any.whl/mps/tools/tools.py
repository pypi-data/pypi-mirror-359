"""A tool to compile the mps miniatures."""

from typing import Annotated

from mps._typing import PathLike
from mps.models import Meta, MpsHierarchy, Pattern
from mps.utils.decorators import future


@future
def compile(
    mps: MpsHierarchy
    | Annotated[PathLike, "Base directory location of mps/"]
    | None = None,
) -> bool:
    """Compiles the mps hierarchy into python scripts.

    This offers the advantage of being able to import from directly plain buffer
    objects / strings without any io head.
    """
    if not mps:
        mps = MpsHierarchy()

    raise NotImplementedError


@future
def sync() -> bool:
    """Synchronize the lateset miniatures to the compiled script."""
    raise NotImplementedError


@future
def forge_meta(meta: Meta) -> Pattern:
    """Forge a meta into a pattern with the help of an LLM.

    Args:
        meta:
            the meta that is going to start the interactive session with LLM eventually
            forging a pattern miniature.
        forger: the LLM that will assist you forge the meta to a pattern.

    """
    raise NotImplementedError
