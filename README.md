<!--- Copyright (c) 2022 - 2026 Benjamin Mummery -->

# pre-commit-hooks

A selection of quality-of-life tools for use with [pre-commit](https://github.com/pre-commit/pre-commit).

## Table of Contents

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [1. Usage](#1-usage)
  - [1.1 Usage with Pre-Commit](#11-usage-with-pre-commit)
  - [1.2 Usage in a vanilla hook](#12-usage-in-a-vanilla-hook)
- [2. Hooks](#2-hooks)
  - [2.1 The `add-copyright` Hook](#21-the-add-copyright-hook)
    - [2.1.1 Configuration](#211-configuration)
      - [CLI Arguments](#cli-arguments)
      - [`.pre-commit-config.yaml` Configuration](#pre-commit-configyaml-configuration)
      - [Config file configuration](#config-file-configuration)
    - [2.1.2 Command line arguments](#212-command-line-arguments)
      - [`pyproject.toml`](#pyprojecttoml)
    - [2.1.3 `.add-copyright-hook-config.yaml` file](#213-add-copyright-hook-configyaml-file)
    - [2.1.4 Language Support](#214-language-support)
  - [2.2 The `update-copyright` Hook](#22-the-update-copyright-hook)
  - [2.3 The `add-msg-issue` Hook](#23-the-add-msg-issue-hook)
    - [2.3.1 Example 1: Usage when defining the commit msg from command line](#231-example-1-usage-when-defining-the-commit-msg-from-command-line)
    - [2.3.2 Example 2: Usage when defining the commit msg from editor](#232-example-2-usage-when-defining-the-commit-msg-from-editor)
    - [2.3.3 Defining a custom template](#233-defining-a-custom-template)
  - [2.4 The `sort-file-contents` hook](#24-the-sort-file-contents-hook)
    - [2.4.1 Section - aware sorting](#241-section---aware-sorting)
    - [2.4.2 Uniqueness](#242-uniqueness)
  - [2.5 The `no-import-testtools-in-src` hook](#25-the-no-import-testtools-in-src-hook)
  - [2.6 The `americanise` hook](#26-the-americanise-hook)
    - [2.6.1 Configuration](#261-configuration)
      - [`.pre-commit-config.yaml` Configuration](#pre-commit-configyaml-configuration-1)
      - [Inline ignores](#inline-ignores)
  - [2.7 The `sync-type-hints` hook](#27-the-sync-type-hints-hook)
    - [2.7.1 Configuration](#271-configuration)
      - [`.pre-commit-config.yaml` Configuration](#pre-commit-configyaml-configuration-2)
      - [Config file configuration](#config-file-configuration-1)
      - [Inline ignores](#inline-ignores-1)
    - [2.7.2 Supported docstring formats](#272-supported-docstring-formats)
- [3. Development](#3-development)
  - [3.0 Setup](#30-setup)
  - [3.1 Testing](#31-testing)
    - [3.1.1 Testing scheme](#311-testing-scheme)
    - [3.1.2 Running Tests](#312-running-tests)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## 1. Usage

### 1.1 Usage with Pre-Commit

Add the following to the `.pre-commit-config.yaml` in your repo (or create it if necessary):

```yaml
default_install_hook_types: [pre-commit, prepare-commit-msg]

repos:
-   repo: https://github.com/BenjaminMummery/pre-commit-hooks
    rev: ''
    hooks:
    -   id: add-copyright
    -   id: update-copyright
    -   id: add-msg-issue
    -   id: sort-file-contents
        files: .gitignore
    -   id: no-import-testtools-in-src
    -   id: americanise
    -   id: sync-type-hints
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
docstr = true
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

#### 2.1.3 `.add-copyright-hook-config.yaml` file

If command line arguments are not specified, the hook will look for a file named `.add-copyright-hook-config.yaml` in the root of the git repo, and read the name and year from there.
This file should be formatted as follows:

```yaml
name: James T. Kirk
format: Property of {name} as of {year}
```

#### 2.1.4 Language Support

The add-copyright hook currently runs on changed source files of the following types:

| Language   | File Extension | Example |
|------------|----------------|---------|
| C++        | `.cpp`         | `// Copyright (c) 1969 Buzz` |
| C#         | `.cs`          | `/* Copyright (c) 1969 Buzz */` |
| CSS        | `.css`         |`/* Copyright (c) 1969 Buzz */` |
| Dart       | `.dart`        | `// Copyright (c) 1969 Buzz` |
| HTML       | `.html`        | `<!--- Copyright (c) 1969 Buzz -->` |
| Java       | `.java`        | `// Copyright (c) 1969 Buzz` |
| Javascript | `.js`          | `// Copyright (c) 1969 Buzz` |
| Kotlin     | `.kt`          | `// Copyright (c) 1969 Buzz` |
| Lua        | `.lua`         | `-- Copyright (c) 1969 Buzz` |
| Markdown   | `.md`          | `<!--- Copyright (c) 1969 Buzz -->` |
| Perl       | `.pl`          | `# Copyright (c) 1969 Buzz` |
| PHP        | `.PHP`         | `// Copyright (c) 1969 Buzz` |
| Python[^1] | `.py`          | `# Copyright (c) 1969 Buzz` |
| Ruby       | `.rb`          | `# Copyright (c) 1969 Buzz` |
| Rust       | `.rst`         | `// Copyright (c) 1969 Buzz` |
| Scala      | `.scala`       | `// Copyright (c) 1969 Buzz` |
| SQL        | `.sql`         | `-- Copyright (c) 1969 Buzz` |
| Swift      | `.swift`       | `// Copyright (c) 1969 Buzz` |

[^1]: For python files we also support inserting copyright info into/as module-level docstrings. To enable this, insert the following lines into your `pyproject.toml` or `.add-copyright-hook-config.yaml`:

    ```yaml
    [tool.add-copyright.python]
    docstr=true
    ```

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
# new file:   test.py
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

### 2.5 The `no-import-testtools-in-src` hook

This hook checks for imports of `pytest` and/or `unittest` in source files that are not test files (i.e. do not have 'test' somewhere in their path).

### 2.6 The `americanise` hook

This hook checks for common non-US spellings of english words (e.g. 'initialise' rather than 'initialize') and corrects them. The hook will try to match the case of the original word, although this may be imprecise for complex case patterns when the correct spelling of the word is a different length.

#### 2.6.1 Configuration

##### `.pre-commit-config.yaml` Configuration

Additional words can be manually added in the `.pre-commit-config.yaml`. For example, if we want to change all instances of `absence` to `absence` and all instances of `forth` to `fourth`, the configuration would be:

```yaml
repos:
-   repo: https://github.com/BenjaminMummery/pre-commit-hooks
    rev: ''
    hooks:
    -   id: americanise
        args: ["-w absence:absence", "-w forth:fourth"]
```

##### Inline ignores

Individual instances can be excluded from this hook by marking them with an inline comment reading `pragma: no americanise`. For example:

```python
def initialise():  # pragma: no americanise
    print("initialise")
```

will be corrected to:

```python
def initialise():  # pragma: no americanise
    print("initialise")
```

### 2.7 The `sync-type-hints` hook

This hook synchronises type information between Python function and method signatures and their docstrings. It parses type annotations from docstring `Args`/`Parameters` and `Returns` sections, compares them with type hints in the signature, and updates the source file accordingly.

By default, missing signature annotations are filled in from the docstring. When the two sources disagree, the hook fails so that the conflict can be resolved manually.

For example, given:

```python
def greet(name, count):
    """Say hello.

    Args:
        name (str): Who to greet.
        count (int): How many times.

    Returns:
        bool: Whether greeting succeeded.
    """
    return True
```

the hook will rewrite the signature as:

```python
def greet(name: str, count: int) -> bool:
```

The docstring is left unchanged unless configured otherwise.

#### 2.7.1 Configuration

##### `.pre-commit-config.yaml` Configuration

```yaml
repos:
-   repo: https://github.com/BenjaminMummery/pre-commit-hooks
    rev: ''
    hooks:
    -   id: sync-type-hints
        args:
        -   --on-clash=prefer-signature
        -   --remove-docstring-types
```

The hook accepts the following command line arguments:

| Flag | Description |
|------|-------------|
| `--on-clash` | How to handle disagreements between docstring and signature types. One of `error` (default), `prefer-signature`, or `prefer-docstring`. |
| `--remove-docstring-types` | Remove type information from docstrings after syncing. |

When `--on-clash` is set to:

- `error`: the hook fails with a descriptive message.
- `prefer-signature`: docstring types are updated to match the signature.
- `prefer-docstring`: signature annotations are updated to match the docstring.

##### Config file configuration

Configuration can also be supplied in `pyproject.toml` or `setup.cfg`:

```toml
[tool.sync_type_hints]
on-clash = "error"
remove-docstring-types = false
```

Command line arguments take precedence over config file settings.

##### Inline ignores

Individual functions can be excluded by marking the definition line with an inline comment reading `pragma: no sync-type-hints`. For example:

```python
def legacy(name):  # pragma: no sync-type-hints
    """Args:
        name (str): Ignored by the hook.
    """
    return name
```

#### 2.7.2 Supported docstring formats

The hook recognises type information in the following docstring styles:

| Style | Parameter example | Return example |
|-------|-------------------|----------------|
| Google | `name (str): Description.` | `bool: Description.` |
| NumPy | `name : str` | `bool` (on the line after the `Returns` underline) |
| Sphinx | `:param str name: Description.` | `:rtype: bool` |

## 3. Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management, packaging, and running commands in a locked virtual environment.

### 3.0 Setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then sync dependencies and install pre-commit hooks:

```bash
make install
```

Or manually:

```bash
uv sync
uv run pre-commit install
```

Build a wheel or source distribution with:

```bash
uv build
```

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

The provided `Makefile` defines commands for running various combinations of tests. All targets run through `uv run` (for example, `make test` runs unit and integration tests).

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
  - `test_sync_type_hints`
- Testing shared resources:
  - `test_shared`: run all unit tests for utilities on which multiple hooks rely and show coverage (fail fast).
