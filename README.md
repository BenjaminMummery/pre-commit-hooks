<!--- Copyright (c) 2022 - 2026 Benjamin Mummery -->

# pre-commit-hooks

A collection of quality-of-life hooks for
[pre-commit](https://github.com/pre-commit/pre-commit).

See the [full documentation](https://benjaminmummery.github.io/pre-commit-hooks/)
for installation, configuration, examples, and the generated Python API reference.

## Hooks

| Hook | Purpose |
| --- | --- |
| `add-copyright` | Add missing copyright notices. |
| `update-copyright` | Update copyright ranges from Git history before push. |
| `add-msg-issue` | Add an issue identifier from the branch name to commit messages. |
| `sort-file-contents` | Sort sectioned text files and optionally remove duplicates. |
| `no-import-testtools-in-src` | Reject test-framework imports from production source. |
| `americanise` | Normalize UK and Canadian spellings to US spellings. |
| `sync-type-hints` | Synchronize signature and docstring type information. |

## Quick start

Add the hooks you need to `.pre-commit-config.yaml`, replacing `<version>` with a
released tag:

```yaml
default_install_hook_types: [pre-commit, pre-push, prepare-commit-msg]

repos:
  - repo: https://github.com/BenjaminMummery/pre-commit-hooks
    rev: <version>
    hooks:
      - id: add-copyright
      - id: update-copyright
      - id: add-msg-issue
      - id: sort-file-contents
      - id: no-import-testtools-in-src
      - id: americanise
      - id: sync-type-hints
```

`add-copyright` requires an explicit copyright holder. For example:

```toml
[tool.add_copyright]
name = "Example Ltd"
```

Then install the configured Git hooks:

```bash
pre-commit install
```

Read [Getting started](https://benjaminmummery.github.io/pre-commit-hooks/getting-started/)
for stage-specific commands and configuration details.

## Development

Contributor setup, test targets, documentation builds, and packaging commands are
described in the
[contributing guide](https://benjaminmummery.github.io/pre-commit-hooks/contributing/).
