"""Build the MPS Hierarchy."""

from functools import singledispatch
from re import Pattern
from typing import Any

from mps._typing import PathLike
from mps.models import Meta, Mps, MpsHierarchy
from mps.utils.decorators import future


@future()
@singledispatch
async def _build(location: PathLike | MpsHierarchy) -> Mps:
    raise NotImplementedError


@_build.register
async def _(location: MpsHierarchy) -> Mps: ...


@_build.register
async def _(location: PathLike) -> Mps: ...


@future(message="Forging a meta is planned for a future release.")
def metaforge(meta: Meta, forger: Any) -> Pattern:
    """Forge a meta into a pattern with the help of an LLM.

    Args:
        meta:
            the meta that is going to start the interactive session with LLM eventually
            forging a pattern miniature.
        forger: the LLM that will assist you forge the meta to a pattern.

    """
    raise NotImplementedError
