# pre-commit-hooks

A selection of quality-of-life tools for use with [pre-commit](https://github.com/pre-commit/pre-commit).

## Table of Contents

<!--TOC-->

- [pre-commit-hooks](#pre-commit-hooks)
  - [Table of Contents](#table-of-contents)
  - [Using with Pre-Commit](#using-with-pre-commit)
  - [add-msg-issue](#add-msg-issue)
    - [Defining a custom template](#defining-a-custom-template)

<!--TOC-->

## Using with Pre-Commit

Add the following to your `.pre-commit-config.yaml`

```yaml
-   repo: https://github.com/BenjaminMummery/pre-commit-hooks
    rev: v1.0.0
    hooks:
    -   id: add-msg-issue
```

TODO: instructions on setting up pre-commit to run on prepare-commit-message

For more information on pre-commit, see [https://github.com/pre-commit/pre-commit](https://github.com/pre-commit/pre-commit)

## add-msg-issue

Search the branch name for something that looks like an issue message, and insert it into the commit message.

Please note that using this hook means that your commit messages will never be empty, so commits will not abort for that reason.

### Defining a custom template

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

These correspond to the issue id, subject line, and body of the commit message. The default template is `{subject}\n\n[{issue_id}]\n{body}`.
