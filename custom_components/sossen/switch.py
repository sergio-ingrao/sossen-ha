"""Switch platform for SOSSEN Microinverter (daytime-only mode)."""

import logging

from homeassistant.components.switch import SwitchEntity
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
    """Set up SOSSEN switch entity from a config entry."""
    coordinator: SossenCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SossenDaytimeSwitch(coordinator, entry)])


class SossenDaytimeSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to enable daytime-only polling."""

    _attr_has_entity_name = True
    _attr_name = "Solo Diurno"
    _attr_icon = "mdi:weather-sunny"

    def __init__(
        self, coordinator: SossenCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data[CONF_DEVICE_ID]}_daytime_only"

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
    def is_on(self) -> bool:
        """Return true if daytime-only mode is enabled."""
        return self.coordinator.daytime_only

    async def async_turn_on(self, **kwargs) -> None:
        """Enable daytime-only mode."""
        await self.coordinator.async_set_daytime_only(True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Disable daytime-only mode (poll 24/7)."""
        await self.coordinator.async_set_daytime_only(False)
        self.async_write_ha_state()
