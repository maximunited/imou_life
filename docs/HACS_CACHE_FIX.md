# HACS Cache Fix for v1.2.1/v1.2.2

## Problem
When trying to install v1.2.1 or v1.2.2 from HACS, you get:
```
No manifest.json file found 'manifest.json'
```

## Root Cause
HACS caches the `hacs.json` configuration from the repository. Version 1.2.0 had incorrect HACS configuration (`content_in_root: false`), which told HACS to look for files in a subdirectory. Even though v1.2.1+ has the correct configuration (`content_in_root: true`), HACS may still be using the old cached settings.

## Solution

### Option 1: Clear HACS Cache (Recommended)

1. **Remove the integration from HACS:**
   - Go to HACS > Integrations
   - Find "Imou Life"
   - Click the three dots menu
   - Select "Remove"

2. **Clear Home Assistant cache** (optional but recommended):
   - Restart Home Assistant completely
   - This ensures all caches are cleared

3. **Re-add the integration:**
   - Go to HACS > Integrations
   - Click "+ Explore & Download Repositories"
   - Search for "Imou Life"
   - Download v1.2.2 (or later)

### Option 2: Manual Installation

If HACS continues to have issues, install manually:

1. **Download the zip:**
   ```bash
   wget https://github.com/maximunited/imou_life/releases/download/v1.2.2/imou_life.zip
   ```

2. **Extract to custom_components:**
   ```bash
   cd /config/custom_components
   mkdir -p imou_life
   unzip -o imou_life.zip -d imou_life/
   ```

3. **Verify structure:**
   ```bash
   ls imou_life/manifest.json
   # Should exist directly in imou_life/ directory
   ```

4. **Restart Home Assistant**

### Option 3: Wait for HACS Cache Expiry

HACS caches repository metadata for ~24 hours. If you can wait, the cache will expire and HACS will fetch the new configuration automatically.

## Verification

After installation, verify the structure is correct:

```bash
ls -la /config/custom_components/imou_life/
```

You should see:
```
custom_components/
+-- imou_life/
    +-- __init__.py
    +-- manifest.json  ? Should be here (not in a subdirectory!)
    +-- config_flow.py
    +-- ...
```

**NOT** like this (old broken structure):
```
custom_components/
+-- imou_life/
    +-- imou_life/  ? NO! This is wrong
        +-- __init__.py
        +-- manifest.json
        +-- ...
```

## Still Not Working?

If you still get errors:

1. **Check HACS version:** Make sure you're running HACS 1.6.0 or later
2. **Check for multiple installations:** Remove any duplicate `imou_life` directories
3. **Check file permissions:** Ensure Home Assistant can read the files
4. **Open an issue:** https://github.com/maximunited/imou_life/issues with:
   - HACS version
   - Home Assistant version
   - Error messages from logs
   - Output of `ls -la /config/custom_components/imou_life/`

## Technical Details

The fix involved:
- **hacs.json**: Changed `"content_in_root": false` ? `"content_in_root": true`
- **Release workflow**: Fixed zip creation to put files in root
- Both v1.2.1 and v1.2.2 have correct zip structure verified

See [HACS_INSTALLATION_FIX.md](HACS_INSTALLATION_FIX.md) for full technical details.
