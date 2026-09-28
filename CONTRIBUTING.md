# Development Guide

## Requirements

[mise](https://mise.jdx.dev/) is the only direct requirement. The project tools are declared in [mise.toml](mise.toml) and locked in `mise.lock` files.

Set up the repository with:

```bash
mise trust
mise install
mise run hooks:install
```

## Principles

- Keep reusable commands and toolchain definitions in mise so local development and CI use the same entry points.
- Run `mise run check` before finishing a change. If it fails, try `mise run fix`, then correct any remaining issues manually.
- Keep the uv lockfile in sync with pyproject.toml; use uv to regenerate it.
- Keep Ruff formatting and linting, ty type checks, and pytest passing.

## Common Commands

Run `mise tasks` to see the full task list.

```bash
# Run all read-only checks
mise run check

# Apply safe automatic fixes
mise run fix

# Build the project
mise run build

# Run project tests
mise run test

# Run project-specific lint checks
mise run lint

# Audit project dependencies
mise run audit
```

## GitHub Actions Maintenance

```bash
# Update action versions and pin them to commit hashes
mise run actions:update
```

Read [mise.toml](mise.toml) and [mise.ci.toml](mise.ci.toml) for the task definitions.
