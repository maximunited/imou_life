# Mergify Auto-merge Configuration

This document explains how Mergify is configured for the Imou Life integration and how to use it.

## What is Mergify?

Mergify is a GitHub bot that automates pull request management, including auto-merging, labeling, and workflow automation.

## Automatic Actions

### Auto-merge (with conditions)

Mergify will **automatically merge** PRs when ALL conditions are met:

#### Dependabot Updates

**Minor/Patch updates** (auto-merge without approval):
- ✅ All CI checks pass (Pre-commit, HACS, Hassfest)
- ✅ No merge conflicts
- ✅ Not a draft PR
- ✅ Title matches: `chore(deps): ... minor|patch`, `chore(deps-dev):`, or `ci(deps):`

**Major updates** (requires approval):
- ✅ All CI checks pass (Pre-commit, HACS, Hassfest)
- ✅ At least 1 approval from a maintainer
- ✅ No merge conflicts
- ✅ Not a draft PR

#### Pre-commit.ci Updates

- ✅ All CI checks pass (Pre-commit, HACS, Hassfest)
- ✅ No merge conflicts
- ✅ Not a draft PR

### Automatic Labeling

Mergify automatically adds labels based on:

| Condition | Label Added |
|-----------|-------------|
| Title starts with `feat:` | `enhancement` |
| Title starts with `fix:` | `bug` |
| Title starts with `docs:` | `documentation` |
| Title starts with `refactor:` | `refactoring` |
| Title starts with `test:` | `tests` |
| Title starts with `ci:` | `github-actions` |
| Files modified: `.github/workflows/` | `github-actions` |
| Files modified: `config/requirements*.txt` | `dependencies` |
| Files modified: `docs/` | `documentation` |
| Author: `dependabot[bot]` + CI passes | `auto-merge`, `dependencies` |
| Author: `pre-commit-ci[bot]` + CI passes | `auto-merge`, `dependencies` |

### Automatic Comments

**Missing Tests Warning:**
- Triggered on: PRs with `feat:` title but no changes in `tests/`
- Bypass: Add `skip-tests` label

**Missing Changelog Reminder:**
- Triggered on: PRs with `feat:` or `fix:` title but no changes to `docs/CHANGELOG.md`
- Bypass: Add `skip-changelog` label

**Merge Conflict Notice:**
- Triggered on: PRs authored by you with merge conflicts
- Action: Comment with rebase instructions

### Automatic Cleanup

- **Branch deletion**: Merged PR branches are automatically deleted
- **Stale review dismissal**: Approvals are dismissed when new commits are pushed (safety feature)

## Manual Commands

You can control Mergify with comments on PRs:

| Command | Action |
|---------|--------|
| `@mergifyio rebase` | Rebase the PR on the base branch |
| `@mergifyio update` | Update the PR with the base branch (merge) |
| `@mergifyio refresh` | Refresh Mergify's evaluation of the PR |
| `@mergifyio backport <branch>` | Backport the PR to another branch |

## Required CI Checks

For auto-merge to work, these checks must pass:

1. ✅ **Pre-commit** - Code formatting and linting
2. ✅ **HACS** - HACS validation
3. ✅ **Hassfest** - Home Assistant validation

**Note:** Only core checks are required (Pre-commit, HACS, Hassfest).
Optional checks like the compatibility matrix are not required.

## Bypassing Auto-merge

To prevent auto-merge on a specific PR:

1. **Convert to draft** - Draft PRs never auto-merge
2. **Add `do-not-merge` label** - Add this custom label
3. **Request changes** - Any "Request changes" review blocks auto-merge

## Configuration File

The Mergify configuration is in `.mergify.yml` at the repository root.

## Queue System

Mergify uses a merge queue to:
- Serialize merges (one at a time)
- Re-test before final merge
- Use squash merge with clean commit messages

## Security

Mergify has these safety features:

- ✅ **No major version auto-merge without approval** - Human review required for breaking changes
- ✅ **All CI must pass** - No shortcuts around quality checks
- ✅ **Conflict detection** - Won't merge PRs with conflicts
- ✅ **Stale review dismissal** - New commits invalidate old approvals
- ✅ **Bot scope limited** - Only Dependabot and pre-commit.ci auto-merge

## Troubleshooting

### PR not auto-merging

Check the Mergify dashboard on the PR (bottom of conversation):
1. Click "Show all checks"
2. Find "Mergify" check
3. Click "Details" to see why conditions aren't met

Common reasons:
- ❌ CI check still running or failed
- ❌ Merge conflicts present
- ❌ PR is a draft
- ❌ Title doesn't match expected pattern
- ❌ Major version update needs approval

### Forcing a recheck

Comment on the PR:
```text
@mergifyio refresh
```

### Disabling Mergify temporarily

Add the `do-not-merge` label to prevent auto-merge on a specific PR.

## Monitoring

View Mergify activity:
- **PR checks**: See Mergify status in PR checks section
- **Labels**: Track `auto-merge` label
- **Comments**: Mergify comments explain actions taken

## Further Reading

- [Mergify Documentation](https://docs.mergify.com/)
- [Merge Queue Guide](https://docs.mergify.com/merge-queue/)
- [Configuration Reference](https://docs.mergify.com/configuration/)
