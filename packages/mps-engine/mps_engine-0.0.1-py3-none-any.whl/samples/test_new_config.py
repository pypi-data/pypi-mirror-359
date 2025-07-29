from mps.core.config import MpsConfig
from mps.core.discovery import MpsDiscovery


def test_basic_discovery() -> None:
    """Test if our discovery finds the existing test MPS directory."""
    discovery = MpsDiscovery()

    found_path = discovery.discover()
    print(f"Discovery found: {found_path}")

    config = MpsConfig()
    print(f"Config base_dir: {config.base_dir}")
    print(f"Config pattern_dir: {config.pattern_dir}")
    print(f"Config strategy_dir: {config.strategy_dir}")
    print(f"Config meta_dir: {config.meta_dir}")
    print(f"Config context_dir: {config.ext.context_dir}")
    print(f"Config preference_dir: {config.ext.preference_dir}")
    print(f"Config configuration_dir: {config.ext.configuration_dir}")


if __name__ == "__main__":
    test_basic_discovery()
