from pathlib import Path

import pytest

from mps.core.config import MpsConfig
from mps.core.errors import MpsConfigurationError, MpsDirectoryNotFoundError


class TestMpsConfig:
    """Test the main configuration class"""

    def test_explicit_base_dir(self, tmp_path: Path):
        """Test explicit base_dir parameter"""
        mps_dir = tmp_path / "mps"
        mps_dir.mkdir()

        config = MpsConfig(base_dir=mps_dir)
        assert config.base_dir == mps_dir.resolve()

    def test_directory_properties(self, tmp_path: Path):
        """Test all directory properties"""
        mps_dir = tmp_path / "mps"
        mps_dir.mkdir()

        config = MpsConfig(base_dir=mps_dir)

        assert config.pattern_dir == mps_dir / "pattern"
        assert config.strategy_dir == mps_dir / "strategy"
        assert config.meta_dir == mps_dir / "meta"
        assert config.ext.context_dir == mps_dir / "ext" / "context"
        assert config.ext.preference_dir == mps_dir / "ext" / "preference"
        assert config.ext.configuration_dir == mps_dir / "ext" / "configuration"

    def test_caching_behavior2(self, tmp_path: Path):
        """Test that paths are cached properly"""
        mps_dir = tmp_path / "mps"
        mps_dir.mkdir()

        config = MpsConfig(base_dir=mps_dir)

        # first access
        dir1 = config.base_dir
        # second access - should be same object (cached)
        dir2 = config.base_dir

        assert dir1 is dir2  # same object reference

    def test_extension_caching_behavior(self, tmp_path: Path):
        mps_dir = tmp_path / "mps"
        mps_dir.mkdir()

        config = MpsConfig(base_dir=mps_dir)

        dir1 = config.ext.configuration_dir
        dir2 = config.ext.configuration_dir
        assert dir1 is dir2

    def test_explicit_base_dir2(self, complete_mps_setup: Path):
        """Test explicit base_dir parameter"""
        config = MpsConfig(base_dir=complete_mps_setup)

        assert config.base_dir == complete_mps_setup.resolve()

    def test_all_directory_properties(self, complete_mps_setup: Path):
        """Test that all directory properties work correctly"""
        config = MpsConfig(base_dir=complete_mps_setup)

        # core directories
        assert config.pattern_dir == complete_mps_setup / "pattern"
        assert config.strategy_dir == complete_mps_setup / "strategy"
        assert config.meta_dir == complete_mps_setup / "meta"

        # extension directories
        assert config.ext.context_dir == complete_mps_setup / "ext" / "context"
        assert config.ext.preference_dir == complete_mps_setup / "ext" / "preference"
        assert (
            config.ext.configuration_dir == complete_mps_setup / "ext" / "configuration"
        )

    def test_caching_behavior(self, complete_mps_setup: Path):
        """Test that directory resolution is cached"""
        config = MpsConfig(base_dir=complete_mps_setup)

        # multiple accesses should return same object
        dir1 = config.base_dir
        dir2 = config.base_dir

        assert dir1 is dir2  # same object (cached)

    def test_nonexistent_explicit_directory(self, tmp_path: Path):
        """Test error when explicit directory doesn't exist"""
        nonexistent = tmp_path / "does-not-exist"

        with pytest.raises(MpsDirectoryNotFoundError):
            config = MpsConfig(base_dir=nonexistent)
            # error should occur when accessing base_dir
            _ = config.base_dir

    def test_file_instead_of_directory(self, tmp_path: Path):
        """Test error when path points to file instead of directory"""
        file_path = tmp_path / "not-a-directory.txt"
        file_path.write_text("I am a file")

        with pytest.raises(MpsConfigurationError):
            config = MpsConfig(base_dir=file_path)
            _ = config.base_dir

    def test_config_repr(self, complete_mps_setup: Path):
        """Test string representation of config"""
        config = MpsConfig(base_dir=complete_mps_setup)

        repr_str = repr(config)
        assert "MpsConfig" in repr_str
        assert str(complete_mps_setup) in repr_str

    def test_config_repr_with_error(self, tmp_path: Path):
        """Test string representation when config has errors"""
        nonexistent = tmp_path / "does-not-exist"
        config = MpsConfig(base_dir=nonexistent)

        repr_str = repr(config)
        assert "MpsConfig" in repr_str
        assert "error" in repr_str.lower()
