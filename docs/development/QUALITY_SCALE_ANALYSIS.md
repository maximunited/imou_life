# Quality Scale Analysis

## Current Status: **NOT Platinum** ⚠️

Our `quality_scale.yaml` claims "Platinum" but uses outdated/generic rule names. The official Home Assistant quality scale has 55 specific rules that must be tracked.

## Official Quality Scale Requirements

**Total Rules: 55**
- 🥉 Bronze: 19 rules
- 🥈 Silver: 10 rules
- 🥇 Gold: 23 rules
- 🏆 Platinum: 3 rules

## Our Current quality_scale.yaml

We have only **12 generic categories** listed:

```yaml
# Bronze
config_flow: done
tests: done
codeowners: done

# Silver
error_recovery: done
offline_handling: done
logging: done
troubleshooting_docs: done

# Gold
device_discovery: done
entity_naming: done
translations: done
comprehensive_docs: done
test_coverage: done
firmware_updates: exempt

# Platinum
type_annotations: done
async_code: done
performance: done
```

**Problem**: These are NOT the official rule names. We need to map against the 55 specific rules.

## Detailed Rule Analysis

### 🥉 Bronze Tier (19 rules)

| Rule | Status | Notes |
|------|--------|-------|
| action-setup | ❓ Unknown | Need to verify services registered in async_setup |
| appropriate-polling | ✅ Likely | Default 15min, configurable |
| brands | ❓ Unknown | Do we have branding assets? |
| common-modules | ✅ Yes | entity.py, entity_mixins.py, platform_setup.py |
| config-flow-test-coverage | ✅ Yes | 10/10 tests passing |
| config-flow | ✅ Yes | UI-based setup |
| dependency-transparency | ❓ Unknown | Need to check docs |
| docs-actions | ❓ Unknown | PTZ services documented? |
| docs-high-level-description | ✅ Yes | README has overview |
| docs-installation-instructions | ✅ Yes | docs/INSTALLATION.md |
| docs-removal-instructions | ❌ No | Missing uninstall docs |
| entity-event-setup | ❓ Unknown | Need to verify |
| entity-unique-id | ✅ Likely | Using device IDs |
| has-entity-name | ❓ Unknown | Need to check entities |
| runtime-data | ❌ **No** | We use hass.data[DOMAIN], not entry.runtime_data |
| test-before-configure | ✅ Yes | Validates credentials in config flow |
| test-before-setup | ✅ Yes | Validates device in async_setup_entry |
| unique-config-entry | ✅ Yes | Uses device_id as unique_id |
| (missing #19?) | | |

**Bronze Status**: ~12/19 confirmed ✅, **2 FAILING** ❌

### 🥈 Silver Tier (10 rules)

| Rule | Status | Notes |
|------|--------|-------|
| action-exceptions | ❓ Unknown | Do our services raise proper exceptions? |
| config-entry-unloading | ✅ Yes | async_unload_entry implemented |
| docs-configuration-parameters | ✅ Yes | docs/CONFIGURATION.md |
| docs-installation-parameters | ✅ Yes | docs/INSTALLATION.md |
| entity-unavailable | ✅ Yes | Sets unavailable when offline |
| integration-owner | ✅ Yes | CODEOWNERS file |
| log-when-unavailable | ❓ Unknown | Need to verify logging |
| parallel-updates | ❌ **No** | Not specified in platforms |
| reauthentication-flow | ❌ **No** | No reauth flow implemented |
| test-coverage | ❌ **No** | We have ~70%, not 95% |

**Silver Status**: ~5/10 confirmed ✅, **3 FAILING** ❌

### 🥇 Gold Tier (23 rules)

| Rule | Status | Notes |
|------|--------|-------|
| devices | ✅ Yes | Creates devices |
| diagnostics | ✅ Yes | diagnostics.py |
| discovery-update-info | ❓ Unknown | |
| discovery | ✅ Yes | Device discovery in config flow |
| docs-data-update | ❓ Unknown | |
| docs-examples | ❌ No | No automation examples |
| docs-known-limitations | ❓ Unknown | |
| docs-supported-devices | ❌ No | No device compatibility list |
| docs-supported-functions | ❓ Unknown | |
| docs-troubleshooting | ✅ Yes | docs/PERFORMANCE_TROUBLESHOOTING.md |
| docs-use-cases | ❌ No | No use case examples |
| dynamic-devices | ❌ No | Cannot add devices after setup |
| entity-category | ✅ Likely | API status sensor is diagnostic |
| entity-device-class | ❓ Unknown | |
| entity-disabled-by-default | ❓ Unknown | |
| entity-translations | ✅ Yes | 8 languages |
| exception-translations | ❓ Unknown | |
| icon-translations | ✅ Yes | Just added icons.json! |
| reconfiguration-flow | ❌ **No** | No reconfigure flow |
| repair-issues | ❌ **No** | No repair flows |
| stale-devices | ❌ **No** | No stale device cleanup |
| (2 more?) | | |

**Gold Status**: ~8/23 confirmed ✅, **7 FAILING** ❌

### 🏆 Platinum Tier (3 rules)

| Rule | Status | Notes |
|------|--------|-------|
| async-dependency | ❌ **No** | imouapi is sync, not async |
| inject-websession | ❌ **No** | imouapi doesn't accept websession |
| strict-typing | ❓ Partial | We have type hints but not strict mode |

**Platinum Status**: **0/3** confirmed ✅, **2-3 FAILING** ❌

## Summary

### What We Actually Are

Based on failing rules:

- ❌ **Not Platinum**: Missing all 3 platinum requirements
- ❌ **Not Gold**: Missing 7+ gold requirements
- ❌ **Not Silver**: Missing 3 silver requirements
- ⚠️ **Possibly Bronze**: Missing 2 bronze requirements

**Estimated Actual Tier: Bronze** (with some Bronze rules still failing)

### Critical Missing Features

**Bronze Tier Blockers:**
1. ❌ `runtime-data` - Using old hass.data pattern instead of entry.runtime_data
2. ❌ `docs-removal-instructions` - No uninstall documentation

**Silver Tier Blockers:**
1. ❌ `parallel-updates` - Not specified
2. ❌ `reauthentication-flow` - No reauth flow
3. ❌ `test-coverage` - Only ~70%, need 95%

**Gold Tier Blockers:**
1. ❌ `reconfiguration-flow` - Cannot reconfigure after setup
2. ❌ `repair-issues` - No repair flows
3. ❌ `dynamic-devices` - Cannot add devices post-setup
4. ❌ `docs-examples` - No automation examples
5. ❌ `docs-supported-devices` - No device compatibility list
6. ❌ `docs-use-cases` - No use case documentation
7. ❌ `stale-devices` - No cleanup of removed devices

**Platinum Tier Blockers:**
1. ❌ `async-dependency` - imouapi library is synchronous
2. ❌ `inject-websession` - imouapi doesn't accept aiohttp session
3. ❓ `strict-typing` - Need mypy strict mode

### Realistic Quality Scale

**We should set quality_scale to: `bronze`** (or `silver` if we fix the 2 Bronze blockers quickly)

The official Imou repo honestly claims `bronze` - and they're right to do so.

## Action Items

### Quick Wins (Get to Solid Bronze)
1. ✅ Add uninstall docs
2. ✅ Migrate to entry.runtime_data pattern
3. ✅ Verify all Bronze requirements

### Medium Effort (Get to Silver)
1. Add parallel_updates to platforms
2. Implement reauthentication flow
3. Increase test coverage to 95%

### Large Effort (Get to Gold)
1. Add reconfiguration flow
2. Add repair flows
3. Add dynamic device discovery
4. Write comprehensive documentation (examples, use cases, device list)
5. Implement stale device cleanup

### Massive Effort (Get to Platinum)
1. Migrate to async API library (pyimouapi?) or wrap sync calls properly
2. Implement strict typing with mypy
3. Ensure dependency accepts websession

## Recommendation

**Update manifest.json to `"quality_scale": "bronze"`** and be honest about our current status.

Then systematically work through the rules to legitimately reach Silver, Gold, and eventually Platinum.

## Sources

- [Integration quality scale | Home Assistant Developer Docs](https://developers.home-assistant.io/docs/core/integration-quality-scale/)
- [Integration Quality Scale Rules](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/)
- [Quality scale - Home Assistant](https://www.home-assistant.io/docs/quality_scale/)
