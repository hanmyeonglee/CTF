import sys

try:
    import tomllib as toml
except ImportError:
    import tomli as toml

try:
    with open('config.toml', 'rb') as f:
        config = toml.load(f)
except FileNotFoundError:
    print('config.toml not found, maybe run `cp config.toml.example config.toml`', file=sys.stderr)
    sys.exit(1)

