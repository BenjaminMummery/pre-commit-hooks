<!--- Copyright (c) 2026 Benjamin Mummery -->

# Getting started

## Configure the hooks

Add the repository to `.pre-commit-config.yaml`, replacing `<version>` with a
released tag:

```yaml
default_install_hook_types:
  - pre-commit
  - pre-push
  - prepare-commit-msg

repos:
  - repo: https://github.com/BenjaminMummery/pre-commit-hooks
    rev: <version>
    hooks:
      - id: add-copyright
      - id: update-copyright
      - id: add-msg-issue
      - id: sort-file-contents
        files: ^\.gitignore$
      - id: no-import-testtools-in-src
      - id: americanise
      - id: sync-type-hints
```

Only enable the hooks that your project needs.

## Configure copyright ownership

`add-copyright` deliberately has no implicit copyright holder. Configure a stable
holder in `pyproject.toml`:

```toml
[tool.add_copyright]
name = "Example Ltd"
```

For a personal repository, explicitly opt in to Git's `user.name`:

```toml
[tool.add_copyright]
use_git_user = true
```

The two options are mutually exclusive. See the
[copyright guide](hooks/copyright.md) for formatting and language-specific options.

## Install the Git hooks

```bash
pre-commit install
```

The `default_install_hook_types` setting installs all three hook types needed by the
example. Existing clones should run the command again after adding `pre-push` or
`prepare-commit-msg`.

## Test the configuration

Run the normal commit-stage hooks over the repository:

```bash
pre-commit run --all-files
```

Run the history-based copyright updater explicitly:

```bash
pre-commit run update-copyright --hook-stage manual --all-files
```

Hooks that modify files return a non-zero status. Review their changes, stage the
files, and rerun the command.

## Run a hook directly

The installed console commands can also be called from a conventional Git hook or
another automation system.
For example, a minimal `.git/hooks/prepare-commit-msg` that invokes `add-msg-issue` is:

```bash
#!/usr/bin/env bash
add-msg-issue "$1"
```

This requires the package to be installed in the environment used by Git.
Using pre-commit is recommended because it creates and manages an isolated environment for the hooks.
