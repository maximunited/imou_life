# Imou Life Integration Performance Troubleshooting

## Overview

This document provides solutions for the "Setup of switch platform imou_life is taking over 10 seconds" error and other performance issues with the Imou Life integration.

## Recent Improvements

The integration has been updated with the following performance enhancements:

1. **Timeout Protection**: Added configurable timeouts to prevent hanging setup
2. **Better Error Handling**: Improved error reporting and recovery
3. **Enhanced Logging**: More detailed logging for troubleshooting
4. **Performance Monitoring**: Better tracking of setup steps

## Configuration Options

### Setup Timeout

You can now configure a custom setup timeout to prevent the integration from hanging:

```yaml
# In your Home Assistant configuration.yaml or through the UI
imou_life:
  setup_timeout: 45  # seconds (default: 30)
```

### API Timeout

Configure API request timeouts:

```yaml
imou_life:
  api_timeout: 15  # seconds
```

## Troubleshooting Steps

### 1. Enable Debug Logging

Add this to your `configuration.yaml`:

```yaml
logger:
  custom_components.imou_life: debug
```

### 2. Check Network Connectivity

Test if you can reach the Imou API:

```bash
# Test basic connectivity
curl -I https://openapi.easy4ip.com/openapi

# Test with timeout
curl --max-time 10 https://openapi.easy4ip.com/openapi
```

### 3. Verify Device Status

Ensure your Imou device is:
- Online and accessible
- Has proper permissions
- Not experiencing connectivity issues

### 4. Check API Credentials

Verify your:
- App ID and App Secret are correct
- Device ID is valid
- Account has proper permissions

### 5. Monitor Setup Performance

Use the provided test scripts to diagnose performance:

```bash
# Test setup performance simulation
python test_setup_performance.py

# Validate your configuration
python validate_imou_setup.py
```

## Common Performance Bottlenecks

### Device Initialization (>10s)

**Symptoms**: Setup hangs during device initialization
**Causes**:
- Slow network connection to Imou servers
- API server issues
- Device offline or unresponsive

**Solutions**:
1. Increase setup timeout in configuration
2. Check network connectivity
3. Verify device is online
4. Try again during off-peak hours

### Initial Data Fetch (>5s)

**Symptoms**: Setup hangs during initial data retrieval
**Causes**:
- Device slow to respond
- Large amount of data to fetch
- API rate limiting

**Solutions**:
1. Increase scan interval
2. Check device connectivity
3. Verify API rate limits

### Platform Setup (>1s)

**Symptoms**: Individual platforms take time to load
**Causes**:
- Complex entity creation
- Sensor discovery delays

**Solutions**:
1. Check entity count
2. Verify sensor configurations
3. Monitor platform-specific logs

## Performance Optimization

### 1. Increase Timeouts

If you have a slow connection, increase timeouts:

```yaml
imou_life:
  setup_timeout: 60      # 60 seconds for setup
  api_timeout: 30        # 30 seconds for API calls
  scan_interval: 900     # 15 minutes between updates
```

### 2. Reduce Update Frequency

Increase scan intervals to reduce API calls:

```yaml
imou_life:
  scan_interval: 1800    # 30 minutes between updates
```

### 3. Enable Only Required Platforms

If you don't need all platforms, you can modify the code to load only what you need.

## Monitoring and Debugging

### Check Home Assistant Logs

Look for these log entries:

```
[DEBUG] custom_components.imou_life: Initializing device with timeout 30 seconds...
[DEBUG] custom_components.imou_life: Device initialization completed
[DEBUG] custom_components.imou_life: Fetching initial data with timeout 30 seconds...
[DEBUG] custom_components.imou_life: Initial data fetch completed
[DEBUG] custom_components.imou_life: Setting up platforms: ['switch', 'sensor', ...]
[DEBUG] custom_components.imou_life: Integration setup completed successfully
```

### Performance Metrics

Monitor these metrics:
- Setup completion time
- API response times
- Device response times
- Platform loading times

## Getting Help

If you continue to experience issues:

1. **Check the logs**: Enable debug logging and check for specific error messages
2. **Test connectivity**: Use the validation script to test your setup
3. **Report issues**: Include logs, configuration, and performance metrics
4. **Community support**: Check Home Assistant community forums

## Related Files

- `test_setup_performance.py` - Performance testing script
- `validate_imou_setup.py` - Configuration validation script
- `custom_components/imou_life/__init__.py` - Main integration file
- `custom_components/imou_life/switch.py` - Switch platform implementation

## Version History

- **v1.0.0**: Initial release
- **v1.1.0**: Added timeout protection and performance improvements
- **v1.2.0**: Enhanced error handling and logging
