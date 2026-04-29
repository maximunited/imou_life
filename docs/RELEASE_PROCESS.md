# Release Process

This document describes the automated release process for the Imou Life integration and how to fix issues when automation fails.

## Overview

The release process is managed by two main components:

1. **`git bump` command** (PowerShell script: `tools/scripts/git-bump.ps1`)
   - Updates `manifest.json` version
   - Generates changelog entry in `docs/CHANGELOG.md`
   - Commits changes
   - Creates and pushes git tag
   - Triggers GitHub Actions workflow

2. **Release Management workflow** (`.github/workflows/releases.yml`)
   - Triggered by tag push (e.g., `v1.2.0`)
   - Reads version from git tag
   - Extracts changelog using `mindsers/changelog-reader-action`
   - Creates integration zip file (`imou_life.zip`)
   - Creates GitHub release with zip attachment

## Automated Release (Happy Path)

### Step 1: Ensure Clean Changelog Format

Before bumping version, ensure `docs/CHANGELOG.md` follows [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
# Changelog

## [1.2.0] (2026-04-29)
### Added
- New feature 1
- New feature 2

### Changed
- Changed behavior 1

### Fixed
- Bug fix 1
- **SECURITY**: Security fix description

### Tests
- Test updates
```

**Important**: The changelog-reader-action expects:
- Version format: `## [X.Y.Z] (YYYY-MM-DD)`
- Date format: `YYYY-MM-DD`
- Standard sections: Added, Changed, Deprecated, Removed, Fixed, Security, Tests

### Step 2: Run git bump

```bash
# Auto-increment patch version (1.1.2 → 1.1.3)
git bump

# Specify exact version with description
git bump 1.2.0 "Battery optimization refactoring and critical security fixes"

# The script will:
# 1. Update manifest.json
# 2. Add basic changelog entry (if not exists)
# 3. Commit changes
# 4. Create and push tag v1.2.0
# 5. Trigger GitHub Actions
```

**Note**: The `git bump` script creates a basic changelog entry. For detailed release notes, manually edit the changelog BEFORE running `git bump`.

### Step 3: Monitor Workflow

```bash
# Check workflow status
gh run list --limit 5

# View specific run
gh run view <run-id>

# View failed logs
gh run view <run-id> --log-failed
```

The workflow should:
1. ✅ Extract version from tag
2. ✅ Read changelog entry
3. ✅ Create zip file
4. ✅ Create GitHub pre-release

### Step 4: Verify Release

```bash
# List releases
gh release list

# View specific release
gh release view v1.2.0
```

The release should include:
- Release notes from changelog
- Attached `imou_life.zip` file
- Pre-release status (for version tags like v1.2.0)

## Manual Release (When Automation Fails)

### Common Failure: "No log entry found for version X.Y.Z"

**Cause**: The changelog format doesn't match Keep a Changelog standard, or the version header is malformed.

**Fix**:

1. **Check the workflow logs**:
   ```bash
   gh run view <run-id> --log-failed
   ```

2. **Verify changelog format**:
   - Version header must be: `## [X.Y.Z] (YYYY-MM-DD)`
   - Must have at least one section (Added/Changed/Fixed/etc.)
   - Date format must be `YYYY-MM-DD` (not `DD-MM-YYYY`)

3. **Fix the changelog** in `docs/CHANGELOG.md`:
   ```markdown
   ## [1.2.0] (2026-04-29)
   ### Added
   - Comprehensive CLAUDE.md with project architecture

   ### Fixed
   - **SECURITY**: Removed hardcoded credentials from camera.py
   ```

4. **Manually create the release**:
   ```bash
   # Delete failed draft release if exists
   gh release delete ci-v1.2.0 -y

   # Create zip file
   cd custom_components
   zip -r ../imou_life.zip imou_life/ -x "*.pyc" -x "*__pycache__*" -x "*.git*"
   cd ..

   # Extract changelog for this version
   python -c "
   import re
   with open('docs/CHANGELOG.md', 'r', encoding='utf-8') as f:
       content = f.read()
   match = re.search(r'## \[1\.2\.0\].*?(?=## \[1\.1\.)', content, re.DOTALL)
   if match:
       with open('release_notes.txt', 'w', encoding='utf-8') as f:
           f.write(match.group(0).strip())
   "

   # Create pre-release
   gh release create v1.2.0 \
     --title "v1.2.0 - Brief Description" \
     --notes-file release_notes.txt \
     --prerelease \
     imou_life.zip

   # Clean up
   rm release_notes.txt imou_life.zip
   ```

### Manual Release with Enhanced Notes

If you want to enhance release notes after initial creation:

```bash
# Update existing release
gh release edit v1.2.0 \
  --title "v1.2.0 - Battery Optimization & Security Fixes" \
  --notes-file release_notes.txt

# Add missing zip file
gh release upload v1.2.0 imou_life.zip
```

## Release Types

### Pre-release (default for version tags)

Created when pushing a version tag (e.g., `v1.2.0`):
- Marked as pre-release in GitHub
- Used for testing before stable release
- Can be graduated to stable release

### Stable Release

To graduate a pre-release to stable:

```bash
# Method 1: Push 'stable' tag
git tag stable
git push origin stable

# Method 2: Edit release manually
gh release edit v1.2.0 --prerelease=false

# Method 3: Use workflow dispatch
# Go to GitHub Actions → Release Management → Run workflow
# Select "release" type
```

### CI Draft Releases

Automatically created on pushes to master/main:
- Tag format: `ci-vX.Y.Z`
- Draft status
- For internal testing only
- Usually cleaned up after testing

## Best Practices

1. **Always enhance changelog before release**:
   - Run `git bump` creates basic entry
   - Edit `docs/CHANGELOG.md` to add detailed sections
   - Commit enhanced changelog
   - Then the tag will have proper notes

2. **Test the changelog parser**:
   ```bash
   # Install the changelog reader locally if needed
   npm install -g changelog-reader

   # Test parsing
   changelog-reader --version 1.2.0 ./docs/CHANGELOG.md
   ```

3. **Version numbering**:
   - Patch (1.0.X): Bug fixes, small changes
   - Minor (1.X.0): New features, backward compatible
   - Major (X.0.0): Breaking changes

4. **Tag management**:
   ```bash
   # List all tags
   git tag

   # Delete local tag
   git tag -d v1.2.0

   # Delete remote tag
   git push origin :refs/tags/v1.2.0

   # Re-create tag at specific commit
   git tag v1.2.0 <commit-sha>
   git push origin v1.2.0
   ```

## Troubleshooting

### Workflow doesn't trigger

**Check**:
```bash
# Verify tag was pushed
git ls-remote --tags origin

# Check workflow file
cat .github/workflows/releases.yml | grep "tags:"
```

**Fix**: Ensure tag starts with `v` (e.g., `v1.2.0`, not `1.2.0`)

### Zip file not created

**Check logs**:
```bash
gh run view <run-id> --log | grep "Create zip"
```

**Manual fix**: See "Manual Release" section above

### Changelog reader fails with validation errors

**Disable validation**:
Edit `.github/workflows/releases.yml`:
```yaml
- name: Get Changelog Entry
  uses: mindsers/changelog-reader-action@v2
  with:
    validation_depth: 10
    validation_level: none  # Add this line
    version: ${{ steps.version.outputs.version }}
    path: ./docs/CHANGELOG.md
```

### Release already exists

**Options**:
```bash
# Delete and recreate
gh release delete v1.2.0 -y
gh release create v1.2.0 ...

# Update existing
gh release edit v1.2.0 --notes-file new_notes.txt
```

## Workflow Configuration

The Release Management workflow (`.github/workflows/releases.yml`) supports:

- **Triggers**:
  - Tag push: `v*` (creates pre-release)
  - Tag push: `stable` (graduates latest pre-release to stable)
  - Branch push: master/main (creates CI draft)
  - Manual dispatch (custom release type)

- **Outputs**:
  - GitHub release (pre-release, stable, or draft)
  - Integration zip file (`imou_life.zip`)
  - Changelog-based release notes

- **Configuration**:
  - Uses `mindsers/changelog-reader-action@v2` for changelog parsing
  - Requires Keep a Changelog format
  - Validates last 10 changelog entries
  - Can be customized via workflow inputs

## References

- [Keep a Changelog](https://keepachangelog.com/) - Changelog format standard
- [Semantic Versioning](https://semver.org/) - Version numbering standard
- [mindsers/changelog-reader-action](https://github.com/mindsers/changelog-reader-action) - GitHub Action documentation
- [GitHub CLI](https://cli.github.com/manual/gh_release) - `gh release` command reference

## Support

For issues with the release process:
1. Check workflow logs: `gh run view <run-id> --log-failed`
2. Verify changelog format matches Keep a Changelog standard
3. Test manually create release before debugging automation
4. Report issues at: https://github.com/maximunited/imou_life/issues
