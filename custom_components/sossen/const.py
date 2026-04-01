"""Constants for the SOSSEN Microinverter integration."""

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass

DOMAIN = "sossen"
DEFAULT_POLL_INTERVAL = 10

CONF_DEVICE_ID = "device_id"
CONF_DEVICE_IP = "device_ip"
CONF_LOCAL_KEY = "local_key"
CONF_POLL_INTERVAL = "poll_interval"
CONF_DAYTIME_ONLY = "daytime_only"

PLATFORMS = ["sensor", "binary_sensor", "number", "switch"]

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
DP_DC_POWER_TOTAL = 4169
DP_WIFI_SIGNAL = 4172
DP_TEMPERATURE = 4183
DP_TEMPERATURE_2 = 4185

# DP IDs for writing (0x8000+ range)
DP_SET_FLAG = 32770
DP_SET_POWER_LIMIT = 32771

# Tuya DP numbers
TUYA_DP_DATA = "21"
TUYA_DP_COMMAND = 24
TUYA_DP_POLL = [4103]

SENSOR_DEFINITIONS = [
    {
        "key": "dc_power_total_w",
        "name": "Potenza DC Totale",
        "device_class": SensorDeviceClass.POWER,
        "unit": "W",
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:solar-power",
    },
    {
        "key": "ac_power_w",
        "name": "Potenza AC",
        "device_class": SensorDeviceClass.POWER,
        "unit": "W",
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:flash",
    },
    {
        "key": "ac_voltage_v",
        "name": "Tensione AC",
        "device_class": SensorDeviceClass.VOLTAGE,
        "unit": "V",
        "state_class": SensorStateClass.MEASUREMENT,
        "precision": 1,
    },
    {
        "key": "ac_frequency_hz",
        "name": "Frequenza AC",
        "device_class": SensorDeviceClass.FREQUENCY,
        "unit": "Hz",
        "state_class": SensorStateClass.MEASUREMENT,
        "precision": 2,
    },
    {
        "key": "dc_voltage_1_v",
        "name": "Tensione DC 1",
        "device_class": SensorDeviceClass.VOLTAGE,
        "unit": "V",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "dc_current_1_a",
        "name": "Corrente DC 1",
        "device_class": SensorDeviceClass.CURRENT,
        "unit": "A",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "dc_power_1_w",
        "name": "Potenza DC 1",
        "device_class": SensorDeviceClass.POWER,
        "unit": "W",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "dc_voltage_2_v",
        "name": "Tensione DC 2",
        "device_class": SensorDeviceClass.VOLTAGE,
        "unit": "V",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "dc_current_2_a",
        "name": "Corrente DC 2",
        "device_class": SensorDeviceClass.CURRENT,
        "unit": "A",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "dc_power_2_w",
        "name": "Potenza DC 2",
        "device_class": SensorDeviceClass.POWER,
        "unit": "W",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "energy_total_kwh",
        "name": "Energia Totale",
        "device_class": SensorDeviceClass.ENERGY,
        "unit": "kWh",
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:solar-power-variant",
    },
    {
        "key": "temperature_c",
        "name": "Temperatura",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": "°C",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "wifi_signal",
        "name": "Parametro 4172",
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:help-circle-outline",
    },
]
