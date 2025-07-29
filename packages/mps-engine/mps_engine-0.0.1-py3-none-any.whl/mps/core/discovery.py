"""Layer 1: Discovery Engine."""

import os
import tomllib
from pathlib import Path

from mps.core.errors import MpsDirectoryNotFoundError


class MpsDiscovery:
    """Discovery algorithms of mps/ base directory in your project.

    Execution order:
        - Start from current working directory
        - Look for mps/ in current directory
        - If not found, move to parent directory
        - Repeat until found or reach filesystem root
        - Also check for pyproject.toml files during the walk
    """

    def discover(self, start_path: Path | None = None) -> Path | None:
        """Primary discovery method - tries all strategies in priority order.

        Priority:
            1. Environment variable (MPS_BASE_DIR)
            2. Filesystem Discovery (pyproject.toml + directory walking)

        Args:
            start_path: Where to start searching (defaults to current working directory)

        Returns:
            Path to valid MPS directory, or None if not found

        Raises:
            MpsConfigurationError: If configuration found but invalid

        """
        if start_path is None:
            start_path = Path.cwd()

        env_path = self._discover_from_env()
        if env_path:
            return env_path

        found_path, errors = self._discover_from_filesystem(start_path)
        if found_path:
            return found_path

        if errors:
            from .errors import MpsConfigurationError

            err_msg = "MPS configuration errors found:\n" + "\n".join(
                f"  - {err}" for err in errors
            )
            raise MpsConfigurationError(err_msg)

        # TODO(mghalix): add search_paths
        raise MpsDirectoryNotFoundError

    def _discover_from_filesystem(
        self, start_path: Path
    ) -> tuple[Path | None, list[str]]:
        """Walk up from the current directory looking for mps/."""
        current_path = start_path.resolve()
        all_errors = []

        while True:
            found_path, level_errors = self._check_level(current_path)

            if level_errors:
                all_errors.extend(level_errors)

            if found_path:
                return found_path, []

            parent = current_path.parent

            # stop if we've reached filesystem root
            if parent == current_path:
                break

            current_path = parent

        return None, all_errors

    def _discover_from_env(self) -> Path | None:
        """Read MPS_BASE_DIR environment variable."""
        env_path = os.environ.get("MPS_BASE_DIR")
        if not env_path:
            return None

        path = Path(env_path)
        if not self._is_valid_mps_directory(path):
            return None

        return path

    # helpers
    def _check_level(self, current_path: Path) -> tuple[Path | None, list[str]]:
        """Check current directory level from MPS configuration.

        Returns:
            (found_path, error_messages)
            - found_path: valid MPS directory path if found, None otherwise
            - error_messages: list of issues found

        """
        errors: list[str] = []

        # highest priority: check for the pyproject.toml first
        pyproject_path = current_path / "pyproject.toml"

        if pyproject_path.exists():
            base_dir_config = self._read_pyproject_mps_config(pyproject_path)

            if base_dir_config:
                configured_path = self._resolve_path_from_pyproject(
                    pyproject_path, base_dir_config
                )

                if self._is_valid_mps_directory(configured_path):
                    return configured_path, []

                if configured_path.exists() and not os.access(configured_path, os.R_OK):
                    from .errors import MpsPermissionError

                    raise MpsPermissionError(
                        path=str(configured_path), operation="read"
                    )

                fallback_path = current_path / "mps"

                err_msg: str
                if self._is_valid_mps_directory(fallback_path):
                    err_msg = (
                        f"mps/ directory not found at: '{configured_path}' (from pyproject.toml)."
                        f"Did you mean 'mps'? (found at {fallback_path})"
                    )
                else:
                    err_msg = f"mps/ directory not found at '{configured_path}' (from pyproject.toml)"

                errors.append(err_msg)

                return None, errors

        # no pyproject.toml config -- check for mps/ directory
        mps_path = current_path / "mps"
        if self._is_valid_mps_directory(mps_path):
            return mps_path, []

        # nothing found at this level
        return None, []

    def _is_valid_mps_directory(self, path: Path) -> bool:
        return path.exists() and path.is_dir()

    def _read_pyproject_mps_config(self, pyproject_path: Path) -> str | None:
        try:
            with pyproject_path.open("rb") as f:
                data = tomllib.load(f)
            return data.get("tool", {}).get("mps", {}).get("base_dir")
        except (OSError, tomllib.TOMLDecodeError):
            return None

    def _resolve_path_from_pyproject(
        self, pyproject_path: Path, base_dir_config: str
    ) -> Path:
        """Resolve base_dir relative to pyproject.toml location."""
        if (p := Path(base_dir_config)).is_absolute():
            return p

        pyproject_dir = pyproject_path.parent
        return pyproject_dir / base_dir_config
