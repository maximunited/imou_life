# Uninstalling Imou Life

This guide explains how to remove the Imou Life integration from your Home Assistant installation.

## Method 1: Remove via Home Assistant UI (Recommended)

1. Navigate to **Settings** → **Devices & Services**
2. Find **Imou Life** in the list of integrations
3. Click the three dots menu (⋮) next to the integration
4. Select **Delete**
5. Confirm the removal

This will:
- Remove all devices and entities created by the integration
- Delete the configuration entry
- Clean up integration data

## Method 2: Manual Removal

If the UI method doesn't work or the integration is misbehaving:

### Step 1: Remove Integration Data

1. Stop Home Assistant
2. Navigate to your Home Assistant configuration directory
3. Remove the integration from `.storage/core.config_entries`:
   - Open the file in a text editor
   - Find and remove the entry with `"domain": "imou_life"`
   - Save the file

### Step 2: Remove Entity Registry Entries

1. Open `.storage/core.entity_registry`
2. Remove all entries where `"platform": "imou_life"`
3. Save the file

### Step 3: Remove Device Registry Entries

1. Open `.storage/core.device_registry`
2. Remove all entries where `"imou_life"` appears in identifiers
3. Save the file

### Step 4: Remove Integration Files

**HACS Installation:**
1. Navigate to **HACS** → **Integrations**
2. Find **Imou Life**
3. Click the three dots menu (⋮)
4. Select **Remove**
5. Restart Home Assistant

**Manual Installation:**
1. Navigate to `custom_components/` in your config directory
2. Delete the `imou_life/` folder
3. Restart Home Assistant

## Cleanup After Removal

After uninstalling, you may want to:

1. **Remove unused entities from dashboards**
   - Edit your Lovelace dashboards
   - Remove cards referencing Imou devices

2. **Clean up automations**
   - Check automations that used Imou entities
   - Update or remove them

3. **Remove any custom templates or scripts**
   - Search for references to `imou_life` in your configuration

## Troubleshooting

### Integration won't delete from UI

If you get an error when trying to delete:

1. Check Home Assistant logs for specific error messages
2. Try restarting Home Assistant first, then delete
3. Use Manual Removal method above

### Entities still appear after removal

1. Clear browser cache
2. Restart Home Assistant
3. Check `.storage/core.entity_registry` for orphaned entries

### "Integration is being used" error

This means the integration is referenced in:
- Automations
- Scripts
- Scenes
- Dashboard cards
- Templates

Remove these references first, then try uninstalling again.

## Re-installation

If you want to reinstall the integration:

1. Complete the uninstall steps above
2. Restart Home Assistant
3. Follow the [Installation Guide](INSTALLATION.md)
4. Reconfigure with your App ID and App Secret

## Data Retention

**What gets deleted:**
- Device and entity configurations
- Integration settings
- Entity states

**What is NOT deleted:**
- Historical data in the database (entity states over time)
- Lovelace dashboard configurations
- Automations and scripts

To remove historical data, use Home Assistant's database purge features.

## Need Help?

- **Issues**: https://github.com/maximunited/imou_life/issues
- **Discussions**: https://github.com/maximunited/imou_life/discussions
- **Documentation**: https://github.com/maximunited/imou_life
