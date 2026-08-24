<!--- Copyright (c) 2026 Benjamin Mummery -->

# pre-commit-hooks

A collection of focused quality-of-life hooks for
[pre-commit](https://pre-commit.com/).

The hooks can add and maintain copyright notices, enrich commit messages, keep
structured files tidy, normalize spelling, and synchronize Python type hints with
docstrings.

## Available hooks

| Hook | Purpose | Default stage |
| --- | --- | --- |
| [`add-copyright`](hooks/copyright.md#add-copyright-notices) | Add missing copyright notices to supported source files. | `pre-commit` |
| [`update-copyright`](hooks/copyright.md#update-copyright-ranges) | Extend copyright ranges from committed file history. | `pre-push`, `manual` |
| [`add-msg-issue`](hooks/commit-messages.md#add-message-issue-hook) | Add an issue identifier from the branch name to a commit message. | `prepare-commit-msg` |
| [`sort-file-contents`](hooks/file-maintenance.md#sort-file-contents) | Sort sectioned files such as `.gitignore`. | `pre-commit` |
| [`no-import-testtools-in-src`](hooks/file-maintenance.md#prevent-test-imports-in-source)  | Prevent test-framework imports in production code. | `pre-commit` |
| [`americanise`](hooks/file-maintenance.md#normalize-spelling) | Normalize common non-US spellings. | `pre-commit` |
| [`sync-type-hints`](hooks/type-hints.md) | Synchronize signature annotations and docstring types. | `pre-commit` |

[Get started](getting-started.md){ .md-button .md-button--primary }
[API reference](reference/index.md){ .md-button }

## Requirements

- Python 3.9 or newer
- Git
- [pre-commit](https://pre-commit.com/)

Each released revision is installed by pre-commit in an isolated environment, so
consuming projects do not need to add this package to their application dependencies.
