# Battery Optimization Code Review

## Executive Summary

The battery optimization feature is well-structured but has several critical issues that prevent it from being production-ready. Most concerning are the use of unittest.mock in production code and placeholder/commented-out API integrations.

**Overall Assessment**: 🟡 Framework is good, implementation needs work
**Test Coverage**: ✅ 72-85% (good)
**Production Ready**: ❌ No - contains mocks and incomplete integrations

---

## Critical Issues

### 1. ❌ unittest.mock in Production Code

**Files**: `battery_binary_sensor.py`, `battery_button.py`, `battery_select.py`

```python
# Lines 4 in all three files
from unittest.mock import AsyncMock, MagicMock
```

**Problem**: Test utilities imported in production code
**Impact**: Technical debt, confusing for developers, unprofessional
**Fix**: Remove mocks, create proper entity base class or use real device instances

**Recommendation**:
```python
# Instead of creating MagicMock sensor_instance, either:
# Option 1: Don't inherit from ImouEntity if it doesn't fit
# Option 2: Create a BatteryOptimizationEntity base class
# Option 3: Make ImouEntity more flexible with optional device parameter
```

---

### 2. ❌ Hardcoded Mock Data

**File**: `battery_binary_sensor.py:142`

```python
def _is_low_battery(self) -> bool:
    battery_level = 85  # Mock value
    return battery_level <= battery_threshold
```

**Problem**: Returns fake data, feature doesn't work
**Impact**: User sees incorrect battery status
**Fix**: Integrate with actual battery data from coordinator

---

### 3. ❌ Commented-Out API Calls

**File**: `battery_coordinator.py` (lines 278, 286, 305, 317, 330, 344)

```python
async def _enter_sleep_mode(self):
    _LOGGER.info("Entering sleep mode")
    # await self.device.async_enter_sleep_mode()  # <-- Not implemented
```

**Problem**: Feature is a skeleton, doesn't actually control device
**Impact**: Buttons and settings do nothing
**Fix**: Complete the imouapi integration or document as "planned feature"

---

## Logic Errors

### 4. 🐛 Sleep Schedule Logic is Backwards

**File**: `battery_coordinator.py:193-201`

```python
def _should_sleep_custom(self, current_time: time) -> bool:
    if self._sleep_start_time <= self._sleep_end_time:
        # Same day schedule (e.g., 10 PM to 6 AM)  <-- COMMENT IS WRONG
        return self._sleep_start_time <= current_time <= self._sleep_end_time
```

**Problem**:
- Comment says "10 PM to 6 AM" but that's overnight, not same-day
- Same-day would be "9 AM to 5 PM" (both times on same day)
- Logic is inverted

**Fix**:
```python
def _should_sleep_custom(self, current_time: time) -> bool:
    """Check if device should sleep during custom schedule."""
    if self._sleep_start_time <= self._sleep_end_time:
        # Same-day schedule (e.g., 9:00 to 17:00)
        return self._sleep_start_time <= current_time <= self._sleep_end_time
    else:
        # Overnight schedule (e.g., 22:00 to 06:00 next day)
        return current_time >= self._sleep_start_time or current_time <= self._sleep_end_time
```

---

### 5. 🐛 Night-Only Schedule Logic

**File**: `battery_coordinator.py:184-189`

```python
def _should_sleep_night_only(self, current_time: time) -> bool:
    """Check if device should sleep during night-only schedule."""
    return (
        current_time >= self._sleep_start_time
        or current_time <= self._sleep_end_time  # <-- OR is correct here
    )
```

**Status**: Actually this is CORRECT for overnight schedule
**Recommendation**: Rename to `_should_sleep_overnight` for clarity

---

## Design Issues

### 6. ⚠️ Hardcoded Hysteresis

**File**: `battery_coordinator.py:165`

```python
elif (
    battery_level > self._battery_threshold + 10  # <-- Hardcoded +10%
    and self._battery_optimization_active
):
```

**Problem**: Magic number, not configurable
**Recommendation**: Add `battery_hysteresis` config option (default: 10)

---

### 7. ⚠️ Type Hint Error

**File**: `battery_coordinator.py:388`

```python
def get_battery_optimization_status(self) -> Dict[str, str]:  # <-- Wrong!
    return {
        "active": self._battery_optimization_active,  # bool
        "battery_threshold": self._battery_threshold,  # int
        ...
    }
```

**Fix**:
```python
def get_battery_optimization_status(self) -> Dict[str, Any]:
```

---

### 8. ⚠️ Method Visibility Issues

**Problem**: Private methods (`_enter_sleep_mode`) called from other classes
**Files**: Coordinator has `_is_sleep_mode_active` called from binary_sensor

**Recommendation**: Make public methods that are part of the coordinator's API:
```python
# Public API methods (no underscore)
async def enter_sleep_mode(self)
async def exit_sleep_mode(self)
def is_sleep_mode_active(self) -> bool
```

---

## Code Quality Issues

### 9. 📦 Excessive hasattr Checks

**Files**: All battery entity files

```python
if hasattr(self.coordinator, "get_battery_optimization_status"):
    status = self.coordinator.get_battery_optimization_status()
```

**Problem**: Coordinator should have a defined interface
**Recommendation**:
- Define a `BatteryOptimizationCoordinator` protocol/ABC
- Remove hasattr checks
- Let it fail fast if coordinator doesn't support battery features

---

### 10. 🔄 Code Duplication

**Problem**: Entity initialization is nearly identical across all three battery entity files

**Recommendation**: Extract to a base class
```python
class ImouBatteryEntity(ImouEntity):
    """Base class for battery optimization entities."""

    def __init__(self, coordinator, config_entry, entity_type: str,
                 description: str, icon: str, attribute_name: str):
        # Create proper entity without mocks
        super().__init__(coordinator, config_entry, platform=entity_type)
        self._description = description
        self._icon = icon
        self._attribute_name = attribute_name

    @property
    def name(self) -> str:
        return f"{self.coordinator.device.get_name()} {self._description}"

    @property
    def icon(self) -> str:
        return self._icon
```

---

### 11. ⚠️ Error Handling

**Problem**: Broad exception catching, some silent failures

```python
except Exception as exception:  # Too broad
    return False  # Silent failure
```

**Recommendation**:
```python
except (AttributeError, ValueError, KeyError) as exception:
    _LOGGER.warning("Failed to get battery state: %s", exception)
    return False
except Exception as exception:
    _LOGGER.error("Unexpected error in battery status: %s", exception, exc_info=True)
    raise
```

---

## Performance Issues

### 12. ⚡ Potential Race Conditions

**File**: `battery_coordinator.py`

**Problem**: No locking around state changes
```python
self._battery_optimization_active = True  # Multiple async methods modify this
```

**Recommendation**: Add asyncio.Lock for state mutations
```python
self._optimization_lock = asyncio.Lock()

async def _activate_battery_optimization(self):
    async with self._optimization_lock:
        # ... state changes
```

---

### 13. ⚡ Unnecessary API Calls

**File**: `battery_coordinator.py:203-207`

```python
async def _should_sleep_battery_based(self) -> bool:
    battery_data = await self._get_battery_data()  # <-- Extra API call
    battery_level = battery_data.get("level", 100)
    return battery_level <= self._battery_threshold
```

**Problem**: Called during every update cycle, makes redundant API call
**Recommendation**: Use cached data from last update
```python
async def _should_sleep_battery_based(self) -> bool:
    # Use cached battery level from coordinator.data
    battery_level = self.data.get("battery_level", 100) if self.data else 100
    return battery_level <= self._battery_threshold
```

---

## Recommendations Summary

### Immediate (Before Production)

1. ❌ **Remove unittest.mock imports** - refactor entity initialization
2. ❌ **Complete API integration** or mark as experimental/stub
3. ❌ **Remove hardcoded mock data** - use real battery values
4. 🐛 **Fix sleep schedule comment** - update to match logic

### Short-term (Next Sprint)

5. ⚠️ **Add battery_hysteresis config option**
6. ⚠️ **Fix type hints** - Dict[str, Any]
7. ⚠️ **Make API methods public** - remove underscores where needed
8. 📦 **Extract base battery entity class** - reduce duplication
9. ⚡ **Add state locking** - prevent race conditions
10. ⚡ **Use cached battery data** - avoid redundant API calls

### Long-term (Nice to Have)

11. 📦 **Define coordinator protocol/interface** - remove hasattr checks
12. ⚠️ **Improve error handling** - specific exceptions, better logging
13. 📝 **Add docstring examples** - show expected behavior
14. 🧪 **Integration tests** - test with real device mock

---

## Positive Aspects ✅

1. **Well-structured** - clear separation of concerns
2. **Good test coverage** - 72-85% for battery modules
3. **Extensible design** - easy to add new optimization features
4. **Comprehensive features** - sleep schedules, power modes, sensitivity control
5. **Good logging** - appropriate log levels throughout
6. **Config-driven** - stores settings in config entry

---

## Overall Rating

| Category | Score | Notes |
|----------|-------|-------|
| Architecture | 8/10 | Well-designed but uses mocks improperly |
| Code Quality | 6/10 | Several logic errors and bad practices |
| Test Coverage | 8/10 | Good coverage but tests fake behavior |
| Documentation | 7/10 | Good comments but some are misleading |
| Production Ready | 3/10 | Not functional without API integration |

**Recommendation**: Complete the imouapi integration before marking as production-ready. The framework is solid but the implementation is incomplete.
