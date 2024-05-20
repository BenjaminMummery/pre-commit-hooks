<!--- Copyright (c) 2022 - 2024 Benjamin Mummery -->

# pre-commit-hooks

A selection of quality-of-life tools for use with [pre-commit](https://github.com/pre-commit/pre-commit).

## Table of Contents

<!--TOC-->

- [pre-commit-hooks](#pre-commit-hooks)
  - [Table of Contents](#table-of-contents)
  - [1. Usage](#1-usage)
    - [1.1 Usage with Pre-Commit](#11-usage-with-pre-commit)
    - [1.2 Usage in a vanilla hook](#12-usage-in-a-vanilla-hook)
  - [2. Hooks](#2-hooks)
    - [2.1 The `add-copyright` Hook](#21-the-add-copyright-hook)
    - [2.2 The `update-copyright` Hook](#22-the-update-copyright-hook)
    - [2.3 The `add-msg-issue` Hook](#23-the-add-msg-issue-hook)
    - [2.4 The `sort-file-contents` hook](#24-the-sort-file-contents-hook)
  - [3. Development](#3-development)
    - [3.1 Testing](#31-testing)

<!--TOC-->

## 1. Usage

### 1.1 Usage with Pre-Commit

Add the following to the `.pre-commit-config.yaml` in your repo (or create it if necessary):

```yaml
default_install_hook_types: [pre-commit, prepare-commit-msg]

repos:
-   repo: https://github.com/BenjaminMummery/pre-commit-hooks
    rev: v1.0.0
    hooks:
    -   id: add-copyright
    -   id: add-msg-issue
    -   id: sort-file-contents
        files: .gitignore
```

Even if you've already installed pre-commit, it may be necessary to run:

```bash
pre-commit install
```

(this is because `add-msg-issue` runs at the `prepare-commit-msg` stage which Pre-commit does not install to by default).

You should see the following output:

```bash
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
pre-commit installed at .git/hooks/prepare-commit-msg
```

For more information on pre-commit, see [https://github.com/pre-commit/pre-commit](https://github.com/pre-commit/pre-commit)

### 1.2 Usage in a vanilla hook

The following is a minimal example of a `.git/hooks/prepare-commit-msg` to run add-msg-issue:

```bash
#!/usr/bin/env bash
add-msg-issue $1
```

Note that this assumes that you've installed add-msg-issue in your global python environment.

## 2. Hooks

### 2.1 The `add-copyright` Hook

Check changed source files for something that looks like a copyright comment. If one is not found, insert one.

By default, the copyright message is constructed as a comment in the format

```text
Copyright (c) <year> <name>
```

where the year is the current year, and the name is sourced from the git `user.name` configuration.

#### 2.1.1 Configuration

If required, the default behaviour can be overruled either by command line arguments or configuration files.

##### CLI Arguments

```term
add-copyright [-n NAME] [-f FORMAT] [FILES]
```

##### `.pre-commit-config.yaml` Configuration

```yaml
- repo: https://github.com/BenjaminMummery/pre-commit-hooks
  rev: v1.5.0
  hooks:
    - id: add-copyright
      args: ["-n NAME", "-f FORMAT"]
```

##### Config file configuration

We currently support configuration options in `pyproject.toml` and `setup.cfg` files.

```toml
[tool.add_copyright]
name = "NAME"
format = "FORMAT"
```

Behaviour for individual languages can also be configured:

```toml
[tool.add_copyright.python]
format = "FORMAT"
```

where there is a conflict between individual language settings and the global tool settings, the language settings are given authority.

#### 2.1.2 Command line arguments

The `add-copyright` hook accepts the following command line arguments to control the values inserted into new copyright messages:

| Flag | Description |
|------|-------------|
| `-n` / `--name` | Set a custom name to be used rather than git's `user.name` |
| `-f` / `--format` | Set a custom f-string for the copyright to be inserted. Must contain `{name}` and `{year}`. |

If you're using a `.pre-commit-config.yaml`, these can be configured as follows:

```yaml
repos:
-   repo: https://github.com/BenjaminMummery/pre-commit-hooks
    rev: v1.4.0
    hooks:
    -   id: add-copyright
        args: ["-n", "James T. Kirk", "-f", "Property of {name} as of {year}"]
    -   id: add-msg-issue
```

Alternatively, a local configuration file can be specified:

##### `pyproject.toml`

```toml
[tool.add_copyright]
name = "James T. Kirk"
format = "Property of {name} as of {year}"
```

The config file can contain name and format.
Any properties that are not set by the config file will be inferred from the current year / git user name.

#### 2.1.3 `.add-copyright-hook-config.yaml` file.

If command line arguments are not specified, the hook will look for a file named `.add-copyright-hook-config.yaml` in the root of the git repo, and read the name and year from there.
This file should be formatted as follows:

```yaml
name: James T. Kirk
format: Property of {name} as of {year}
```

#### 2.1.4 Language Support.

The add-copyright hook currently runs on changed source files of the following types:

| Language   | File Extension | Example |
|------------|----------------|---------|
| C++        | `.cpp`         | `// Copyright (c) 1969 Buzz` |
| C#         | `.cs`          | `/* Copyright (c) 1969 Buzz */` |
| HTML       | `.html`        | `<!--- Copyright (c) 1969 Buzz -->` |
| Java       | `.java`        | `// Copyright (c) 1969 Buzz` |
| Javascript | `.js`          | `// Copyright (c) 1969 Buzz` |
| Markdown   | `.md`          | `<!--- Copyright (c) 1969 Buzz -->` |
| Perl       | `.pl`          | `# Copyright (c) 1969 Buzz` |
| PHP        | `.PHP`         | `// Copyright (c) 1969 Buzz` |
| Python     | `.py`          | `# Copyright (c) 1969 Buzz` |
| Typescript | `.ts`          | `// Copyright (c) 1969 Buzz` |




### 2.2 The `update-copyright` Hook

Check changed source files for something that looks like a copyright comment.
If one is found, the end date is checked against the current date and updated if it is out of date.


### 2.3 The `add-msg-issue` Hook

Search the branch name for something that looks like an issue message, and insert it into the commit message.

#### 2.3.1 Example 1: Usage when defining the commit msg from command line

In a branch called `feature/TEST-01/demo`, the command `git commit -m "test commit" -m "Some more description about our test commit."` produces a commit message that reads

```
test commit

[TEST-01]
Some more description about our test commit.
```

#### 2.3.2 Example 2: Usage when defining the commit msg from editor

If a message is not specified in the command line, the issue ID is instead inserted into the message prior to it opening in the editor.
You should be greeted with something that looks like:

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

#### 2.3.3 Defining a custom template

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

These correspond to the issue id, subject line, and body of the commit message.
The default template is:

```python
"{subject}\n\n[{issue_id}]\n{body}"
```

### 2.4 The `sort-file-contents` hook

The `sort-file-contents` hook sorts the lines in the specified files while retaining sections.
This is primarily aimed at managing large .gitignore files.

#### 2.4.1 Section - aware sorting

Sections are identified as sets of sequential lines preceded by a comment and separated from other sections by a blank line.
The contents of each section are sorted alphabetically, while the overall structure of sections is unchanged.
For example:

```python
# section 1
delta
bravo

# section 2
charlie
alpha
```

would be sorted as:

```python
# section 1
bravo
delta

# section 2
alpha
charlie
```

Development of this hook was motivated by encountering file contents sorters that would produce the following:

```python
# section 1
# section 2
alpha
bravo
charlie
delta
```

#### 2.4.2 Uniqueness

The `-u` or `--unique` flag causes the hook to check the sorted lines for uniqueness.
Duplicate entries within the same section will be removed automatically;
lines that are duplicated between sections will be left in place and a warning raised to the user.
This latter behaviour is due to us not knowing which section the line should belong to.

## 3. Development

### 3.1 Testing

#### 3.1.1 Testing scheme

Tests are organised in three levels:
1. Unit: tests for individual methods.
   All other methods should be mocked.
   Hooks have a single entry point so are best tested with the integration tests, unit tests should be used where necessary.
2. Integration: tests for combinations of methods.
3. System: end-to-end tests.
   Uses the `pre-commit try_repo` facility.


#### 3.1.2 Running Tests

The provided `Makefile` defines commands for running various combinations of tests:

- General Purpose:
    - `test`: run unit and integration tests and show coverage (fail fast).
    - `test_all`: as `test`, but also runs system tests (fail fast).
    - `clean`: remove the test venv and all temporary files.
- Testing by Level: run all tests of the specified level and show coverage (fail fast).
    - `test_unit`
    - `test_integration`
    - `test_system`
- Testing by hook: run all tests for the specified hook and show coverage (fail slow).
    - `test_add_copyright`
    - `test_add_issue`
    - `test_sort_file_contents`
    - `test_update_copyright`
- Testing shared resources:
    - `test_shared`: run all unit tests for utilities on which multiple hooks rely and show coverage (fail fast).
