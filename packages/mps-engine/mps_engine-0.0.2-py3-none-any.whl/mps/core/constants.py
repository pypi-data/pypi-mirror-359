"""MPS architecture constants and conventions."""

from pathlib import Path

# directory structure constants
EXTENSION_PREFIX = "ext"

# standard directory names
META_DIR = "meta"
PATTERN_DIR = "pattern"
STRATEGY_DIR = "strategy"
CONTEXT_DIR = "context"
PREFERENCE_DIR = "preference"
CONFIGURATION_DIR = "configuration"

# extension directory paths (relative to base)
EXT_CONTEXT_DIR = Path(EXTENSION_PREFIX) / CONTEXT_DIR
EXT_PREFERENCE_DIR = Path(EXTENSION_PREFIX) / PREFERENCE_DIR
EXT_CONFIGURATION_DIR = Path(EXTENSION_PREFIX) / CONFIGURATION_DIR
