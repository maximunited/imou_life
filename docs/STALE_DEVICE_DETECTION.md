# Stale Device Detection

This document describes the stale device detection feature implemented to meet Home Assistant Gold tier quality scale requirements.

## Overview

Stale device detection automatically identifies when a device registered in Home Assistant no longer exists on the user's Imou account (e.g., device was deleted from Imou Life app) and prompts the user to remove it.

## How It Works

### Detection Flow

1. **Error Monitoring**: The coordinator monitors API errors during data updates
2. **Pattern Recognition**: Identifies "device not found" errors (distinct from auth/rate limit errors)
3. **Failure Threshold**: Requires 3 consecutive failures to avoid false positives
4. **Repair Issue**: Creates a repair issue in HA UI when threshold is reached
5. **User Action**: User chooses to Remove, Retry, or Ignore

### State Machine

```
NORMAL
  └─> "Device not found" error
      └─> SUSPECTED_STALE (count = 1)
          └─> Another "device not found" error
              └─> SUSPECTED_STALE (count = 2)
                  └─> Third "device not found" error
                      └─> CONFIRMED_STALE (count = 3)
                          └─> Repair issue created
```

### Error Differentiation

The system distinguishes between different error types:

| Error Type | Pattern | Action |
|------------|---------|--------|
| **Stale Device** | "device not found", "invalid device", "not authorized to operate on device" | Increment counter → repair issue after 3 |
| **Auth Failed** | "authentication failed", "token expired", "invalid app" | Trigger reauth flow immediately |
| **Rate Limit** | "OP1013", "exceed limit" | Adjust polling, continue normally |
| **Other** | Connection errors, timeouts | Log and retry |

### Why 3 Failures?

- **Prevents false positives**: Temporary API glitches won't trigger removal
- **Network resilience**: Brief connectivity issues are tolerated
- **User confidence**: Multiple failures indicate a real problem

## User Experience

### What the User Sees

1. **First failure**: Warning in logs (invisible to most users)
2. **Second failure**: Warning in logs
3. **Third failure**: Repair issue appears in Settings → System → Repairs

### Repair Issue Dialog

**Title**: "Device No Longer Available"

**Message**:
```
The device 'Camera Name' (ID: device_123) appears to no longer exist on your Imou account.

Error: Device not found

What would you like to do?
```

**Options**:
- **Remove device from Home Assistant**: Deletes the config entry permanently
- **Retry connection**: Resets failure counter and reloads integration (if device was re-added)
- **Ignore warning and continue**: Dismisses the warning, polling continues

## Implementation Details

### Files Modified

1. **`const.py`**: Added constants for threshold and error patterns
2. **`coordinator.py`**: Detection logic, failure tracking, event firing
3. **`__init__.py`**: Event listener and repair issue creation
4. **`config_flow.py`**: Repair flow step handler
5. **`sensor.py`**: API Status sensor shows stale device info
6. **`translations/en.json`**: User-facing strings

### Coordinator Tracking

The coordinator maintains these attributes:

```python
self.stale_device_suspected: bool = False
self.stale_device_failure_count: int = 0
self.stale_device_last_error: str | None = None
```

### API Status Sensor

The diagnostic sensor (disabled by default) exposes:

- `stale_device_suspected`: Boolean flag
- `stale_device_failure_count`: Current count
- `stale_device_last_error`: Last error message (if any)

## Testing

### Unit Tests

Location: `tests/unit/test_stale_device_detection.py`

**Coverage**:
- ✅ Pattern detection (stale vs auth vs rate limit)
- ✅ 3-failure threshold
- ✅ Counter reset on success
- ✅ Mixed error scenarios
- ✅ Error message formatting
- ✅ State transitions

**All 10 tests passing** ✅

### Manual Testing Checklist

To test this feature in a real environment:

1. **Setup**: Add a device to HA via the integration
2. **Trigger stale state**: Delete the device from Imou Life app
3. **Wait for failures**: Allow 3 polling cycles to occur (3 × scan interval)
4. **Verify repair issue**: Check Settings → System → Repairs
5. **Test "Remove"**: Choose Remove, verify config entry is deleted
6. **Test "Retry"**: Re-add device to Imou, choose Retry, verify recovery
7. **Test "Ignore"**: Choose Ignore, verify polling continues

### Mock Testing (for development)

```python
# Mock the API to return stale device error
device.async_get_data.side_effect = ImouException("Device not found")

# Trigger 3 updates
await coordinator._async_update_data()  # count = 1
await coordinator._async_update_data()  # count = 2
await coordinator._async_update_data()  # count = 3, repair issue created

# Verify state
assert coordinator.stale_device_suspected is True
assert coordinator.stale_device_failure_count == 3
```

## Edge Cases Handled

1. **False positives**: 3-failure threshold prevents temporary API glitches from triggering removal
2. **Device re-added**: Successful update automatically resets counter
3. **Multiple devices**: Each config entry has independent coordinator and tracking
4. **Rate limit during detection**: Rate limit errors don't increment stale device counter
5. **Auth errors**: Authentication failures trigger reauth flow, not stale detection
6. **Entry removed manually**: Event listener verifies entry exists before creating repair issue
7. **Successful recovery**: Counter resets to 0 when device responds successfully

## Configuration

No user configuration needed. The feature is automatic and uses these defaults:

- **Failure threshold**: 3 consecutive failures (defined in `const.py`)
- **Error patterns**: "device not found", "invalid device", "not authorized to operate on device"

## Logging

**Warning level** (visible in logs):
```
Device may no longer exist on account (failure 1/3): Device not found
Device may no longer exist on account (failure 2/3): Device not found
Device may no longer exist on account (failure 3/3): Device not found
Device 'Camera Name' (device_123) appears to no longer exist on account. Repair issue created for user action.
```

## Future Enhancements

### Orphaned Device Detection (Deferred)

A related but separate feature to detect devices with **zero entities**:

- **Scope**: Devices that exist in HA but have no entities registered
- **Different failure mode**: Setup/configuration issue vs device removed from cloud
- **Implementation approach**: Entity count check after platform setup
- **Similar repair flow**: Remove, Retry Setup, Ignore options
- **Estimated effort**: 1-2 hours (reuse repair flow pattern)

See `docs/ENHANCEMENT_ORPHANED_DEVICES.md` for detailed design.

## Gold Tier Compliance

This feature satisfies the Home Assistant Gold tier "stale-devices" requirement:

> **stale-devices**: The integration must be able to detect when a device is no longer available and remove it from Home Assistant.

**Implementation**:
- ✅ Detects device removal via API error patterns
- ✅ Provides user control via repair issue
- ✅ Automatic cleanup available (user-confirmed)
- ✅ No silent deletions (always requires user action)
- ✅ Comprehensive test coverage

## See Also

- [Home Assistant Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/)
- [Repair Flow Documentation](https://developers.home-assistant.io/docs/core/platform/repairs/)
- [DataUpdateCoordinator Pattern](https://developers.home-assistant.io/docs/integration_fetching_data/)
