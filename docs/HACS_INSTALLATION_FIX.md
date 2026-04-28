# HACS Installation Directory Structure Fix

**Issue Fixed**: HACS was creating `custom_components/imou_life/imou_life/` instead of `custom_components/imou_life/`

**Date**: 2026-04-29
**Affected Versions**: v1.2.0 and earlier
**Fixed In**: v1.2.1+

---

## Problem Description

### Incorrect Structure (v1.2.0 and earlier)

When installing via HACS, the integration files were placed in the wrong directory:

```
custom_components/
└── imou_life/              ← HACS creates this
    └── imou_life/          ← Zip contains this subdirectory (WRONG!)
        ├── __init__.py
        ├── manifest.json
        └── ...
```

**Result**: Home Assistant couldn't find the integration because files were in `custom_components/imou_life/imou_life/` instead of `custom_components/imou_life/`.

### Correct Structure (v1.2.1+)

```
custom_components/
└── imou_life/              ← HACS creates this
    ├── __init__.py         ← Zip contents go directly here (CORRECT!)
    ├── manifest.json
    └── ...
```

---

## Root Cause

The issue was caused by two configuration problems:

### 1. hacs.json Configuration

**Before (Wrong)**:
```json
{
  "content_in_root": false,  ← Told HACS content is in subdirectory
  "persistent_directory": "imou_life"
}
```

**After (Fixed)**:
```json
{
  "content_in_root": true,   ← Content is in zip root
  (persistent_directory removed - not needed)
}
```

### 2. Release Zip Structure

**Before (Wrong)**:
```bash
# In releases.yml workflow:
cd custom_components/imou_life
zip imou_life.zip -r ./     ← Creates zip with 'imou_life/' subdirectory

# Resulting zip structure:
imou_life/
  __init__.py
  manifest.json
  ...
```

**After (Fixed)**:
```bash
# In releases.yml workflow:
cd custom_components/imou_life
zip -r ../../imou_life.zip . -x "*.pyc" -x "*__pycache__*"

# Resulting zip structure:
__init__.py                 ← Files directly in zip root
manifest.json
...
```

---

## Fixes Applied

### 1. Updated hacs.json

**File**: `hacs.json`

**Changes**:
- Set `"content_in_root": true`
- Removed `"persistent_directory"` (not needed with content_in_root)

**Commit**: [hash]

### 2. Updated Release Workflow

**File**: `.github/workflows/releases.yml`

**Changes**:
- Changed zip creation to put files in zip root
- Added verification step to show zip structure
- Excluded `__pycache__`, `.pyc`, `.git*` files

**Before**:
```yaml
- name: Create zip file for the integration
  run: |
    cd "${{ github.workspace }}/custom_components/${{ steps.information.outputs.name }}"
    zip ${{ steps.information.outputs.name }}.zip -r ./
    mv ${{ steps.information.outputs.name }}.zip "${{ github.workspace }}/"
```

**After**:
```yaml
- name: Create zip file for the integration
  run: |
    cd "${{ github.workspace }}/custom_components/${{ steps.information.outputs.name }}"
    zip -r ../../${{ steps.information.outputs.name }}.zip . -x "*.pyc" -x "*__pycache__*" -x "*.git*"
    mv ../../${{ steps.information.outputs.name }}.zip "${{ github.workspace }}/"
    echo "Verifying zip structure:"
    unzip -l "${{ github.workspace }}/${{ steps.information.outputs.name }}.zip" | head -20
```

**Commit**: [hash]

### 3. Documentation Updates

Created this document to explain the issue and fix for future reference.

---

## Verification

### How to Verify Zip Structure

```bash
# Download release zip
wget https://github.com/maximunited/imou_life/releases/download/v1.2.1/imou_life.zip

# Check structure
unzip -l imou_life.zip | head -20

# Should show:
__init__.py                 ← Files in root
manifest.json
battery_coordinator.py
...

# Should NOT show:
imou_life/                  ← No subdirectory
  __init__.py
  manifest.json
```

### How to Test HACS Installation

1. Create test directory structure:
```bash
mkdir -p custom_components/imou_life
cd custom_components/imou_life
```

2. Extract zip:
```bash
unzip imou_life.zip
```

3. Verify files are directly in `custom_components/imou_life/`:
```bash
ls -la
# Should see:
# __init__.py
# manifest.json
# etc.
```

---

## For Users Affected by v1.2.0

If you installed v1.2.0 via HACS and it created the wrong structure:

### Option 1: Reinstall (Recommended)

1. Remove the integration from HACS
2. Delete `custom_components/imou_life/` directory
3. Reinstall from HACS (will use v1.2.1+ with correct structure)
4. Restart Home Assistant

### Option 2: Manual Fix

1. Navigate to Home Assistant config directory
2. Move files up one level:
```bash
cd custom_components/imou_life
mv imou_life/* .
rmdir imou_life
```
3. Restart Home Assistant

### Option 3: Manual Installation

Download the correct zip and extract manually:

1. Download: https://github.com/maximunited/imou_life/releases/download/v1.2.1/imou_life.zip
2. Extract to `custom_components/imou_life/`
3. Restart Home Assistant

---

## Prevention

To prevent this issue in future releases:

### 1. Always Test Zip Structure

Before releasing, verify zip contents:
```bash
unzip -l imou_life.zip | head -20
```

Should see files directly, NOT in a subdirectory.

### 2. Test HACS-like Extraction

```bash
mkdir -p test/custom_components/imou_life
cd test/custom_components/imou_life
unzip ../../../imou_life.zip
ls -la  # Should see manifest.json here
```

### 3. CI/CD Validation

The release workflow now includes verification:
```yaml
echo "Verifying zip structure:"
unzip -l "${{ github.workspace }}/${{ steps.information.outputs.name }}.zip" | head -20
```

---

## HACS Configuration Reference

### Correct hacs.json for Integration

```json
{
  "name": "Imou Life",
  "render_readme": true,
  "homeassistant": "2023.8.0",
  "zip_release": true,
  "filename": "imou_life.zip",
  "hide_default_branch": true,
  "content_in_root": true,     ← Critical: files in zip root
  "hacs": "1.6.0"
}
```

### Key Settings Explained

- `"zip_release": true` - Use zip file from releases, not git checkout
- `"filename": "imou_life.zip"` - Name of zip file in release assets
- `"content_in_root": true` - **Files are directly in zip root, not in subdirectory**
- `"hide_default_branch": true` - Don't show master branch as option

### What NOT to Include

- ~~`"persistent_directory": "imou_life"`~~ - Not needed with content_in_root: true
- This setting confuses HACS when used with content_in_root: true

---

## References

- **HACS Documentation**: https://hacs.xyz/docs/publish/integration
- **Issue Report**: User reported wrong directory structure in v1.2.0
- **Fix Commits**: [To be filled in after merge]

---

## Testing Checklist

Before releasing a new version, verify:

- [ ] hacs.json has `"content_in_root": true`
- [ ] Release workflow creates zip with files in root
- [ ] Zip structure verified in workflow output
- [ ] Local test: extract zip to `custom_components/imou_life/`
- [ ] Verify `custom_components/imou_life/manifest.json` exists
- [ ] No nested `imou_life/imou_life/` directory created

---

**Status**: ✅ Fixed in v1.2.1
**Impact**: All HACS users installing v1.2.1+ will get correct structure
**Backward Compat**: Users must reinstall or manually fix v1.2.0 installations
