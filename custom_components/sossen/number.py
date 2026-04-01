"""Number platform for SOSSEN Microinverter (power limit control)."""

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_ID, DOMAIN
from .coordinator import SossenCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up SOSSEN number entity from a config entry."""
    coordinator: SossenCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SossenPowerLimit(coordinator, entry)])


class SossenPowerLimit(CoordinatorEntity, NumberEntity):
    """Number entity to set the inverter power limit."""

    _attr_has_entity_name = True
    _attr_name = "Limite Potenza"
    _attr_icon = "mdi:transmission-tower"
    _attr_native_min_value = 500
    _attr_native_max_value = 1000
    _attr_native_step = 10
    _attr_native_unit_of_measurement = "W"
    _attr_mode = NumberMode.BOX

    def __init__(
        self, coordinator: SossenCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data[CONF_DEVICE_ID]}_power_limit"

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
    def native_value(self) -> float | None:
        """Return the current power limit."""
        return self.coordinator.power_limit

    async def async_set_native_value(self, value: float) -> None:
        """Set the power limit."""
        await self.coordinator.async_set_power_limit(int(value))
        self.async_write_ha_state()
