# pre-commit-hooks

A selection of quality-of-life tools for use with [pre-commit](https://github.com/pre-commit/pre-commit).

## Table of Contents

<!--TOC-->

- [pre-commit-hooks](#pre-commit-hooks)
  - [Table of Contents](#table-of-contents)
  - [1. Usage with Pre-Commit](#1-usage-with-pre-commit)
  - [2. Usage in a vanilla hook](#2-usage-in-a-vanilla-hook)
  - [3. The `add-copyright` Hook](#3-the-add-copyright-hook)
    - [3.1 Controlling the name and year](#31-controlling-the-name-and-year)
  - [4. The `add-msg-issue` Hook](#4-the-add-msg-issue-hook)
    - [4.1 Example 1: Usage when defining the commit msg from command line](#41-example-1-usage-when-defining-the-commit-msg-from-command-line)
    - [4.2 Example 2: Usage when defining the commit msg from editor](#42-example-2-usage-when-defining-the-commit-msg-from-editor)
    - [4.3 Defining a custom template](#43-defining-a-custom-template)

<!--TOC-->

## 1. Usage with Pre-Commit

Add the following to the `.pre-commit-config.yaml` in your repo (or create it if necessary):

```yaml
default_install_hook_types: [pre-commit, prepare-commit-msg]

repos:
-   repo: https://github.com/BenjaminMummery/pre-commit-hooks
    rev: v1.0.0
    hooks:
    -   id: add-copyright
    -   id: add-msg-issue
```

Even if you've already installed pre-commit, it may be necessary to run:


```bash
pre-commit install
```

(this is because `add-msg-issue` runs at the `prepare-commit-msg` stage which Pre-commit does not install to by default).

You should see the following output:

```
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
pre-commit installed at .git/hooks/prepare-commit-msg
```

For more information on pre-commit, see [https://github.com/pre-commit/pre-commit](https://github.com/pre-commit/pre-commit)

## 2. Usage in a vanilla hook

The following is a minimal example of a `.git/hooks/prepare-commit-msg` to run add-msg-issue:

```bash
#!/usr/bin/env bash
add-msg-issue $1
```

Note that this assumes that you've installed add-msg-issue in your global python environment.

## 3. The `add-copyright` Hook

Check changed source files for something that looks like a copyright comment. If one is not found, insert one.

By default, the copyright message is constructed in the format

```
# Copyright (c) <year> <name>
```

where the year is the current year, and the name is sourced from the git `user.name` configuration.

### 3.1 Controlling the name and year

The `add-copyright` hook accepts the following command line arguments to control the values inserted into new copyright messages:

| Flag | Description |
|------|-------------|
| `-n` / `--name` | Set a custom name to be used rather than git's `user.name` |
| `-y` / `--year` | Set a custom year to be used rather than the current year. |

If you're using a `.pre-commit-config.yaml`, these can be configured as follows:

```yaml
repos:
-   repo: https://github.com/BenjaminMummery/pre-commit-hooks
    rev: v1.0.0
    hooks:
    -   id: add-copyright
        args: ["-n", "James T. Kirk", "-y", "1701"]
    -   id: add-msg-issue
```

## 4. The `add-msg-issue` Hook

Search the branch name for something that looks like an issue message, and insert it into the commit message.

Please note that using this hook means that your commit messages will never be empty, so commits will not abort for that reason.

### 4.1 Example 1: Usage when defining the commit msg from command line

In a branch called `feature/TEST-01/demo`, the command `git commit -m "test commit" -m "Some more description about our test commit."` produces a commit message that reads

```
test commit

[TEST-01]
Some more description about our test commit.
```

### 4.2 Example 2: Usage when defining the commit msg from editor

If a message is not specified in the command line, the issue ID is instead inserted into the message prior to it opening in the editor. You should be greeted with something that looks like:

```markdown
[TEST-01]

# Please enter the commit message for your changes. Lines starting
# with '#' will be ignored, and an empty message aborts the commit.
#
# On branch feature/TEST-01/demo
# Changes to be committed:
#	new file:   test.py
#
```

Note that this means that the commit will not be aborted due to an empty message unless you delete the inserted ID.

### 4.3 Defining a custom template

If the default template is not to your liking, you can define your own by passing the `--template` argument:

```yaml
-   repo: https://github.com/BenjaminMummery/pre-commit-hooks
    rev: v1.0.0
    hooks:
    -   id: add-msg-issue
        args: ["--template", "{issue_id}: {subject}\n\n{body}"]
```
The template must include the following keywords:

```python
{issue_id}
{subject}
{body}
```

These correspond to the issue id, subject line, and body of the commit message. The default template is:

```python
"{subject}\n\n[{issue_id}]\n{body}"
```
