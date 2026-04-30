# Quality Scale Roadmap

This document outlines the path from Bronze tier to Platinum tier compliance for the Imou Life integration.

## Current Status

**Tier**: Bronze (79% complete)
- **Bronze**: 15/19 ✅ (79%)
- **Silver**: 5/10 ✅ (50%)
- **Gold**: 7/23 ✅ (30%)
- **Platinum**: 0/3 ✅ (0%, 2 exempt)

**Overall**: 27/55 requirements met (49%)

---

## 🥉 Bronze Tier (15/19 complete)

**Goal**: Baseline quality - functional integration with proper setup and documentation.

### ✅ Completed (15 requirements)

1. **action-setup** - Services registered in platform setup
2. **appropriate-polling** - 15min default, configurable
3. **common-modules** - Shared entity/mixin/setup modules
4. **config-flow** - UI-based setup
5. **config-flow-test-coverage** - 10 config flow tests
6. **dependency-transparency** - Python dependencies documented
7. **docs-actions** - Service documentation (SERVICES.md)
8. **docs-high-level-description** - README overview
9. **docs-installation-instructions** - INSTALLATION.md
10. **docs-removal-instructions** - UNINSTALL.md
11. **entity-unique-id** - All entities have unique IDs
12. **test-before-configure** - Credential validation in config flow
13. **test-before-setup** - Integration initialization validation
14. **unique-config-entry** - Duplicate device prevention
15. **config-entry-unloading** - Clean unload implementation

### ⚠️ TODO (4 requirements)

#### 1. brands (Low Priority)
**Requirement**: Branding assets must be provided.

**Tasks**:
- Create logo (256x256 PNG)
- Create icon (256x256 PNG)
- Add to `custom_components/imou_life/`
- Follow [Home Assistant Brand Guidelines](https://developers.home-assistant.io/docs/creating_integration_brand_guidelines)

**Effort**: 1-2 hours (design work)

#### 2. entity-event-setup (Medium Priority)
**Requirement**: Entity events must be properly set up.

**Tasks**:
- Audit all entity types for event setup
- Verify binary sensors fire events correctly
- Add event tests if needed

**Effort**: 2-4 hours (audit + testing)

#### 3. has-entity-name ⚡ CRITICAL
**Requirement**: Entities must use `has_entity_name = True`.

**Current State**: Entities use legacy naming pattern
```python
@property
def name(self):
    return f"{self.device.get_name()} {self.sensor_instance.get_description()}"
```

**Target State**:
```python
_attr_has_entity_name = True

@property
def name(self):
    return self.sensor_instance.get_description()
```

**Tasks**:
1. Add `_attr_has_entity_name = True` to `ImouEntity` base class
2. Update `name` property to return sensor description only
3. Verify all entity names render correctly in UI
4. Enable test in `test_bronze_tier_compliance.py`

**Impact**: Breaking change for existing installations (entity IDs will change)

**Migration Strategy**:
- Add to manifest.json: `"entity_namespace": true`
- Document migration in CHANGELOG
- Bump version to 2.0.0

**Effort**: 4-6 hours (implementation + testing + migration guide)

#### 4. runtime-data ⚡ CRITICAL
**Requirement**: Use `entry.runtime_data` instead of `hass.data[DOMAIN]`.

**Current Pattern** (`__init__.py`):
```python
hass.data.setdefault(DOMAIN, {})
hass.data[DOMAIN][entry.entry_id] = coordinator
```

**Target Pattern**:
```python
entry.runtime_data = coordinator
```

**Files to Update**:
- `custom_components/imou_life/__init__.py`
- `custom_components/imou_life/camera.py`
- `custom_components/imou_life/sensor.py`
- `custom_components/imou_life/binary_sensor.py`
- `custom_components/imou_life/switch.py`
- `custom_components/imou_life/select.py`
- `custom_components/imou_life/button.py`
- `custom_components/imou_life/siren.py`
- All battery-specific platform files

**Tasks**:
1. Update `async_setup_entry` to use `entry.runtime_data`
2. Update `async_unload_entry` to clear `entry.runtime_data`
3. Update all platform `async_setup_entry` functions
4. Update tests to mock `entry.runtime_data`
5. Remove `hass.data[DOMAIN]` usage

**Effort**: 6-8 hours (global change across all platforms + testing)

### Bronze Completion Timeline

**Estimated Total Effort**: 13-20 hours

**Recommended Order**:
1. runtime-data (6-8h) - Critical, affects all platforms
2. has-entity-name (4-6h) - Critical, breaking change
3. entity-event-setup (2-4h) - Medium priority
4. brands (1-2h) - Can be done last

**Target**: Version 2.0.0

---

## 🥈 Silver Tier (5/10 complete)

**Goal**: Stable user experience - reliable error handling, reauth, logging.

### ✅ Completed (5 requirements)

1. **config-entry-unloading** - Integration can be unloaded
2. **docs-configuration-parameters** - CONFIGURATION.md exists
3. **docs-installation-parameters** - INSTALLATION.md exists
4. **entity-unavailable** - Sets unavailable when offline
5. **integration-owner** - CODEOWNERS file exists

### ⚠️ TODO (5 requirements)

#### 1. action-exceptions
**Requirement**: Service calls must handle exceptions properly.

**Tasks**:
- Audit all service handlers for exception handling
- Add try/except blocks with proper error messages
- Test exception scenarios

**Effort**: 4-6 hours

#### 2. log-when-unavailable
**Requirement**: Log when devices become unavailable.

**Tasks**:
- Add logging in entity `available` property changes
- Log device offline events
- Add rate limiting to prevent log spam

**Effort**: 2-3 hours

#### 3. parallel-updates
**Requirement**: Platform updates must specify `PARALLEL_UPDATES`.

**Tasks**:
- Add `PARALLEL_UPDATES = 1` to all platform files
- Document why (API rate limits)
- Test with multiple devices

**Effort**: 1-2 hours

#### 4. reauthentication-flow ⚡ HIGH PRIORITY
**Requirement**: Handle expired credentials with reauth flow.

**Tasks**:
- Add `async_step_reauth` to config flow
- Detect authentication errors in coordinator
- Trigger reauth flow on auth failure
- Add reauth tests

**Current**: Authentication errors require manual reconfiguration

**Effort**: 6-8 hours

#### 5. test-coverage
**Requirement**: Maintain >95% test coverage.

**Current**: ~70% coverage (241 tests)

**Tasks**:
- Identify uncovered code paths
- Add tests for edge cases
- Add integration tests for complex flows
- Configure coverage enforcement in CI

**Effort**: 10-15 hours

### Silver Completion Timeline

**Estimated Total Effort**: 23-34 hours

**Target**: Version 2.1.0

---

## 🥇 Gold Tier (7/23 complete)

**Goal**: Comprehensive support - diagnostics, translations, advanced features.

### ✅ Completed (7 requirements)

1. **devices** - Creates device entries
2. **diagnostics** - Diagnostics implemented
3. **discovery** - Device discovery in config flow
4. **docs-troubleshooting** - PERFORMANCE_TROUBLESHOOTING.md
5. **entity-category** - Diagnostic sensors use category
6. **entity-translations** - 8 languages supported
7. **icon-translations** - icons.json added

### ⚠️ TODO (16 requirements)

**High Priority**:
- **dynamic-devices** - Add devices after initial setup (6-8h)
- **reconfiguration-flow** - Modify config without removal (4-6h)
- **entity-device-class** - Proper device classes for all entities (3-4h)
- **entity-disabled-by-default** - Diagnostic entities disabled by default (2-3h)

**Medium Priority**:
- **docs-supported-devices** - Device compatibility list (4-6h)
- **docs-supported-functions** - Entity documentation (4-6h)
- **docs-known-limitations** - Limitations documentation (2-3h)
- **docs-examples** - Automation examples (3-4h)
- **docs-use-cases** - Use case examples (2-3h)

**Low Priority**:
- **discovery-update-info** - Update device info from discovery (2-3h)
- **docs-data-update** - Document update mechanisms (2-3h)
- **exception-translations** - Translate exception messages (3-4h)
- **repair-issues** - Repair flows for common issues (6-8h)
- **stale-devices** - Clean up stale devices (3-4h)

### Gold Completion Timeline

**Estimated Total Effort**: 52-73 hours

**Target**: Version 2.5.0

---

## 🏆 Platinum Tier (0/3, 2 exempt)

**Goal**: Technical excellence - async, type safety, modern patterns.

### ⚠️ Exempt (2 requirements)

#### 1. async-dependency
**Requirement**: Use async libraries for I/O.

**Status**: **EXEMPT** - Library limitation

**Reason**: The `imouapi` library (1.0.15) is synchronous. Migration would require:
- Switching to `pyimouapi` (different API, 1.2.2)
- Wrapping all calls in executor
- Complete rewrite of API integration

**Alternative**: Monitor `imouapi` for async support

#### 2. inject-websession
**Requirement**: Use Home Assistant's aiohttp session.

**Status**: **EXEMPT** - Library limitation

**Reason**: The `imouapi` library doesn't accept `aiohttp.ClientSession` parameter. This is a library design limitation.

**Alternative**: Submit PR to imouapi library

### ⚠️ TODO (1 requirement)

#### 1. strict-typing
**Requirement**: Full type coverage with strict mypy.

**Current**: Type hints exist but not strict mode

**Tasks**:
1. Enable strict mode in `pyproject.toml`:
   ```toml
   [tool.mypy]
   strict = true
   ```
2. Fix all type errors revealed by strict mode
3. Add return type annotations to all functions
4. Type all function parameters
5. Handle Optional types properly
6. Configure mypy in pre-commit hooks

**Estimated Errors**: 100-200 type issues to fix

**Effort**: 15-20 hours

### Platinum Completion Timeline

**Estimated Total Effort**: 15-20 hours

**Target**: Version 3.0.0

**Note**: Platinum requires all lower tiers complete

---

## Migration Strategy

### Version Numbering

- **v1.x.x**: Current (Bronze incomplete)
- **v2.0.0**: Bronze complete (breaking: has-entity-name, runtime-data)
- **v2.1.0**: Silver complete
- **v2.5.0**: Gold complete
- **v3.0.0**: Platinum complete

### Breaking Changes

**v2.0.0** will include breaking changes:
- Entity IDs will change due to `has_entity_name = True`
- Migration guide required
- CHANGELOG entry required

**Migration Guide Required**:
```markdown
## Breaking Changes in v2.0.0

### Entity Naming Changes

Entity IDs have changed to follow Home Assistant naming standards:

**Before**: `sensor.living_room_camera_storage_used`
**After**: `sensor.living_room_camera_storage_used` (device name + entity name)

The format remains similar, but the underlying implementation now uses
`has_entity_name = True` which is required for Bronze tier compliance.

### Action Required

1. Update automations that reference entity IDs
2. Update dashboards
3. Update scripts and templates

Most setups will not require changes as entity IDs remain stable.
```

---

## Overall Timeline

### Conservative Estimates

**Bronze Completion**: 13-20 hours (v2.0.0)
**Silver Completion**: 23-34 hours (v2.1.0)
**Gold Completion**: 52-73 hours (v2.5.0)
**Platinum Completion**: 15-20 hours (v3.0.0)

**Total**: 103-147 hours

### Aggressive Timeline

Working 10 hours per week:
- **Bronze**: 2-3 weeks
- **Silver**: 3-4 weeks
- **Gold**: 6-8 weeks
- **Platinum**: 2-3 weeks

**Total**: 13-18 weeks (~3-4 months)

### Realistic Timeline

Working 5 hours per week:
- **Bronze**: 3-4 weeks
- **Silver**: 5-7 weeks
- **Gold**: 10-15 weeks
- **Platinum**: 3-4 weeks

**Total**: 21-30 weeks (~5-7 months)

---

## Prioritization Matrix

### Critical (Must Have for Bronze)
1. runtime-data (8h)
2. has-entity-name (6h)

### High Priority (Silver Requirements)
3. reauthentication-flow (8h)
4. test-coverage (15h)
5. action-exceptions (6h)

### Medium Priority (Gold Quick Wins)
6. entity-device-class (4h)
7. entity-disabled-by-default (3h)
8. dynamic-devices (8h)

### Low Priority (Documentation & Polish)
9. All docs-* requirements (20h)
10. Branding (2h)

---

## Success Metrics

### Bronze
- ✅ 19/19 requirements met
- ✅ All compliance tests passing
- ✅ No breaking issues in migration

### Silver
- ✅ Reauth flow working
- ✅ 95%+ test coverage
- ✅ Clean logs (no spam)

### Gold
- ✅ Dynamic device addition
- ✅ Reconfiguration without removal
- ✅ Comprehensive documentation

### Platinum
- ✅ Zero mypy errors in strict mode
- ✅ Full type coverage
- ✅ Modern HA patterns

---

## Resources

- [Official Quality Scale Rules](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/)
- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Integration Examples](https://github.com/home-assistant/core/tree/dev/homeassistant/components)
- [Quality Scale Analysis](QUALITY_SCALE_ANALYSIS.md)
- [Bronze Tier Completion](BRONZE_TIER_COMPLETION.md)

---

## Next Actions

1. **Immediate** (v2.0.0):
   - Implement runtime-data migration
   - Implement has-entity-name with migration guide
   - Test thoroughly
   - Release v2.0.0

2. **Short Term** (v2.1.0):
   - Implement reauthentication flow
   - Increase test coverage to 95%+
   - Add parallel-updates to platforms

3. **Medium Term** (v2.5.0):
   - Add dynamic device support
   - Implement reconfiguration flow
   - Complete documentation requirements

4. **Long Term** (v3.0.0):
   - Enable strict typing
   - Fix all type errors
   - Achieve Platinum compliance
