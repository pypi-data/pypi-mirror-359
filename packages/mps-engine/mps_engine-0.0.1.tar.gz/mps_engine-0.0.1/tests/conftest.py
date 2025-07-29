import os
from pathlib import Path

import pytest

import mps
from mps.core.constants import (
    EXT_CONFIGURATION_DIR,
    EXT_CONTEXT_DIR,
    EXT_PREFERENCE_DIR,
    META_DIR,
    PATTERN_DIR,
    STRATEGY_DIR,
)


@pytest.fixture(autouse=True)
def reset_mps_config():
    """Reset MPS configuration before each test to avoid state leakage"""
    # Store original config if any
    original_config = getattr(mps, "_global_config", None)

    # Clear global config
    mps._global_config = None

    # Clear environment variables
    original_env = os.environ.get("MPS_BASE_DIR")
    if "MPS_BASE_DIR" in os.environ:
        del os.environ["MPS_BASE_DIR"]

    yield

    # Restore original state
    mps._global_config = original_config
    if original_env:
        os.environ["MPS_BASE_DIR"] = original_env


@pytest.fixture
def temp_mps_structure(tmp_path: Path) -> Path:
    """
    Create a complete MPS directory structure for testing.

    Returns the path to the MPS base directory.
    """
    mps_dir = tmp_path / "mps"

    # Create all standard directories
    (mps_dir / META_DIR).mkdir(parents=True)
    (mps_dir / PATTERN_DIR).mkdir(parents=True)
    (mps_dir / STRATEGY_DIR).mkdir(parents=True)

    # Create extension directories
    (mps_dir / EXT_CONTEXT_DIR).mkdir(parents=True)
    (mps_dir / EXT_PREFERENCE_DIR).mkdir(parents=True)
    (mps_dir / EXT_CONFIGURATION_DIR).mkdir(parents=True)

    return mps_dir


@pytest.fixture
def sample_pattern_content() -> str:
    """Sample pattern content with variables"""
    return """# IDENTITY and PURPOSE

You are an expert {{role}} who helps with {{task}}.

## GOAL

Your goal is to {{objective}}.

## OUTPUT INSTRUCTIONS

- Be {{tone}}
- Use {{format}} format
- Include {{examples}}

## INPUT

INPUT:"""


@pytest.fixture
def sample_patterns(temp_mps_structure: Path, sample_pattern_content: str) -> Path:
    """Create sample pattern files in the test structure"""
    patterns_dir = temp_mps_structure / PATTERN_DIR

    # Create translate pattern
    translate_dir = patterns_dir / "translate"
    translate_dir.mkdir()
    (translate_dir / "system.md").write_text("""# IDENTITY and PURPOSE

You are an expert translator for {{lang_code}}.

## OUTPUT INSTRUCTIONS

- Translate accurately to {{lang_code}}
- Keep original formatting

## INPUT

INPUT:""")

    # Create summarize pattern
    summarize_dir = patterns_dir / "summarize"
    summarize_dir.mkdir()
    (summarize_dir / "system.md").write_text(
        sample_pattern_content.replace("{{role}}", "summarizer").replace(
            "{{task}}", "creating summaries"
        )
    )

    return patterns_dir


@pytest.fixture
def sample_strategies(temp_mps_structure: Path) -> Path:
    """Create sample strategy files"""
    strategies_dir = temp_mps_structure / STRATEGY_DIR

    # Chain of Thought strategy
    (strategies_dir / "cot.json").write_text("""{
    "description": "Chain-of-Thought (CoT) Prompting",
    "prompt": "Think step by step to answer the question. Return the final answer in the required format."
}""")

    # Tree of Thought strategy
    (strategies_dir / "tot.json").write_text("""{
    "description": "Tree-of-Thought (ToT) Prompting",
    "prompt": "Generate multiple reasoning paths briefly and select the best one."
}""")

    return strategies_dir


@pytest.fixture
def sample_context(temp_mps_structure: Path) -> Path:
    """Create sample context files"""
    context_dir = temp_mps_structure / EXT_CONTEXT_DIR

    (context_dir / "biography.txt").write_text(
        "My name is John Doe and I am a software engineer."
    )
    (context_dir / "resume.md").write_text("""# John Doe

## Experience
- Software Engineer at Tech Corp
- 5 years Python experience
""")

    return context_dir


@pytest.fixture
def sample_preferences(temp_mps_structure: Path) -> Path:
    """Create sample preference files"""
    pref_dir = temp_mps_structure / EXT_PREFERENCE_DIR

    (pref_dir / "programming-language.txt").write_text(
        "Always use {{language}} in code examples."
    )
    (pref_dir / "tone.txt").write_text("Keep responses {{style}} and {{formality}}.")

    return pref_dir


@pytest.fixture
def sample_configurations(temp_mps_structure: Path) -> Path:
    """Create sample configuration files"""
    config_dir = temp_mps_structure / EXT_CONFIGURATION_DIR

    (config_dir / "creative.json").write_text("""{
    "temperature": 0.8,
    "max_tokens": 500,
    "message": "Be creative and expressive"
}""")

    (config_dir / "precise.json").write_text("""{
    "temperature": 0.1,
    "max_tokens": 100,
    "message": "Be precise and concise"
}""")

    return config_dir


@pytest.fixture
def complete_mps_setup(
    temp_mps_structure: Path,
    sample_patterns: Path,
    sample_strategies: Path,
    sample_context: Path,
    sample_preferences: Path,
    sample_configurations: Path,
) -> Path:
    """
    Create a complete MPS setup with all components.

    This is the main fixture most tests should use.
    """
    return temp_mps_structure


@pytest.fixture
def mps_with_pyproject(tmp_path: Path, complete_mps_setup: Path) -> tuple[Path, Path]:
    """
    Create MPS structure with pyproject.toml configuration.

    Returns (project_root, mps_dir)
    """
    project_root = tmp_path / "project"
    project_root.mkdir()

    # Move MPS to project
    mps_in_project = project_root / "mps"
    complete_mps_setup.rename(mps_in_project)

    # Create pyproject.toml
    (project_root / "pyproject.toml").write_text("""[tool.mps]
base_dir = "mps"

[project]
name = "test-project"
version = "0.1.0"
""")

    return project_root, mps_in_project


@pytest.fixture
def set_test_mps_dir(complete_mps_setup: Path):
    """Set MPS to use test directory for the duration of the test"""
    mps.set_mps_base_dir(complete_mps_setup)
    yield complete_mps_setup
    # Cleanup handled by reset_mps_config
