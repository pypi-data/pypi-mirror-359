"""MPS errors."""

from typing import Literal


class MpsError(Exception):
    """Base class for all MPS errors."""


class MpsConfigurationError(MpsError):
    """Raised when MPS configuration is found but invalid."""

    def __init__(self, message: str, suggestions: list[str] | None = None) -> None:
        """Initialize mps configuration error."""
        super().__init__(message)
        self.suggestions = suggestions or []

    def __str__(self) -> str:
        """Represent the error in string."""
        msg = super().__str__()
        if not self.suggestions:
            return msg

        suggestions_text = "\n".join(
            f"  💡 {suggestion}" for suggestion in self.suggestions
        )
        msg += f"\n\nSuggesstions:\n{suggestions_text}"
        return msg


class MpsDirectoryNotFoundError(MpsError):
    """Raised when no MPS directory can be found."""

    def __init__(self, search_paths: list[str] | None = None) -> None:
        """Initialize MPS directory not found error."""
        self.search_paths = search_paths or []

        message: str
        if search_paths:
            paths_text = "\n".join(f"  - {path}" for path in search_paths)
            message = f"No MPS directory found. Searched in:\n{paths_text}"
        else:
            message = "No MPS directory found."

        super().__init__(message)


class MpsPermissionError(MpsError):
    """Raised when MPS directory exists but cannot be accessed."""

    def __init__(
        self, path: str, operation: Literal["access", "read", "write"] = "access"
    ) -> None:
        """Initialize MPS permission error."""
        self.path = path
        self.operation = operation
        message = f"Permission denied: cannot {operation} MPS directory at '{path}'"
        super().__init__(message)


class MpsValidationError(MpsError):
    """Raised when MPS directory structure is invalid."""

    def __init__(self, path: str, issues: list[str]) -> None:
        """Initialize MPS validation error."""
        self.path = path
        self.issues = issues

        issues_text = "\n".join(f"  ❌ {issue}" for issue in issues)
        message = f"Invalid MPS directory structure at '{path}':\n{issues_text}"

        super().__init__(message)


class MpsWrongHierarchyError(MpsError):
    """Raised when the local hierarchy structure of mps is incorrect."""


class MiniatureNotFoundError(MpsError):
    """Raised when the engine dont find a queried miniature in its home."""


class UnknownMiniatureError(MpsError):
    """Raised when a miniature requested with an unsupported miniature kind."""
