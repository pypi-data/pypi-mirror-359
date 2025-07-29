"""Reasoning Plugins for Semantic Kernel.

A reasoning plugin is applied at the System Instruction level.
"""

from functools import partial

from mps import strategy
from mps.models import Pattern, Strategy


def _apply(system_instruction: str | Pattern, strategy: str | Strategy) -> str:
    return f"{system_instruction}\n{strategy}"


DEFAULT_STRATEGIES = (
    "aot",
    "cod",
    "cot",
    "ltm",
    "reflexion",
    "self-consistent",
    "self-refine",
    "standard",
    "tot",
)

for name in DEFAULT_STRATEGIES:
    func_name = f"apply_{name}"
    func = partial(_apply, strategy=strategy(name))
