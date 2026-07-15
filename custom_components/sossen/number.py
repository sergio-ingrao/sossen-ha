"""Number platform for SOSSEN Microinverter (power limit control)."""

import logging

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_DEVICE_ID,
    DOMAIN,
    POWER_LIMIT_MIN,
    POWER_LIMIT_STEP,
    build_device_info,
)
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
    _attr_translation_key = "power_limit"
    _attr_device_class = NumberDeviceClass.POWER
    _attr_icon = "mdi:transmission-tower"
    _attr_native_min_value = POWER_LIMIT_MIN
    _attr_native_step = POWER_LIMIT_STEP
    _attr_native_unit_of_measurement = "W"
    _attr_mode = NumberMode.BOX

    def __init__(
        self, coordinator: SossenCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data[CONF_DEVICE_ID]}_power_limit"
        self._attr_native_max_value = coordinator.model["power_limit_max"]
        self._attr_device_info = build_device_info(entry)

    @property
    def native_value(self) -> float | None:
        """Return the current power limit."""
        return self.coordinator.power_limit

    async def async_set_native_value(self, value: float) -> None:
        """Set the power limit."""
        await self.coordinator.async_set_power_limit(int(value))
        self.async_write_ha_state()
