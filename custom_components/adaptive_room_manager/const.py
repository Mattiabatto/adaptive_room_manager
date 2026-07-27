"""Constants for Adaptive Room Manager."""

DOMAIN = "adaptive_room_manager"
NAME = "Adaptive Room Manager"
MANUFACTURER = "Adaptive Room Manager"
MODEL = "Adaptive Room"
PLATFORMS = ["binary_sensor", "sensor", "switch", "number", "select"]

CONF_ENTRY_TYPE = "entry_type"
ENTRY_TYPE_HOME = "home"
ENTRY_TYPE_ROOM = "room"
HOME_UNIQUE_ID = "home_settings"

CONF_AREA_ID = "area_id"
CONF_TEMPORARY = "temporary_presence"
CONF_PERSISTENT = "persistent_presence"
CONF_LUX = "lux_sensors"
CONF_COVERS = "covers"
CONF_DAY_LIGHTS = "day_lights"
CONF_EVENING_LIGHTS = "evening_lights"
CONF_NIGHT_LIGHTS = "night_lights"
CONF_EVENING_START = "evening_start"
CONF_NIGHT_START = "night_start"
CONF_MORNING_START = "morning_start"
CONF_LUX_THRESHOLD = "lux_threshold"
CONF_ABSENCE_DELAY = "absence_delay"

DEFAULT_EVENING_START = "18:00:00"
DEFAULT_NIGHT_START = "22:30:00"
DEFAULT_MORNING_START = "07:00:00"
DEFAULT_LUX_THRESHOLD = 40.0
DEFAULT_ABSENCE_DELAY = 600
