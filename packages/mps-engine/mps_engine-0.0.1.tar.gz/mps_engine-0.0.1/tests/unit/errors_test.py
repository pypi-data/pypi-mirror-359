# import pytest
#
# import mps
# from mps.core.config import MpsConfig
# from mps.core.errors import (
#     MpsDirectoryNotFoundError,
# )
#
#
# class TestErrorScenarios:
#     """Test that errors are handled gracefully with helpful messages"""
#
#     def test_nonexistent_mps_directory(self):
#         """Test error when MPS directory doesn't exist"""
#         with pytest.raises(MpsDirectoryNotFoundError) as exc_info:
#             MpsConfig(base_dir="/definitely/does/not/exist")
#
#         assert "does/not/exist" in str(exc_info.value)
#
#     def test_nonexistent_pattern(self):
#         """Test error when pattern doesn't exist"""
#         with pytest.raises(Exception):  # Replace with specific error
#             mps.pattern("definitely-does-not-exist")
#
#     def test_malformed_pyproject_toml(self, tmp_path):
#         """Test handling of malformed pyproject.toml"""
#         # Create bad pyproject.toml
#         pyproject = tmp_path / "pyproject.toml"
#         pyproject.write_text("invalid toml [[[")
#
#         # Should gracefully handle and continue discovery
#         from mps.core.discovery import MpsDiscovery
#
#         discovery = MpsDiscovery()
#
#         # Should not crash, just return None
#         result = discovery._read_pyproject_mps_config(pyproject)
#         assert result is None
#
#
# def test_helpful_error_messages():
#     """Test that error messages are actually helpful"""
#     try:
#         mps.pattern("nonexistent-pattern")
#         assert False, "Should have raised an error"
#     except Exception as e:
#         error_msg = str(e).lower()
#         # Error should be informative
#         assert any(
#             word in error_msg for word in ["not found", "does not exist", "missing"]
#         )
