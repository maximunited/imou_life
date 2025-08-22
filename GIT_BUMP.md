# Git Bump - One Command Version Management

This project includes a Git alias that automatically handles version bumping, committing, tagging, and pushing in a single command.

## How It Works

Instead of manually updating versions, committing, and creating tags, you can now use:

```bash
git bump <version>
```

This single command automatically:
1. ✅ Updates the version in `manifest.json`
2. ✅ Commits the change
3. ✅ Creates the git tag
4. ✅ Pushes everything to GitHub
5. ✅ Triggers the release workflow

## Usage

### Basic Version Bump
```bash
git bump 1.0.24
```

### Version Bump with Custom Message
```bash
git bump 1.0.24 "Bug fixes and improvements"
```

## What Happens Automatically

When you run `git bump 1.0.24`:

1. **Version Update**: Changes `"version": "1.0.23"` to `"version": "1.0.24"` in manifest.json
2. **Auto-commit**: Creates a commit with message "Bump version to 1.0.24"
3. **Tag Creation**: Creates git tag `v1.0.24`
4. **Auto-push**: Pushes both the commit and tag to GitHub
5. **Workflow Trigger**: GitHub Actions automatically creates a pre-release

## Example Session

```bash
$ git bump 1.0.24

🚀 Git Bump - Version 1.0.24
===============================
Current version: 1.0.23
New version: 1.0.24

Updating manifest.json...
Staging changes...
Committing changes: Bump version to 1.0.24
[master abc1234] Bump version to 1.0.24
 1 file changed, 1 insertion(+), 1 deletion(-)

Creating tag: v1.0.24
Pushing changes and tag...
To https://github.com/maximunited/imou_life.git
   def5678..abc1234  master -> master
 * [new tag]         v1.0.24 -> v1.0.24

🎉 Version bump completed successfully!
✅ Version updated to 1.0.24
✅ Changes committed and pushed
✅ Tag v1.0.24 created and pushed
✅ GitHub Actions workflow triggered

Next steps:
1. Check the Actions tab in your GitHub repository
2. Wait for the Release Management workflow to complete
3. Check the Releases section for your new pre-release
```

## Benefits

- **Single Command**: No more manual steps
- **Automatic**: Everything happens automatically
- **Safe**: Checks for existing tags and uncommitted changes
- **Smart**: Validates version format and warns about issues
- **Complete**: Handles the entire release process
- **Git Native**: Works as a Git alias, feels natural

## Requirements

- PowerShell (Windows)
- Git configured with remote origin
- Write access to the repository

## Troubleshooting

### Alias not found
Make sure you've set up the alias:
```bash
git config alias.bump "!powershell -ExecutionPolicy Bypass -File git-bump.ps1"
```

### Permission denied
Run PowerShell as Administrator or adjust execution policy:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Tag already exists
The script automatically handles existing tags by deleting and recreating them.

## Alternative Commands

If you prefer not to use the alias, you can run the script directly:
```bash
powershell -ExecutionPolicy Bypass -File git-bump.ps1 1.0.24
```

## Next Steps

After running `git bump`:
1. Check the [Actions tab](https://github.com/maximunited/imou_life/actions) in your repository
2. Wait for the "Release Management" workflow to complete
3. Check the [Releases section](https://github.com/maximunited/imou_life/releases) for your new pre-release
4. Test the pre-release before graduating to stable

That's it! One command does everything. 🎉
