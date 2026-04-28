# Critical Issues Report

Generated: 2026-04-29

## Summary

Found **5 critical issues** that need immediate attention:
- 2 Exception Handling Issues (loss of error context)
- 1 Input Validation Issue (unhandled ValueError)
- 1 Security Issue (hardcoded credentials)
- 1 Error Type Issue (generic exception)

---

## Critical Issues

### 1. ❌ Exception Re-raised Without Context (`__init__.py:164`)

**Severity**: High  
**Type**: Exception Handling  
**Location**: `custom_components/imou_life/__init__.py` line 164

**Current Code**:
```python
except ImouException as exception:
    _LOGGER.error("Imou exception: %s", str(exception))
    raise ImouException() from exception  # ❌ Creates new exception without args
```

**Problem**:
- Creates a NEW `ImouException()` without any error message or context
- Loses the original exception's error message and details
- Makes debugging extremely difficult
- Users see an empty error message

**Fix**:
```python
except ImouException as exception:
    _LOGGER.error("Imou exception: %s", str(exception))
    raise  # ✅ Re-raises original exception with full context
```

**Impact**: Users cannot diagnose device initialization failures due to missing error information.

---

### 2. ❌ UpdateFailed Raised Without Error Message (`coordinator.py:46`)

**Severity**: High  
**Type**: Exception Handling  
**Location**: `custom_components/imou_life/coordinator.py` line 46

**Current Code**:
```python
except ImouException as exception:
    _LOGGER.error("Imou exception: %s", str(exception))
    raise UpdateFailed() from exception  # ❌ No error message
```

**Problem**:
- Creates `UpdateFailed()` without passing the error message
- Home Assistant logs show generic "Update failed" without specific reason
- Users cannot determine why data fetching failed

**Fix**:
```python
except ImouException as exception:
    error_msg = f"Imou API error: {str(exception)}"
    _LOGGER.error(error_msg)
    raise UpdateFailed(error_msg) from exception  # ✅ Include error message
```

**Impact**: Users cannot diagnose why device updates are failing.

---

### 3. ❌ Unhandled ValueError in Type Conversion (`__init__.py:117`)

**Severity**: High  
**Type**: Input Validation  
**Location**: `custom_components/imou_life/__init__.py` line 117

**Current Code**:
```python
def _parse_timeout_option(timeout_value):
    """Parse timeout option value safely."""
    if isinstance(timeout_value, str):
        return None if timeout_value == "" else int(timeout_value)  # ❌ Can raise ValueError
    return timeout_value
```

**Problem**:
- `int(timeout_value)` can raise `ValueError` if the string is not a valid integer
- No try/except block to handle the error
- Will crash during setup if user provides invalid timeout value
- Function claims to parse "safely" but doesn't handle errors

**Fix**:
```python
def _parse_timeout_option(timeout_value):
    """Parse timeout option value safely."""
    if isinstance(timeout_value, str):
        if timeout_value == "":
            return None
        try:
            return int(timeout_value)
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid timeout value: %s, using default", timeout_value)
            return None
    return timeout_value
```

**Impact**: Integration setup crashes if user provides invalid timeout configuration.

---

### 4. 🔒 Hardcoded Credentials in Fallback Code (`camera.py:169-172`)

**Severity**: **CRITICAL**  
**Type**: Security  
**Location**: `custom_components/imou_life/camera.py` lines 169-172

**Current Code**:
```python
except imouapi.exceptions.APIError as e:
    _LOGGER.warning("API stream failed, falling back to local RTSP: %s", str(e))
    return (
        "rtsp://admin:yourpassword@192.168.1.100:554/cam/realmonitor"  # 🔒 HARDCODED
        "?channel=1&subtype=0"
    )
```

**Problem**:
- **HARDCODED PASSWORD** in source code (`yourpassword`)
- Hardcoded username (`admin`)
- Hardcoded IP address (`192.168.1.100`)
- This is clearly example/placeholder code that should never have made it to production
- If this fallback is ever used, it will fail AND expose credentials in logs
- Violates security best practices

**Fix Options**:

**Option 1 - Remove fallback (recommended)**:
```python
except imouapi.exceptions.APIError as e:
    _LOGGER.error("Failed to get stream URL: %s", str(e))
    raise  # Let Home Assistant handle the error
```

**Option 2 - Use configurable fallback**:
```python
except imouapi.exceptions.APIError as e:
    _LOGGER.error("Failed to get stream URL: %s", str(e))
    # Check for user-configured fallback URL
    fallback_url = self._config_entry.options.get("rtsp_fallback_url")
    if fallback_url:
        _LOGGER.warning("Using configured fallback RTSP URL")
        return fallback_url
    raise  # No fallback available
```

**Impact**: 
- **Security vulnerability** if the fallback code is ever triggered
- **Privacy concern** - hardcoded credentials in open source code
- **Functionality issue** - the fallback will never work with example credentials

**Recommendation**: Remove the fallback entirely. If it's needed, implement it properly with user-configurable settings.

---

### 5. ❌ Generic Exception Raised (`switch.py:89`)

**Severity**: Medium  
**Type**: Error Handling  
**Location**: `custom_components/imou_life/switch.py` line 89

**Current Code**:
```python
if callback_url is None:
    raise Exception("No callback url provided")  # ❌ Generic exception
```

**Problem**:
- Raises generic `Exception` instead of a specific exception type
- Makes error handling difficult for callers
- Violates Python best practices
- Harder to catch specific errors

**Fix**:
```python
if callback_url is None:
    raise ValueError("No callback URL provided for push notifications")  # ✅ Specific exception
```

or create a custom exception:
```python
class ConfigurationError(Exception):
    """Raised when required configuration is missing."""
    pass

if callback_url is None:
    raise ConfigurationError("No callback URL provided for push notifications")
```

**Impact**: Error handling is less precise, makes debugging harder.

---

## Additional Observations (Not Critical)

### Good Practices Found:
✅ Diagnostics properly redacts sensitive data (app_id, app_secret, access_token)  
✅ Type conversions in config_flow.py have proper try/except blocks  
✅ Timeout protection on async operations  
✅ Proper use of Home Assistant's session management  

### Recommendations:
1. Add comprehensive input validation for all user-provided configuration
2. Consider adding custom exception classes for better error categorization
3. Add unit tests specifically for error handling paths
4. Review all exception handling to ensure context is preserved

---

## Priority for Fixes

1. **IMMEDIATE** - Issue #4: Remove hardcoded credentials
2. **HIGH** - Issue #1 & #2: Fix exception handling to preserve error context
3. **HIGH** - Issue #3: Add input validation for timeout parsing
4. **MEDIUM** - Issue #5: Use specific exception types

---

## Testing Recommendations

After fixes:
1. Test device initialization with invalid credentials
2. Test coordinator updates with API failures
3. Test configuration with invalid timeout values
4. Test camera streaming with API failures
5. Test push notification switches without callback URL
