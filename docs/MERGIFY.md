# Mergify Auto-merge Configuration

This document explains how Mergify is configured for the Imou Life integration and how to use it.

## What is Mergify?

Mergify is a GitHub bot that automates pull request management, including auto-merging, labeling, and workflow automation.

## Automatic Actions

### Auto-merge (with conditions)

Mergify **auto-queues** Dependabot and pre-commit.ci PRs when CI passes. The
merge queue then squash-merges them. Human PRs are never auto-queued.

#### Dependabot and pre-commit.ci

- ✅ Author is `dependabot[bot]` or `pre-commit-ci[bot]`
- ✅ Pre-commit, HACS, and Hassfest succeed
- ✅ Not a draft, no `do-not-merge` label

A Mergify comment with an empty "Queue this pull request" checkbox means
auto-queue did **not** fire. Do not treat that as auto-merge.

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
| Author: `dependabot[bot]` | `auto-merge`, `dependencies` |
| Author: `pre-commit-ci[bot]` | `auto-merge`, `dependencies` |

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

Merge queue is always on for this repo. Direct `actions.merge` does not
bypass it. Auto-queue is `merge_protections_settings.auto_merge_conditions`
in `.mergify.yml` (not `actions.merge`).

The queue:
- Serializes merges (one at a time)
- Re-tests before the final squash merge
- Only auto-admits Dependabot and pre-commit.ci; other PRs need the checkbox
  or `@mergifyio queue`

## Security

Mergify has these safety features:

- ✅ **No major version auto-merge without approval** - Human review required for breaking changes
- ✅ **All CI must pass** - No shortcuts around quality checks
- ✅ **Conflict detection** - Won't merge PRs with conflicts
- ✅ **Stale review dismissal** - New commits invalidate old approvals
- ✅ **Bot scope limited** - Only Dependabot and pre-commit.ci auto-merge

## Troubleshooting

### PR not auto-merging

If Mergify only posted "Queue this pull request" with an empty checkbox, the
PR matched queue conditions but `auto_merge_conditions` did not. That is
manual queue, not auto-merge.

Otherwise check the Mergify dashboard on the PR:
1. Click "Show all checks"
2. Find "Mergify Merge Queue"
3. Click "Details" to see why conditions aren't met

Common reasons:
- ❌ Author is not Dependabot / pre-commit.ci (human PRs are manual)
- ❌ CI check still running or failed
- ❌ Merge conflicts present
- ❌ PR is a draft
- ❌ `do-not-merge` label is set

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
