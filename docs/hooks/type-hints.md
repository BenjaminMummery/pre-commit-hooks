<!--- Copyright (c) 2026 Benjamin Mummery -->

# Synchronize type hints

`sync-type-hints` compares Python signature annotations with type information in Google, NumPy, and Sphinx-style docstrings.

Types are synchronized in both directions by default.

## Synchronization from the Docstring to the Signature

Missing signature annotations are populated from the docstring:

```python
def greet(name, count):
    """Greet someone.

    Args:
        name (str): Who to greet.
        count (int): How many times.

    Returns:
        bool: Whether the greeting succeeded.
    """
```

becomes:

```python
def greet(name: str, count: int) -> bool:
    """Greet someone.

    Args:
        name (str): Who to greet.
        count (int): How many times.

    Returns:
        bool: Whether the greeting succeeded.
    """
```

## Synchronization from the Signature to the Docstring

When the signature is typed but an existing docstring entry is not, the docstring is updated:
```python
def greet(name: str) -> bool:
    """Greet someone.

    Args:
        name: Who to greet.

    Returns:
        Whether the greeting succeeded.
    """
```

becomes

```python
def greet(name: str) -> bool:
    """Greet someone.

    Args:
        name (str): Who to greet.

    Returns:
        bool: Whether the greeting succeeded.
    """
```

The hook only synchronizes existing parameter and return documentation; it does not create missing entries or sections.

## Resolve disagreements

Configure how clashes are handled:

```toml
[tool.sync_type_hints]
on-clash = "error"
```

`on-clash` accepts:

- `error` — report the conflict without choosing a source.
- `prefer-signature` — treat signature information as authoritative.
- `prefer-docstring` — treat docstring information as authoritative.

Command-line arguments take precedence over `pyproject.toml` or `setup.cfg`.

## Keep types only in signatures

```toml
[tool.sync_type_hints]
signature-types-only = false
```

`signature-types-only` first resolves information between the signature and docstring as above, then removes type information from the docstring, leaving the signature as the single source of truth.

## Inline Ignores

Ignore an individual function on its definition line:

```python
def legacy(name):  # pragma: no sync-type-hints
    return name
```
