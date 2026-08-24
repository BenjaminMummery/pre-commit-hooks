<!--- Copyright (c) 2026 Benjamin Mummery -->

# Copyright hooks

Copyright management is handled by a pair of hooks:

* [`add-copyright`](#add-copyright-notices) runs on the pre-commit stage and adds copyright information to changed files that do not already have it.
* [`update-copyright`](#update-copyright-ranges) runs on the pre-push stage and updates the date ranges on changed files based on their commit history.

## Add copyright notices

`add-copyright` checks supported source files and inserts a notice when one is missing.
The default format is:

```text
Copyright (c) <year> <name>
```

The current year is used for a new change.
If the file already has committed history, the notice inserts a range that begins with the earliest year available from Git.

### Holder configuration

Choose exactly one holder strategy:

=== "Fixed holder"

    ```toml
    [tool.add_copyright]
    name = "Example Ltd"
    ```

=== "Git user"

    ```toml
    [tool.add_copyright]
    use_git_user = true
    ```

The equivalent command-line options are `--name NAME` and `--use-git-user`.
Command-line configuration takes precedence over project configuration.

!!! warning

    When neither strategy is configured, a file that needs a notice causes an actionable configuration error.
    Files that already contain a notice are left alone.

### Custom formatting

The format must contain both `{name}` and `{year}`:

```toml
[tool.add_copyright]
name = "Example Ltd"
format = "Copyright © {year} {name}. All rights reserved."
```

Per-language formatting overrides the global format:

```toml
[tool.add_copyright.python]
format = "Copyright © {year} {name}"
docstr = true
```

With `docstr = true`, Python notices are inserted into the module docstring instead of a comment.

### Supported languages

The hook supports C++, C#, CSS, Dart, HTML, Java, JavaScript, Kotlin, Lua, Markdown, Perl, PHP, Python, Ruby, Rust, Scala, SQL, and Swift.
Comment syntax is selected from the file type.

## Update copyright ranges

`update-copyright` extends a parsed notice to cover the locally available committer history for that file.
It follows renames where Git can detect them and never shortens an existing range, which avoids damaging notices in shallow clones or repositories with imported history.

The updater runs at `pre-push`, when the commits being examined already exist.
It is also available through the `manual` stage:

```bash
pre-commit run update-copyright --hook-stage manual --all-files
```

If a pre-push run modifies a notice, the push is stopped.
Review and commit the change, then push again.

!!! note

    A pushed revision must be the checked-out `HEAD`, because the hook edits working
    tree files. Pushes of another local branch are rejected with an explanatory
    error.
