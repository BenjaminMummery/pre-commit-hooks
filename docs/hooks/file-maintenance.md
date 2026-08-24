
<!--- Copyright (c) 2026 Benjamin Mummery -->

# File-maintenance hooks

## Sort file contents

`sort-file-contents` sorts lines inside sections while preserving the section order.
A section starts with a comment and ends at the next blank line.

```text title="Before"
# languages
Python
Go

# tools
uv
pre-commit
```

```text title="After"
# languages
Go
Python

# tools
pre-commit
uv
```

Pass `--unique` (or `-u`) to remove duplicates within a section.
Duplicates across different sections are retained and reported because the hook cannot determine the correct section.

## Prevent test imports in source

`no-import-testtools-in-src` rejects imports of `pytest` or `unittest` from source files whose paths do not identify them as tests.

## Normalize spelling

`americanise` replaces common UK and Canadian spellings with US spellings while preserving the original capitalization where possible.

Add project-specific replacements with `-w SOURCE:REPLACEMENT`:

```yaml
- id: americanise
  args:
    - -w
    - forth:fourth
```

Ignore one occurrence with an inline marker:

```python
def initialise():  # pragma: no americanise
    pass
```
