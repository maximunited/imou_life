# Cleaning Up Orphaned Devices After v1.3.6 Update

## Problem

After upgrading to v1.3.6, the API Status sensor moved to the main device, but the old duplicate device (with 0 or 1 entities) remains visible.

## Solution

### Method 1: Delete via Home Assistant UI

1. Go to **Settings** → **Devices & Services** → **Devices**
2. Search for your device name
3. You'll see 2 devices:
   - Device with **23 entities** ✅ (keep this)
   - Device with **0-1 entities** ❌ (delete this)
4. Click the orphaned device
5. Click **⋮** (menu) → **Delete**

### Method 2: Via Home Assistant Developer Tools

1. Go to **Developer Tools** → **Services**
2. Use service: `homeassistant.remove_orphaned_entities`
3. Call the service
4. Restart Home Assistant

### Method 3: Via Configuration YAML

1. Stop Home Assistant
2. Edit `.storage/core.device_registry`
3. Find the orphaned device entry (search for your device ID)
4. Remove the orphaned device JSON block
5. Save and restart Home Assistant

**⚠️ Warning:** Method 3 is advanced and can corrupt your device registry if done incorrectly.

### Method 4: Remove and Re-add Integration (Nuclear Option)

If nothing else works:

1. **Settings** → **Devices & Services** → **Imou Life**
2. Click **⋮** → **Delete**
3. Restart Home Assistant
4. Re-add the integration
5. Only 1 device will be created with all 23 entities

## Verification

After cleanup, verify:
- Only **1 device** for your camera
- Device has **23 entities** total
- API Status sensor is present in the entity list

## Prevention

This was a one-time issue caused by the device identifier change in v1.3.6. Future updates won't create duplicate devices.
