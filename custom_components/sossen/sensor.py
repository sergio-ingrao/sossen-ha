"""Sensor platform for SOSSEN Microinverter."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_ID, DOMAIN, SENSOR_DEFINITIONS
from .coordinator import SossenCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up SOSSEN sensors from a config entry."""
    coordinator: SossenCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        SossenSensor(coordinator, entry, sensor_def)
        for sensor_def in SENSOR_DEFINITIONS
    ]
    entities.append(SossenRawSensor(coordinator, entry))
    async_add_entities(entities)


class SossenSensor(CoordinatorEntity, SensorEntity):
    """Representation of a SOSSEN sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SossenCoordinator,
        entry: ConfigEntry,
        sensor_def: dict,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = sensor_def["key"]
        self._attr_unique_id = f"{entry.data[CONF_DEVICE_ID]}_{self._key}"
        self._attr_translation_key = self._key
        self._attr_name = sensor_def["name"]
        self._attr_device_class = sensor_def.get("device_class")
        self._attr_native_unit_of_measurement = sensor_def.get("unit")
        self._attr_state_class = sensor_def.get("state_class")
        if "icon" in sensor_def:
            self._attr_icon = sensor_def["icon"]
        if "precision" in sensor_def:
            self._attr_suggested_display_precision = sensor_def["precision"]

    @property
    def device_info(self):
        """Return device info to group all entities under one device."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.entry.data[CONF_DEVICE_ID])},
            "name": "SOSSEN Microinverter",
            "manufacturer": "SOSSEN",
            "model": "2in1-DE 800W",
        }

    @property
    def native_value(self):
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._key)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available and self.coordinator.data is not None


class SossenRawSensor(CoordinatorEntity, SensorEntity):
    """Diagnostic sensor showing all raw DP values."""

    _attr_has_entity_name = True
    _attr_name = "Raw Data"
    _attr_icon = "mdi:bug"
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: SossenCoordinator, entry: ConfigEntry) -> None:
        """Initialize the raw sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data[CONF_DEVICE_ID]}_raw"

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.entry.data[CONF_DEVICE_ID])},
            "name": "SOSSEN Microinverter",
            "manufacturer": "SOSSEN",
            "model": "2in1-DE 800W",
        }

    @property
    def native_value(self):
        """Return timestamp of last update."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("power_w")

    @property
    def extra_state_attributes(self):
        """Return all raw DP values as attributes."""
        if not self.coordinator.data:
            return None
        raw = self.coordinator.data.get("_raw", {})
        return {f"dp_{k}": v for k, v in raw.items()}
