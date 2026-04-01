"""Status sensor platform for SOSSEN Microinverter."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_ID, DOMAIN
from .coordinator import SossenCoordinator

STATUS_MAP = {
    0: "off",
    1: "alarm",
    3: "producing",
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up SOSSEN status sensor from a config entry."""
    coordinator: SossenCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SossenStatusSensor(coordinator, entry)])


class SossenStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor with 3 states: producing, alarm, off."""

    _attr_has_entity_name = True
    _attr_name = "Stato"
    _attr_icon = "mdi:solar-power"

    def __init__(
        self, coordinator: SossenCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the status sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data[CONF_DEVICE_ID]}_status"

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
    def native_value(self) -> str | None:
        """Return the status: producing, alarm, or off."""
        if not self.coordinator.data or not self.coordinator.data.get("status"):
            return "off"
        raw = self.coordinator.data.get("status", 0)
        return STATUS_MAP.get(raw, f"unknown ({raw})")

    @property
    def icon(self) -> str:
        """Return icon based on status."""
        value = self.native_value
        if value == "producing":
            return "mdi:solar-power"
        if value == "alarm":
            return "mdi:alert"
        return "mdi:power-sleep"

    @property
    def extra_state_attributes(self):
        """Return the raw status value."""
        if not self.coordinator.data:
            return None
        return {"status_raw": self.coordinator.data.get("status", 0)}
