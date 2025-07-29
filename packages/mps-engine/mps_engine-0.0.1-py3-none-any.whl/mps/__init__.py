"""MPS Engine Python SDK.

This package provides tools for working with MPS metas, patterns and strategies, along
with a rich set of extensions.

Note: AsyncIO support is planned for future releases and is currently unavailable.
"""

__version__ = "0.0.1"

from pathlib import Path

from . import ext
from .core.config import MpsConfig
from .core.errors import (
    MpsConfigurationError,
    MpsDirectoryNotFoundError,
    MpsError,
    MpsPermissionError,
    MpsValidationError,
)
from .fetcher import meta, pattern, strategizer, strategy
from .injector import inject
from .models import Miniature, Mps, MpsHierarchy

# global configuration instance (lazy-loaded)
_global_config: MpsConfig | None = None


def get_config() -> MpsConfig:
    global _global_config
    if _global_config is None:
        _global_config = MpsConfig()
    return _global_config


def set_mps_base_dir(path: str | Path) -> None:
    """Set the MPS base directory.

    Creates a new global configuration instance with the specified path.

    Args:
        path: Path to the MPS base directory

    """
    global _global_config
    _global_config = MpsConfig(base_dir=path)


def get_mps_base_dir() -> Path:
    """Get the current MPS base directory.

    Returns:
        Path to the MPS directory

    """
    return get_config().base_dir


__all__ = (
    "Miniature",
    "Mps",
    "MpsConfig",
    "MpsConfigurationError",
    "MpsDirectoryNotFoundError",
    "MpsError",
    "MpsHierarchy",
    "MpsPermissionError",
    "MpsValidationError",
    "ext",
    "get_mps_base_dir",
    "inject",
    "meta",
    "pattern",
    "set_mps_base_dir",
    "strategizer",
    "strategy",
    # "aio",
)
