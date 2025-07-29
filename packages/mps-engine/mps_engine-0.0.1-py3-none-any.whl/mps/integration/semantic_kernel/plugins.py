"""Semantic kernel plugins leveraging MPS."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from pydantic import BaseModel

from mps import strategy


def _apply(reasoning_kind: str, user_prompt: str) -> str:
    return strategy(reasoning_kind) + "\n" + user_prompt


class ReasoningItem(BaseModel):
    name: str
    description: str
    strategy_name: str
    _reasoning_applier_function: Callable[[str, str], str] = _apply


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


@dataclass
class ReasoningApplier:
    reasoning_items: Sequence[ReasoningItem]
    include_defaults: bool = True

    def __post_init__(self) -> None:
        if self.include_defaults:
            pass

    def _convert_defaults_to_functions(self) -> list[ReasoningItem]:
        items: list[ReasoningItem] = []
        for strategy_name in DEFAULT_STRATEGIES:
            st = strategy(strategy_name)
            items.append(
                ReasoningItem(
                    name=str(st.description),
                    description=st.prompt,
                    strategy_name=strategy_name,
                )
            )

        return items


class ReasoningPlugins:
    """Plugins for selecting the best fit strategy in a conditional manner."""

    # @kernel_function(name="chain_of_thought", description=_COT_DESC)
    # def apply_cot_reasoning(
    #     self, user_prompt: str, *, strategy_name: str = "cot"
    # ) -> str:
    #     """Apply chain of thought strategy to the LLM when responding."""
    #     pass

    # @kernel_function()
    # def apply_tot_reasoning(self): ...
    # @kernel_function()
    # def apply_aot_reasoning(): ...

    # def apply_custom_reason(
    #     self, name: str, description: str, strategy_name: str
    # ) -> kernel_function:
    #     return kernel_function(
    #         name=name,
    #         description=description,
    #     )(lambda: None)
