"""Constants for the SOSSEN Microinverter integration."""

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import Platform
from homeassistant.helpers.entity import EntityCategory

DOMAIN = "sossen"
DEFAULT_POLL_INTERVAL = 10
# While the inverter is powered off, only a light TCP probe runs, this often.
OFF_POLL_INTERVAL = 60

CONF_DEVICE_ID = "device_id"
CONF_DEVICE_IP = "device_ip"
CONF_LOCAL_KEY = "local_key"
CONF_POLL_INTERVAL = "poll_interval"
CONF_MODEL = "model"

# Standard Tuya local TCP port, used to probe whether the inverter is powered.
TUYA_PORT = 6668

DEVICE_NAME = "SOSSEN Microinverter"
DEFAULT_MODEL = "2in1"
POWER_LIMIT_MIN = 500
POWER_LIMIT_STEP = 10

# Supported inverter families. "channels" is the number of DC inputs (panels),
# "power_limit_max" the highest output limit accepted by the family.
MODELS = {
    "2in1": {"model": "2in1 (600/800/1000W)", "channels": 2, "power_limit_max": 1000},
    "4in1": {"model": "4in1 (2400W)", "channels": 4, "power_limit_max": 2400},
}

# Consecutive failed polls before the TCP probe decides between
# "inverter powered off" and "communication error".
MAX_FAILED_POLLS = 3
# Consecutive failures after which the socket is torn down to force a
# reconnect. Must be well above the ~2 min the device needs after a new
# connection before it starts answering polls.
RECONNECT_AFTER_FAILURES = 30
# Failed polls tolerated (reported as "off", not as an error) while the
# device boots: it needs ~2 min after power-on before answering.
WARMUP_POLLS = 20

PLATFORMS = [Platform.SENSOR, Platform.NUMBER]

# DP IDs for reading (0x1000+ range)
DP_STATUS = 4096
DP_ENERGY_TOTAL = 4098
DP_AC_VOLTAGE = 4103
DP_AC_POWER = 4126
DP_AC_FREQUENCY = 4131
DP_DC_CURRENT_1 = 4145
DP_DC_VOLTAGE_1 = 4146
DP_DC_POWER_1 = 4147
DP_DC_CURRENT_2 = 4149
DP_DC_VOLTAGE_2 = 4150
DP_DC_POWER_2 = 4151
# Datapoints 4152 and 4156 are numeric gaps in the otherwise regular
# channel sequence; their function is unknown, so they are left unmapped.
# Channels 3/4 (4in1 models only) — mapping confirmed independently on
# 4in1 2400W hardware by both community forks (flrs-94, Loudramin).
DP_DC_CURRENT_3 = 4153
DP_DC_VOLTAGE_3 = 4154
DP_DC_POWER_3 = 4155
DP_DC_CURRENT_4 = 4157
DP_DC_VOLTAGE_4 = 4158
DP_DC_POWER_4 = 4159
DP_DC_POWER_TOTAL = 4169
# Function unverified (varies slowly; possibly a temperature or RSSI).
DP_UNKNOWN_4172 = 4172
DP_TEMPERATURE = 4183

# DP IDs for writing (0x8000+ range)
DP_SET_FLAG = 32770
DP_SET_POWER_LIMIT = 32771

# Tuya DP numbers
TUYA_DP_COMMAND = 24
TUYA_DP_POLL = [4103]


def build_device_info(entry) -> dict:
    """Return the shared device_info dict for all entities of an entry."""
    model_key = entry.data.get(CONF_MODEL, DEFAULT_MODEL)
    model = MODELS.get(model_key, MODELS[DEFAULT_MODEL])
    return {
        "identifiers": {(DOMAIN, entry.data[CONF_DEVICE_ID])},
        "name": DEVICE_NAME,
        "manufacturer": "SOSSEN",
        "model": model["model"],
    }


# Entity names come from strings.json / translations via translation_key
# (= the "key" field). "when_off" is the value policy while the inverter
# is powered off (no sun and no battery):
#   zero        -> production is genuinely 0 W
#   unavailable -> nothing to measure, a value would be false data
#   retain      -> odometer-style counter, must never drop to 0
# "min_channels" hides channel 3/4 sensors on 2-channel models.
SENSOR_DEFINITIONS = [
    {
        "key": "dc_power_total_w",
        "device_class": SensorDeviceClass.POWER,
        "unit": "W",
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:solar-power",
        "when_off": "zero",
    },
    {
        "key": "ac_power_w",
        "device_class": SensorDeviceClass.POWER,
        "unit": "W",
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:flash",
        "when_off": "zero",
    },
    {
        "key": "ac_voltage_v",
        "device_class": SensorDeviceClass.VOLTAGE,
        "unit": "V",
        "state_class": SensorStateClass.MEASUREMENT,
        "precision": 1,
        "when_off": "unavailable",
    },
    {
        "key": "ac_frequency_hz",
        "device_class": SensorDeviceClass.FREQUENCY,
        "unit": "Hz",
        "state_class": SensorStateClass.MEASUREMENT,
        "precision": 2,
        "when_off": "unavailable",
    },
    {
        "key": "dc_voltage_1_v",
        "device_class": SensorDeviceClass.VOLTAGE,
        "unit": "V",
        "state_class": SensorStateClass.MEASUREMENT,
        "when_off": "unavailable",
    },
    {
        "key": "dc_current_1_a",
        "device_class": SensorDeviceClass.CURRENT,
        "unit": "A",
        "state_class": SensorStateClass.MEASUREMENT,
        "when_off": "zero",
    },
    {
        "key": "dc_power_1_w",
        "device_class": SensorDeviceClass.POWER,
        "unit": "W",
        "state_class": SensorStateClass.MEASUREMENT,
        "when_off": "zero",
    },
    {
        "key": "dc_voltage_2_v",
        "device_class": SensorDeviceClass.VOLTAGE,
        "unit": "V",
        "state_class": SensorStateClass.MEASUREMENT,
        "when_off": "unavailable",
    },
    {
        "key": "dc_current_2_a",
        "device_class": SensorDeviceClass.CURRENT,
        "unit": "A",
        "state_class": SensorStateClass.MEASUREMENT,
        "when_off": "zero",
    },
    {
        "key": "dc_power_2_w",
        "device_class": SensorDeviceClass.POWER,
        "unit": "W",
        "state_class": SensorStateClass.MEASUREMENT,
        "when_off": "zero",
    },
    {
        "key": "dc_voltage_3_v",
        "device_class": SensorDeviceClass.VOLTAGE,
        "unit": "V",
        "state_class": SensorStateClass.MEASUREMENT,
        "when_off": "unavailable",
        "min_channels": 4,
    },
    {
        "key": "dc_current_3_a",
        "device_class": SensorDeviceClass.CURRENT,
        "unit": "A",
        "state_class": SensorStateClass.MEASUREMENT,
        "when_off": "zero",
        "min_channels": 4,
    },
    {
        "key": "dc_power_3_w",
        "device_class": SensorDeviceClass.POWER,
        "unit": "W",
        "state_class": SensorStateClass.MEASUREMENT,
        "when_off": "zero",
        "min_channels": 4,
    },
    {
        "key": "dc_voltage_4_v",
        "device_class": SensorDeviceClass.VOLTAGE,
        "unit": "V",
        "state_class": SensorStateClass.MEASUREMENT,
        "when_off": "unavailable",
        "min_channels": 4,
    },
    {
        "key": "dc_current_4_a",
        "device_class": SensorDeviceClass.CURRENT,
        "unit": "A",
        "state_class": SensorStateClass.MEASUREMENT,
        "when_off": "zero",
        "min_channels": 4,
    },
    {
        "key": "dc_power_4_w",
        "device_class": SensorDeviceClass.POWER,
        "unit": "W",
        "state_class": SensorStateClass.MEASUREMENT,
        "when_off": "zero",
        "min_channels": 4,
    },
    {
        "key": "energy_total_kwh",
        "device_class": SensorDeviceClass.ENERGY,
        "unit": "kWh",
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:solar-power-variant",
        "when_off": "retain",
    },
    {
        "key": "temperature_c",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": "°C",
        "state_class": SensorStateClass.MEASUREMENT,
        "when_off": "unavailable",
    },
    {
        "key": "wifi_signal",
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:help-circle-outline",
        "when_off": "unavailable",
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
]
