"""Fetch a miniature."""

from mps.injector import inject
from mps.loader import (
    _load_configuration,
    _load_context,
    _load_meta,
    _load_pattern,
    _load_preference,
    _load_strategy,
)
from mps.models import (
    Configuration,
    Context,
    Homeless,
    Meta,
    Miniature,
    Pattern,
    Preference,
    Strategy,
)
from mps.utils.decorators import future


def meta(name: str) -> Meta:
    """Load meta by meta miniature name."""
    return _load_meta(name)


def context(name: str) -> Context:
    """Load context by context miniature name."""
    return _load_context(name)


def pattern(name: str) -> Pattern:
    """Load pattern by pattern miniature name."""
    return _load_pattern(name)


def strategy(name: str) -> Strategy:
    """Load strategy by strategy miniature name."""
    return _load_strategy(name)


def preference(name: str) -> Preference:
    """Load preference by preference name."""
    return _load_preference(name)


def configuration(name: str) -> Configuration:
    """Load configuration by configuration name."""
    return _load_configuration(name)


def strategizer(
    *,
    strategy: Strategy,
    pattern: Pattern | None = None,
    context: Context | None = None,
) -> str:
    """Combine strategy, context, and pattern miniatures to create a powerful prompt."""
    s = f"# How you should respond\n{strategy}"
    c = f"# Here is what you should remember\n{context!s}" if context else ""
    p = f"# {pattern!s}" if pattern else ""
    return "\n\n".join((s, c, p))


@future
def shelter(miniature: Homeless) -> Miniature:
    """Shelter a homeless miniature.

    Saving it to its designated miniature path.
    + Saving metadata of its source.
    """
    raise NotImplementedError


if __name__ == "__main__":
    # print(strategy("cot"))
    # print(context("my-resume"))
    # print(context("my-resume") | pattern("summarize"))
    print(
        strategizer(
            strategy=strategy("cot"),
            pattern=inject(pattern("translate"), lang_code="ar"),
            # context=context("my-resume"),
        )
    )
