"""Layer 2: Configuration Manager."""

from functools import cached_property
from pathlib import Path

from mps._typing import PathLike
from mps.core.discovery import MpsDiscovery
from mps.core.errors import MpsConfigurationError, MpsDirectoryNotFoundError

from .constants import (
    EXT_CONFIGURATION_DIR,
    EXT_CONTEXT_DIR,
    EXT_PREFERENCE_DIR,
    META_DIR,
    PATTERN_DIR,
    STRATEGY_DIR,
)


class MpsConfig:
    """Central configuration manager for MPS.

    Handles all configuration sources with proper priority:
    1. Explicit base_dir parameter (highest priority)
    2. MPS_BASE_DIR environment variable
    3. Auto-discovery (pyproject.toml + filesystem search)
    4. Raises error if nothing found

    Example usage:
        ```python
        # Auto-discovery
        config = MpsConfig()

        # Explicit path
        config = MpsConfig(base_dir="/custom/mps")

        # Access directories
        patterns_dir = config.pattern_dir
        strategies_dir = config.strategy_dir
        ```
    """

    def __init__(self, base_dir: PathLike | None = None) -> None:
        """Initialize Mps configuration manager.

        Args:
            base_dir: explicit base directory. If None, uses discovery.

        """
        self._explicit_base_dir = Path(base_dir) if base_dir else None
        self._discovery = MpsDiscovery()

        # cached properties will be set on first acess
        self._base_dir_cache: Path | None = None

    def _resolve_base_dir(self) -> Path:
        raise NotImplementedError

    @cached_property
    def base_dir(self) -> Path:
        """Get the MPS base directory.

        Uses caching for performance - directory is resolved once per instance.

        Returns:
            Path to MPS base directory

        Raises:
            MpsDirectoryNotFoundError: if no MPS directory found
            MpsConfigurationError: if configuration is invalid
            MpsPermissionError: if directory exists but cannot be acessed

        """
        if self._base_dir_cache is not None:
            return self._base_dir_cache

        # priority 1: explicit base_dir parameter
        if self._explicit_base_dir:
            if not self._explicit_base_dir.exists():
                raise MpsDirectoryNotFoundError([str(self._explicit_base_dir)])

            if not self._explicit_base_dir.is_dir():
                raise MpsConfigurationError(
                    f"'{self._explicit_base_dir}' exists but is not a directory"
                )

            self._base_dir_cache = self._explicit_base_dir.resolve()
            return self._base_dir_cache

        # priority 2 & 3: environment variable + auto-discovery
        discovered_path = self._discovery.discover()

        if discovered_path is None:
            # typically should not happen as discovery raises its own errors
            raise MpsDirectoryNotFoundError

        self._base_dir_cache = discovered_path.resolve()
        return self._base_dir_cache

    @cached_property
    def meta_dir(self) -> Path:
        """Get the meta directory (base_dir/meta)."""
        return self.base_dir / META_DIR

    @cached_property
    def pattern_dir(self) -> Path:
        """Get the patterns directory (base_dir/pattern)."""
        return self.base_dir / PATTERN_DIR

    @cached_property
    def strategy_dir(self) -> Path:
        """Get the strategies directory (base_dir/strategy)."""
        return self.base_dir / STRATEGY_DIR

    class Extension:
        """MPS Extension components."""

        def __init__(self, base_dir: Path) -> None:
            """Initialize extension class."""
            self.base_dir = base_dir

        @cached_property
        def context_dir(self) -> Path:
            """Get the context directory (base_dir/prefix/context)."""
            return self.base_dir / EXT_CONTEXT_DIR

        @cached_property
        def preference_dir(self) -> Path:
            """Get the preference directory (base_dir/prefix/preference)."""
            return self.base_dir / EXT_PREFERENCE_DIR

        @cached_property
        def configuration_dir(self) -> Path:
            """Get the configuration directory (base_dir/prefix/configuration)."""
            return self.base_dir / EXT_CONFIGURATION_DIR

    @cached_property
    def ext(self) -> Extension:
        """Contain all MPS extension directories."""
        return self.Extension(base_dir=self.base_dir)

    def __repr__(self) -> str:
        """Represent MpsConfig as string for debugging."""
        try:
            base = self.base_dir
            return f"MpsConfig(base_dir='{base}')"
        except Exception as e:
            return f"MpsConfig(unresolved, error: {e})"
