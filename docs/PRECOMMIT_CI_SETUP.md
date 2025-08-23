# Pre-commit.ci Setup Instructions

This document explains how to enable pre-commit.ci for the Imou Life integration repository.

## 🔧 What is pre-commit.ci?

[Pre-commit.ci](https://pre-commit.ci) is a free service that runs your pre-commit hooks on every pull request, automatically fixing code style issues and ensuring consistent code quality.

## 🚀 Enabling pre-commit.ci

### Step 1: Visit pre-commit.ci

1. Go to [https://pre-commit.ci](https://pre-commit.ci)
2. Click "Sign in with GitHub"
3. Authorize the pre-commit.ci app

### Step 2: Enable for Repository

1. Once signed in, you'll see a list of your repositories
2. Find `maximunited/imou_life` in the list
3. Click the toggle switch to enable pre-commit.ci
4. The service will automatically detect the `.pre-commit-config.yaml` file

### Step 3: Verify Setup

1. Create a test pull request with a code style issue
2. Pre-commit.ci should automatically:
   - Run all configured hooks
   - Fix any auto-fixable issues
   - Comment on the PR with results
   - Update the PR with fixes

## ⚙️ Configuration

The repository includes two configuration files:

### `.pre-commit-config.yaml`
- Main pre-commit configuration
- Defines all hooks and their settings
- Works for both local development and pre-commit.ci

### `.pre-commit-ci.yaml`
- Specific configuration for pre-commit.ci service
- Excludes hooks that can't run in CI (like local manifest validation)
- Sets up auto-update schedule and commit messages

## 🎯 Features Enabled

### Automatic Code Fixes
- **Black**: Python code formatting
- **isort**: Import sorting
- **Trailing whitespace**: Removes extra spaces
- **End of file**: Ensures files end with newline

### Code Quality Checks
- **Flake8**: Python linting
- **Codespell**: Spell checking
- **YAML/JSON**: Syntax validation
- **Large files**: Prevents accidental large file commits

### Auto-updates
- **Monthly updates**: Pre-commit hooks are updated automatically
- **Security**: Always uses latest versions of tools
- **Maintenance**: Reduces manual maintenance overhead

## 📊 Benefits

### For Maintainers
- **Consistent Quality**: All PRs meet code standards automatically
- **Reduced Review Time**: Focus on logic, not style issues
- **Zero Maintenance**: Hooks update automatically

### For Contributors
- **Immediate Feedback**: See issues before manual review
- **Auto-fixes**: Many issues are fixed automatically
- **Learning**: See best practices in action

### For Project
- **Professional Standards**: Maintains high code quality
- **Contributor Friendly**: Easy for new contributors
- **Time Saving**: Reduces back-and-forth on style issues

## 🔍 Monitoring

### Status Badge
The pre-commit.ci status badge in `docs/DEVELOPMENT.md` shows:
- ✅ Green: All checks passing
- ❌ Red: Some checks failing
- 🟡 Yellow: Checks running

### Pull Request Integration
Pre-commit.ci will:
- Add status checks to pull requests
- Comment with detailed results
- Automatically push fixes when possible
- Block merging if critical issues exist

## 🛠️ Troubleshooting

### Common Issues

#### Hook Failures
- **Local hooks**: Some hooks only work locally (excluded via `.pre-commit-ci.yaml`)
- **Dependencies**: CI environment may lack certain dependencies
- **Permissions**: Some hooks may need special permissions

#### Solutions
- Check `.pre-commit-ci.yaml` for excluded hooks
- Review pre-commit.ci logs for specific errors
- Update hook configurations if needed

### Getting Help
- **Pre-commit.ci docs**: [https://pre-commit.ci/](https://pre-commit.ci/)
- **GitHub Issues**: Report issues in the repository
- **Pre-commit docs**: [https://pre-commit.com/](https://pre-commit.com/)

## 📈 Next Steps

After enabling pre-commit.ci:

1. **Test with a PR**: Create a test pull request to verify functionality
2. **Update Documentation**: Ensure all contributors know about the service
3. **Monitor Performance**: Check that CI runs complete successfully
4. **Adjust Configuration**: Fine-tune settings based on experience

---

**Pre-commit.ci helps maintain professional code quality standards automatically!**
