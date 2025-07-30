import os
from pathlib import Path
from textwrap import dedent

import pytest

from mps.core.discovery import MpsDiscovery
from mps.core.errors import MpsConfigurationError, MpsDirectoryNotFoundError


class TestMpsDiscovery:
    """Comprehensive tests for MPS discovery engine"""

    def test_discover_from_environment_variable(self, complete_mps_setup: Path):
        """Test discovery via MPS_BASE_DIR environment variable"""
        # Set environment variable
        os.environ["MPS_BASE_DIR"] = str(complete_mps_setup)

        try:
            discovery = MpsDiscovery()
            found = discovery.discover()
            assert found == complete_mps_setup
        finally:
            # Cleanup
            if "MPS_BASE_DIR" in os.environ:
                del os.environ["MPS_BASE_DIR"]

    def test_discover_from_pyproject_toml(self, mps_with_pyproject: tuple[Path, Path]):
        """Test discovery via pyproject.toml configuration"""
        project_root, mps_dir = mps_with_pyproject

        discovery = MpsDiscovery()
        found = discovery.discover(start_path=project_root)

        assert found == mps_dir

    def test_discover_from_filesystem_walk(
        self, tmp_path: Path, complete_mps_setup: Path
    ):
        """Test discovery by walking up filesystem"""
        # Create nested directory structure
        deep_dir = tmp_path / "project" / "src" / "deep"
        deep_dir.mkdir(parents=True)

        # Move MPS to project root
        mps_in_project = tmp_path / "project" / "mps"
        complete_mps_setup.rename(mps_in_project)

        # Start discovery from deep directory
        discovery = MpsDiscovery()
        found = discovery.discover(start_path=deep_dir)

        assert found == mps_in_project

    def test_pyproject_with_absolute_path(
        self, tmp_path: Path, complete_mps_setup: Path
    ):
        """Test pyproject.toml with absolute path"""
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Create pyproject.toml with absolute path
        (project_root / "pyproject.toml").write_text(f"""[tool.mps]
base_dir = "{complete_mps_setup}"
""")

        discovery = MpsDiscovery()
        found = discovery.discover(start_path=project_root)

        assert found == complete_mps_setup

    def test_pyproject_with_relative_path(self, mps_with_pyproject: tuple[Path, Path]):
        """Test pyproject.toml with relative path"""
        project_root, mps_dir = mps_with_pyproject

        discovery = MpsDiscovery()
        found = discovery.discover(start_path=project_root)

        assert found == mps_dir
        # Verify it's resolved relative to pyproject.toml location
        assert found.parent == project_root

    def test_invalid_pyproject_config_with_suggestion(
        self, tmp_path: Path, complete_mps_setup: Path
    ):
        """Test helpful error when pyproject.toml points to wrong path"""
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Move MPS to project with correct name
        mps_correct = project_root / "mps"
        complete_mps_setup.rename(mps_correct)

        # Create pyproject.toml pointing to wrong path
        (project_root / "pyproject.toml").write_text("""[tool.mps]
base_dir = "wrong-path"
""")

        discovery = MpsDiscovery()

        with pytest.raises(MpsConfigurationError) as exc_info:
            discovery.discover(start_path=project_root)

        error_msg = str(exc_info.value)
        assert "wrong-path" in error_msg
        assert "Did you mean 'mps'?" in error_msg

    def test_malformed_pyproject_toml(self, tmp_path: Path, complete_mps_setup: Path):
        """Test graceful handling of malformed pyproject.toml"""
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Move MPS to project
        mps_in_project = project_root / "mps"
        complete_mps_setup.rename(mps_in_project)

        # Create malformed pyproject.toml
        (project_root / "pyproject.toml").write_text("invalid toml content [[[")

        discovery = MpsDiscovery()

        # Should fallback to filesystem discovery
        found = discovery.discover(start_path=project_root)
        assert found == mps_in_project

    def test_discovery_priority_env_over_pyproject(
        self, mps_with_pyproject: tuple[Path, Path]
    ):
        """Test that environment variable has priority over pyproject.toml"""
        project_root, mps_dir = mps_with_pyproject

        # Create different MPS directory
        env_mps = project_root.parent / "env-mps"
        env_mps.mkdir()

        # Set environment variable
        os.environ["MPS_BASE_DIR"] = str(env_mps)

        try:
            discovery = MpsDiscovery()
            found = discovery.discover(start_path=project_root)

            # Should use environment variable, not pyproject.toml
            assert found == env_mps
        finally:
            if "MPS_BASE_DIR" in os.environ:
                del os.environ["MPS_BASE_DIR"]

    def test_no_mps_found_anywhere(self, tmp_path: Path):
        """Test error when no MPS directory found"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        discovery = MpsDiscovery()

        with pytest.raises(MpsDirectoryNotFoundError):
            discovery.discover(start_path=empty_dir)

    def test_pyproject_toml_discovery(self, tmp_path: Path) -> None:
        """Test discovery via pyproject.toml"""
        # Create mps directory
        mps_dir = tmp_path / "my-mps"
        mps_dir.mkdir()

        # Create pyproject.toml
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            dedent("""
                [tool.mps]
                base_dir = "my-mps"
            """)
        )

        discovery = MpsDiscovery()
        found = discovery.discover(tmp_path)
        assert found == mps_dir

    def test_filesystem_discovery(self, tmp_path: Path):
        """Test automatic filesystem discovery"""
        # Create mps directory
        mps_dir = tmp_path / "mps"
        mps_dir.mkdir()

        discovery = MpsDiscovery()
        found = discovery.discover(tmp_path)
        assert found == mps_dir

    def test_configuration_error_with_suggestion(self, tmp_path: Path):
        """Test helpful error when pyproject.toml points to wrong path"""
        # Create actual mps directory
        mps_dir = tmp_path / "mps"
        mps_dir.mkdir()

        # Create pyproject.toml pointing to wrong path
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            dedent("""
        [tool.mps]
        base_dir = "wrong-path"
        """)
        )

        discovery = MpsDiscovery()

        with pytest.raises(MpsConfigurationError) as exc_info:
            discovery.discover(tmp_path)

        # Should suggest the correct path
        assert "Did you mean 'mps'?" in str(exc_info.value)
