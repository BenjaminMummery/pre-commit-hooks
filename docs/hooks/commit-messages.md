<!--- Copyright (c) 2026 Benjamin Mummery -->

# Add Message Issue Hook

`add-msg-issue` looks for an issue identifier in the current branch name and inserts it into the commit message during `prepare-commit-msg`.

For a branch named `feature/TEST-01/demo`, this command:

```bash
git commit -m "feat: Add the feature" -m "Implementation details."
```

produces:

```text
feat: Add the feature

[TEST-01]
Implementation details.
```

## Custom template

Pass a template through the hook configuration:

```yaml
- id: add-msg-issue
  args:
    - --template
    - "{issue_id}: {subject}\n\n{body}"
```

Templates must contain `{issue_id}`, `{subject}`, and `{body}`. The default is:

```text
{subject}

[{issue_id}]
{body}
```

Because the issue identifier adds content to the message, remove it as well if you
intend to abort an editor-based commit by leaving the message empty.
