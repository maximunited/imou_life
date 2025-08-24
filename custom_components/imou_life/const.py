"""Constants."""

# Internal constants
DOMAIN = "imou_life"
PLATFORMS = ["switch", "sensor", "binary_sensor", "select", "button", "siren", "camera"]

# Configuration definitions
CONF_API_URL = "api_url"
CONF_DEVICE_NAME = "device_name"
CONF_APP_ID = "app_id"
CONF_APP_SECRET = "app_secret"
CONF_ENABLE_DISCOVER = "enable_discover"
CONF_DISCOVERED_DEVICE = "discovered_device"
CONF_DEVICE_ID = "device_id"

OPTION_SCAN_INTERVAL = "scan_interval"
OPTION_API_TIMEOUT = "api_timeout"
OPTION_CALLBACK_URL = "callback_url"
OPTION_API_URL = "api_url"
OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD = "camera_wait_before_download"
OPTION_WAIT_AFTER_WAKE_UP = "wait_after_wakeup"
OPTION_SETUP_TIMEOUT = "setup_timeout"
OPTION_BATTERY_OPTIMIZATION = "battery_optimization"
OPTION_POWER_SAVING_MODE = "power_saving_mode"
OPTION_SLEEP_SCHEDULE = "sleep_schedule"
OPTION_MOTION_SENSITIVITY = "motion_sensitivity"
OPTION_RECORDING_QUALITY = "recording_quality"
OPTION_LED_INDICATORS = "led_indicators"
OPTION_AUTO_SLEEP = "auto_sleep"
OPTION_BATTERY_THRESHOLD = "battery_threshold"

SERVIZE_PTZ_LOCATION = "ptz_location"
SERVIZE_PTZ_MOVE = "ptz_move"
ATTR_PTZ_HORIZONTAL = "horizontal"
ATTR_PTZ_VERTICAL = "vertical"
ATTR_PTZ_ZOOM = "zoom"
ATTR_PTZ_OPERATION = "operation"
ATTR_PTZ_DURATION = "duration"

# Battery optimization services
SERVICE_OPTIMIZE_BATTERY = "optimize_battery"
SERVICE_SET_POWER_MODE = "set_power_mode"
SERVICE_SET_SLEEP_SCHEDULE = "set_sleep_schedule"
SERVICE_SET_MOTION_SENSITIVITY = "set_motion_sensitivity"
SERVICE_SET_RECORDING_QUALITY = "set_recording_quality"
SERVICE_ENTER_SLEEP_MODE = "enter_sleep_mode"
SERVICE_EXIT_SLEEP_MODE = "exit_sleep_mode"
SERVICE_RESET_POWER_SETTINGS = "reset_power_settings"

# Battery optimization attributes
ATTR_POWER_MODE = "power_mode"
ATTR_SLEEP_SCHEDULE = "sleep_schedule"
ATTR_MOTION_SENSITIVITY = "motion_sensitivity"
ATTR_RECORDING_QUALITY = "recording_quality"
ATTR_BATTERY_THRESHOLD = "battery_threshold"
ATTR_LED_INDICATORS = "led_indicators"
ATTR_AUTO_SLEEP = "auto_sleep"

# Defaults
DEFAULT_SCAN_INTERVAL = 15 * 60
DEFAULT_API_URL = "https://openapi.easy4ip.com/openapi"
DEFAULT_BATTERY_OPTIMIZATION = True
DEFAULT_POWER_SAVING_MODE = False
DEFAULT_MOTION_SENSITIVITY = "medium"
DEFAULT_RECORDING_QUALITY = "standard"
DEFAULT_LED_INDICATORS = True
DEFAULT_AUTO_SLEEP = False
DEFAULT_BATTERY_THRESHOLD = 20

# Power mode options
POWER_MODES = ["performance", "balanced", "power_saving", "ultra_power_saving"]

# Motion sensitivity levels
MOTION_SENSITIVITY_LEVELS = ["low", "medium", "high", "ultra_high"]

# Recording quality options
RECORDING_QUALITY_OPTIONS = ["low", "standard", "high", "ultra_high"]

# Sleep schedule options
SLEEP_SCHEDULE_OPTIONS = ["never", "night_only", "custom", "battery_based"]

# switches which are enabled by default
ENABLED_SWITCHES = [
    "motionDetect",
    "headerDetect",
    "abAlarmSound",
    "breathingLight",
    "closeCamera",
    "linkDevAlarm",
    "whiteLight",
    "smartTrack",
    "linkagewhitelight",
    "pushNotifications",
    "powerSavingMode",
    "autoSleep",
    "ledIndicators",
    "motionSensitivity",
]

# cameras which are enabled by default
ENABLED_CAMERAS = [
    "camera",
]

# icons of the sensors
SENSOR_ICONS = {
    "__default__": "mdi:bookmark",
    # sensors
    "lastAlarm": "mdi:timer",
    "storageUsed": "mdi:harddisk",
    "callbackUrl": "mdi:phone-incoming",
    "status": "mdi:lan-connect",
    "battery": "mdi:battery",
    "batteryLevel": "mdi:battery",
    "batteryVoltage": "mdi:flash",
    "powerConsumption": "mdi:lightning-bolt",
    "sleepMode": "mdi:power-sleep",
    "powerSavingStatus": "mdi:battery-saver",
    # binary sensors
    "online": "mdi:check-circle",
    "motionAlarm": "mdi:motion-sensor",
    "lowBattery": "mdi:battery-alert",
    "charging": "mdi:battery-charging",
    "powerSavingActive": "mdi:battery-saver",
    "sleepModeActive": "mdi:power-sleep",
    # select
    "nightVisionMode": "mdi:weather-night",
    "powerMode": "mdi:battery-settings",
    "recordingQuality": "mdi:video-quality",
    "motionSensitivityLevel": "mdi:tune-vertical",
    "sleepSchedule": "mdi:clock-outline",
    # switches
    "motionDetect": "mdi:motion-sensor",
    "headerDetect": "mdi:human",
    "abAlarmSound": "mdi:account-voice",
    "breathingLight": "mdi:television-ambient-light",
    "closeCamera": "mdi:sleep",
    "linkDevAlarm": "mdi:bell",
    "whiteLight": "mdi:light-flood-down",
    "smartTrack": "mdi:radar",
    "linkagewhitelight": "mdi:light-flood-down",
    "pushNotifications": "mdi:webhook",
    "powerSavingMode": "mdi:battery-saver",
    "autoSleep": "mdi:power-sleep",
    "ledIndicators": "mdi:led-variant-off",
    "motionSensitivity": "mdi:tune-vertical",
    # buttons
    "restartDevice": "mdi:restart",
    "refreshData": "mdi:refresh",
    "refreshAlarm": "mdi:refresh",
    "enterSleepMode": "mdi:power-sleep",
    "exitSleepMode": "mdi:power-sleep",
    "optimizeBattery": "mdi:battery-settings",
    "resetPowerSettings": "mdi:refresh-circle",
    # sirens
    "siren": "mdi:alarm-light",
    # cameras
    "camera": "mdi:video",
    "cameraSD": "mdi:video",
}
