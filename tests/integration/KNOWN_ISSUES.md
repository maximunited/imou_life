# Known Issues - Integration Tests

**Last Updated**: 2026-05-08
**Status**: ✅ **RESOLVED** - All integration tests passing

## Overview

All 25 integration tests are now passing (100% pass rate). This document is retained for historical reference.

## Historical Context

Previously (before 2026-04-29), 11 out of 19 integration tests were failing due to mocking/test infrastructure issues. These have all been resolved:

### Fixes Applied

1. **api_ok Fixture Issues** - Fixed in PR #36
   - Removed overly broad mocking that broke coordinator creation
   - Updated tests to use direct patching instead

2. **Config Flow Mocking** - Fixed in PR #36
   - Properly mocked ImouDiscoverService.async_discover_devices
   - Fixed flow context and user input format

3. **Error Handling Mocks** - Fixed in PR #36
   - Corrected exception chain setup
   - Properly simulated API connection failures

4. **Battery Optimization Methods** - Fixed in commit 99beaba
   - Added all required async methods to device mocks

5. **Missing async_refresh** - Fixed in PR #36
   - Added coordinator.async_refresh() calls where needed

6. **Multi-Device Discovery Tests** - Added in PR #XX
   - 5 new tests for automatic device discovery
   - All passing on first implementation

## Current Test Status

```bash
# Run integration tests:
python -m pytest tests/integration/ -v

# Results (as of 2026-05-08):
# - 25 collected
# - 25 passed ✓
# - 0 failed
# - Duration: ~3 seconds
```

### All Passing Tests (25) ✅

**Setup & Configuration (4 tests)**:
1. `test_full_setup_flow_with_discovery`
2. `test_full_setup_flow_manual_entry`
3. `test_setup_and_entity_state_updates`
4. `test_setup_reload_and_unload`

**Battery Optimization (9 tests)**:
5. `test_battery_coordinator_integration`
6. `test_battery_sleep_schedule_workflow`
7. `test_battery_based_sleep_activation`
8. `test_power_mode_changes_propagate`
9. `test_led_indicators_toggle`
10. `test_battery_optimization_status_retrieval`
11. `test_battery_data_caching`
12. `test_concurrent_sleep_mode_operations`

**Entity Interactions (7 tests)**:
13. `test_switch_entity_interaction`
14. `test_binary_sensor_state_changes`
15. `test_api_connection_failure_on_setup`
16. `test_coordinator_update_failure_recovery`
17. `test_multiple_devices_same_integration`
18. `test_config_entry_options_update`
19. `test_entity_availability_reflects_device_status`

**Multi-Device Discovery (5 tests)**:
20. `test_discovery_coordinator_created_for_first_entry_only`
21. `test_discovery_coordinator_uses_custom_interval`
22. `test_discovery_disabled_via_options`
23. `test_automatic_discovery_triggers_config_flow`
24. `test_discovery_transfer_on_first_entry_removal`
25. `test_discovery_stops_on_last_entry_removal`

## Quality Metrics

| Metric | Status |
|--------|--------|
| **Integration Tests** | 25/25 passing (100%) ✓ |
| **Unit Tests** | 446/446 passing (100%) ✓ |
| **Total Tests** | 471/471 passing (100%) ✓ |
| **Type Safety** | mypy clean (0 errors) ✓ |
| **Code Quality** | All pre-commit hooks passing ✓ |

## Related Documentation

- [Integration Test README](README.md) - Test organization and patterns
- [CHANGELOG.md](../../docs/CHANGELOG.md) - v1.6.0 test fixes documented
- [QUALITY_SCALE.md](../../docs/QUALITY_SCALE.md) - Platinum tier achievement

---

**Historical Note**: This file previously documented 11 failing tests. All issues were resolved in PR #36 and subsequent work. Retained for reference only.
