# Mergify Quick Start

## 🚀 Installation Steps

1. **Install Mergify App**
   - Go to: https://github.com/apps/mergify
   - Click "Configure"
   - Select `maximunited/imou_life` repository
   - Click "Install & Authorize"

2. **Merge the PR**
   - Create PR from branch `feat/add-mergify`
   - Review `.mergify.yml` configuration
   - Merge the PR

3. **Test Auto-merge** (optional)
   - Wait for next Dependabot PR
   - Watch it auto-merge when CI passes ✅

## 📋 What Auto-merges

| PR Type | Auto-merge? | Conditions |
|---------|-------------|------------|
| Dependabot patch/minor | ✅ Yes | CI passes |
| Dependabot major | ⚠️ Needs approval | CI passes + 1 approval |
| Pre-commit.ci | ✅ Yes | CI passes |
| Your PRs | ❌ No | Manual merge |

## 🎯 Most Useful Features

### 1. Auto-merge Dependabot
No more manually merging dependency updates! Mergify handles it when all tests pass.

### 2. Auto-labeling
PRs get labeled automatically:
- `feat:` → `enhancement`
- `fix:` → `bug`
- `docs:` → `documentation`

### 3. Helpful Reminders
- Missing tests on `feat:` PRs
- Missing changelog on `feat:`/`fix:` PRs
- Merge conflict notifications

### 4. Branch Cleanup
Merged PR branches are deleted automatically.

## 🛠️ Commands You Can Use

Comment on any PR:

```bash
@mergifyio refresh      # Re-evaluate PR conditions
@mergifyio rebase       # Rebase on master
@mergifyio update       # Merge master into PR
```

## 🔧 Override Auto-merge

To prevent auto-merge on a specific PR:
1. Convert to **Draft**
2. Add label: `do-not-merge`
3. Request changes in a review

## 📖 Full Documentation

See `docs/MERGIFY.md` for complete documentation.

## ⚙️ Configuration

Edit `.mergify.yml` to customize behavior.

## 🐛 Troubleshooting

**PR not merging?**
1. Check "Show all checks" at bottom of PR
2. Find "Mergify" check
3. Click "Details" to see why

**Force recheck:**
Comment `@mergifyio refresh`

---

**Questions?** See docs/MERGIFY.md or visit https://docs.mergify.com/
