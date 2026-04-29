# Pre-Commit Hook Optimization

## Summary

Optimized `.pre-commit-config.yaml` by removing 2 unnecessary hooks that were not relevant for this Windows-based Python project.

## Hooks Removed

1. **`check-executables-have-shebangs`**
   - **Why removed**: This hook checks that executable files have shebangs (`#!/bin/bash`, etc.)
   - **Not relevant because**: Our scripts are Windows `.bat` and `.ps1` files which don't use shebangs
   - **Impact**: None - Windows scripts use file extensions for interpretation, not shebangs

2. **`check-shebang-scripts-are-executable`**
   - **Why removed**: This hook checks that files with shebangs are marked executable
   - **Not relevant because**: Same as above - no shebang-based scripts in this project
   - **Impact**: None - Windows file permissions work differently

## Hooks Kept (All Still Needed)

### File Safety & Validation
- ✅ `check-added-large-files` - Prevent large files in git
- ✅ `check-yaml` - Validates workflow files, services.yaml, quality_scale.yaml
- ✅ `check-json` - Validates manifest.json, translations/*.json
- ✅ `check-toml` - Validates pyproject.toml
- ✅ `check-merge-conflict` - Detect merge conflict markers
- ✅ `check-case-conflict` - Prevent case-sensitivity issues

### File Content Fixes
- ✅ `end-of-file-fixer` - Add newline at end of files
- ✅ `trailing-whitespace` - Remove trailing spaces
- ✅ `fix-byte-order-marker` - Remove BOM from files
- ✅ `mixed-line-ending` - Fix CRLF/LF inconsistencies

### Python-Specific
- ✅ `check-docstring-first` - Ensure docstrings come first
- ✅ `debug-statements` - Catch leftover debug prints
- ✅ `requirements-txt-fixer` - Sort requirements.txt files

### VCS
- ✅ `check-vcs-permalinks` - Validate git permalinks

### Code Quality
- ✅ `black` - Python code formatting
- ✅ `flake8` - Python linting
- ✅ `isort` - Import sorting
- ✅ `codespell` - Spell checking

### Custom
- ✅ `validate-manifest` - Home Assistant manifest validation

## Results

- **Before**: 21 hooks
- **After**: 19 hooks (-2)
- **Test status**: All hooks still pass ✅
- **Performance**: Slightly faster (2 fewer hook executions)
- **Functionality**: No loss - removed hooks never applied to our files

## Verification

All hooks tested and passing:
```bash
python -m pre_commit run --all-files
# 19 hooks passed
```
