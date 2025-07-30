# API Design
## Architecture
```
MpsConfig
├── Sources (priority order):
│   ├── 1. Explicit API calls
│   ├── 2. Environment variables
│   ├── 3. pyproject.toml
│   ├── 4. Auto-discovery
│   └── 5. Defaults
├── Validation layer
└── Cache layer (for performance)
```
## Simple usage
```python
config = MpsConfig()  # Auto-discovers
config.base_dir  # Returns Path object
```

## Explicit usage
```python
config = MpsConfig(base_dir="/custom/path")
```

## Environment/file-based
```python
config = MpsConfig()  # Reads from env/pyproject.toml
```
