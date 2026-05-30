# Release Process

This document describes the automated release process for the Imou Life integration.

## Overview

Releases are fully automated using [python-semantic-release](https://python-semantic-release.readthedocs.io/) (PSR). When you merge a PR to `master`, PSR analyzes the conventional commit messages and automatically:

1. Determines the next version (patch, minor, or major)
2. Updates `pyproject.toml` and `manifest.json` with the new version
3. Creates a git tag (`vX.Y.Z`)
4. Creates a GitHub Release with auto-generated notes

A separate workflow then builds the `imou_life.zip` artifact and attaches it to the release.

## How It Works

```
Feature Branch          master              GitHub
     |                    |                   |
     |-- PR merged ------>|                   |
     |                    |-- PSR runs ------>|
     |                    |   (bump version,  |
     |                    |    create tag,     |
     |                    |    create release) |
     |                    |                   |-- zip workflow
     |                    |                   |   (build & attach)
     |                    |                   |
```

## Release Workflow

### Step 1: Create a Feature Branch

```bash
git checkout master
git pull origin master
git checkout -b feat/my-feature
```

### Step 2: Make Changes with Conventional Commits

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```bash
# Patch release (1.6.0 -> 1.6.1)
git commit -m "fix: resolve API timeout on battery devices"

# Minor release (1.6.0 -> 1.7.0)
git commit -m "feat: add PTZ preset support"

# Major release (1.6.0 -> 2.0.0)
git commit -m "feat!: redesign configuration flow"
# or
git commit -m "feat: redesign configuration flow

BREAKING CHANGE: config flow version incremented, existing entries need migration"
```

**Commit types that trigger releases:**
- `fix:` -> patch bump
- `feat:` -> minor bump
- `feat!:` or `BREAKING CHANGE` -> major bump

**Commit types that do NOT trigger releases:**
- `docs:`, `chore:`, `test:`, `ci:`, `refactor:`, `style:`, `perf:`

### Step 3: Update Changelog (Optional)

For significant releases, update `docs/CHANGELOG.md` with detailed release notes before merging:

```markdown
## [1.7.0] - 2026-06-01

### Added
- PTZ preset support for compatible cameras

### Fixed
- API timeout on battery-powered devices
```

### Step 4: Create and Merge PR

```bash
git push origin feat/my-feature
gh pr create --title "feat: add PTZ preset support" --body "Description of changes"
```

After review, merge the PR to `master`.

### Step 5: Automatic Release

On merge to `master`, the following happens automatically:

1. **Semantic Release workflow** analyzes commits since the last tag
2. If release-worthy commits exist, PSR bumps the version and creates a GitHub Release
3. **Release Artifacts workflow** triggers on the new release, builds `imou_life.zip`, and attaches it

### Step 6: Verify

```bash
gh release list --limit 3
gh release view v1.7.0
```

## Manual Release

If automation fails or you need to create a release manually:

```bash
# Create zip file
cd custom_components
zip -r ../imou_life.zip imou_life/ -x "*.pyc" -x "*__pycache__*" -x "*.git*"
cd ..

# Create release
gh release create v1.7.0 \
  --title "v1.7.0" \
  --generate-notes \
  imou_life.zip

# Clean up
rm imou_life.zip
```

## Running PSR Locally

For dry-run testing:

```bash
pip install python-semantic-release
semantic-release version --noop
```

## Version Numbering

Following [Semantic Versioning](https://semver.org/):
- **Patch** (1.0.X): Bug fixes, small changes
- **Minor** (1.X.0): New features, backward compatible
- **Major** (X.0.0): Breaking changes

## Configuration

PSR is configured in `pyproject.toml` under `[tool.semantic_release]`:
- Version is tracked in both `pyproject.toml` and `manifest.json`
- **PSR does NOT update `docs/CHANGELOG.md`** — auto-generation is disabled (`changelog_file = ""`)
- `docs/CHANGELOG.md` is maintained manually as the curated release history
- GitHub Release notes are auto-generated from PR labels (via `.github/release.yml`)
- Tags use `v` prefix (e.g., `v1.7.0`)
- Releases are created directly as stable (no pre-release graduation)

## Commit Message Validation

A [commitizen](https://commitizen-tools.github.io/commitizen/) pre-commit hook validates that all commit messages follow the conventional commits format. Install hooks with:

```bash
pre-commit install --hook-type commit-msg
```

## Troubleshooting

### No release created after merge

**Check:** Were there release-worthy commits (`fix:` or `feat:`)?
```bash
git log --oneline v1.6.0..HEAD
```
Commits with `docs:`, `chore:`, `test:`, etc. don't trigger releases.

### Workflow doesn't trigger

```bash
gh run list --limit 5
gh run view <run-id> --log-failed
```

### Zip not attached to release

Run the artifacts workflow manually:
```bash
gh workflow run "Release Artifacts" -f tag=v1.7.0
```

### Version mismatch between files

PSR updates both `pyproject.toml` and `manifest.json`. If they're out of sync:
```bash
semantic-release version --noop  # Check what PSR thinks the version should be
```

## References

- [python-semantic-release docs](https://python-semantic-release.readthedocs.io/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Commitizen](https://commitizen-tools.github.io/commitizen/)
