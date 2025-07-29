"""Semantic Kernel Integration with MPS."""

from collections.abc import Callable, Sequence
from functools import partial

try:
    from semantic_kernel.agents import ChatCompletionAgent
except ImportError as e:
    raise ImportError(
        "Failed to import 'semantic_kernel' ensure you have run "
        "'pip mps-engine[semantic-kernel]' for using the semantic-kernel integration."
    ) from e


def _base_sk_wrapper(
    func: Callable | None = None,
    *,
    name: str,
    miniature: Callable,
) -> Callable:
    """kernel_function decorator."""
    if func is None:
        return partial(_base_sk_wrapper, name=name, miniature=miniature)

    more_context = miniature(name)
    kernel_attr_desc_name = "__kernel_function_description__"

    original_desc = ""
    if hasattr(func, kernel_attr_desc_name):
        original_desc = getattr(func, kernel_attr_desc_name)

    combined_desc = f"{more_context.content}{original_desc}"

    setattr(func, kernel_attr_desc_name, combined_desc)

    return func


# context = partial(_base_sk_wrapper, miniature=_contexter)
# preference = partial(_base_sk_wrapper, miniature=_preference_setter)


class _AgentPreference:
    def __init__(self, preference_template: str) -> None:
        """Initialize agent preference based on a template."""
        self.preference_template = preference_template

    def __call__(self, agents: Sequence[ChatCompletionAgent]) -> None:
        for agent in agents:
            if not agent.instructions:
                agent.instructions = ""

            agent.instructions += f"\n\n{self.preference_template}"


def set_agent_preference(name: str, *agents: ChatCompletionAgent) -> bool:
    """Apply a preference miniature for all passed agents."""
    from mps.ext import preference

    try:
        _AgentPreference(str(preference(name)))(agents)
    except Exception:
        return False

    return True
