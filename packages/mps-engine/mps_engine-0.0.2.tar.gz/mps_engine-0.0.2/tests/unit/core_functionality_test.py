from pathlib import Path

import mps


class TestPatternSystem:
    """Test pattern loading and injection together"""

    def test_pattern_loading(self):
        p = mps.pattern("translate")
        assert p is not None
        assert "lang_code" in str(p.content)

    def test_pattern_injection(self):
        p = mps.pattern("translate")
        injected = mps.inject(p, lang_code="en-US")
        assert "en-US" in injected.content
        assert "{{lang_code}}" not in injected.content

    def test_pattern_injection_stateful(self):
        p = mps.pattern("translate")
        p.inject(lang_code="en-US")
        assert "en-US" in p.content
        assert "{{lang_code}}" not in p.content
        assert "lang_code" in p.variables
        assert p.variables["lang_code"] == "en-US"
        assert p["lang_code"] == p.variables["lang_code"] == "en-US"


class TestExtensions:
    """Test all extension components"""

    def test_context_loading(self):
        c = mps.ext.context("biography")
        assert c is not None

    def test_preference_loading(self):
        pref = mps.ext.preference("latex")
        assert pref is not None

    def test_configuration_loading(self):
        config = mps.ext.configuration("short-generator")
        assert config.temperature == 0.1


def test_strategy_loading():
    """Test basic strategy loading"""
    s = mps.strategy("cot")
    assert s is not None
    assert "step by step" in s.prompt.lower()


def test_get_mps_base_dir():
    """Test getting base directory"""
    base_dir = mps.get_mps_base_dir()
    assert base_dir.exists()


def test_set_mps_base_dir(tmp_path: Path):
    """Test setting base directory"""
    test_mps = tmp_path / "test-mps"
    test_mps.mkdir()

    mps.set_mps_base_dir(test_mps)
    current_dir = mps.get_mps_base_dir()
    assert current_dir == test_mps.resolve()
