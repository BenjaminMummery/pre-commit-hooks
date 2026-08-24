<!--- Copyright (c) 2026 Benjamin Mummery -->

# Contributing

## Set up the project

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run:

```bash
make install
```

This synchronizes the locked environment and installs the configured Git hooks.

## Run tests

```bash
make test
```

Useful focused targets include:

| Target | Runs |
| --- | --- |
| `make test_unit` | Unit tests under `src/` |
| `make test_integration` | Hook integration tests |
| `make test_system` | End-to-end `pre-commit try-repo` tests |
| `make test_all` | All three levels |
| `make lint` | Repository pre-commit checks |

## Work on the documentation

Start the live-reloading development server:

```bash
make docs-serve
```

Open <http://127.0.0.1:8000/>. Before submitting documentation changes, run the
same strict build used in CI:

```bash
make docs-build
```

The generated `site/` directory is disposable and must not be committed.

## Build a distribution

```bash
uv build
```
