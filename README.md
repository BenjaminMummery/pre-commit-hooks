# pre-commit-hooks

A selection of quality-of-life tools for use with pre-commit.

## Table of Contents

<!--TOC-->

## Using with Pre-Commit

Add the following to your `.pre-commit-config.yaml`

```yaml
-   repo: https://github.com/BenjaminMummery/pre-commit-hooks
    rev: v0.0.1
    hooks:
    -   id: add-msg-issue
```

For more information on pre-commit, see [https://github.com/pre-commit/pre-commit](https://github.com/pre-commit/pre-commit)

## What the hooks actually do

### add-msg-issue

Search the branch name for something that looks like an issue message, and insert it into the commit message.

TODO: instructions on setting up pre-commit to run on prepare-commit-message