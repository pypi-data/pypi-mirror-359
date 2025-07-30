"""Custom dictionary utilities."""

from collections.abc import Callable
from typing import Any


class CallbackDict(dict):
    """Dictionary that invokes a callback when an item is set."""

    def __init__(
        self,
        callback: Callable[[Any, Any], None] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize the callback dictionary."""
        self.callback = callback
        super().__init__(*args, **kwargs)

    def __setitem__(self, key: Any, value: Any) -> None:
        """Set item with a callback hook."""
        super().__setitem__(key, value)
        if not self.callback:
            return
        self.callback(key, value)
