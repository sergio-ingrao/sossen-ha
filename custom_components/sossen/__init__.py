"""SOSSEN Microinverter integration for Home Assistant."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, PLATFORMS
from .coordinator import SossenCoordinator

_LOGGER = logging.getLogger(__name__)

# Entity domains used by older versions and since removed: the daytime-only
# switch (dropped in 1.1.0) and the status sensor that was wrongly registered
# under binary_sensor.
_STALE_DOMAINS = ("switch", "binary_sensor")


def _cleanup_stale_entities(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove registry entities left over from older versions."""
    registry = er.async_get(hass)
    for entity in er.async_entries_for_config_entry(registry, entry.entry_id):
        if entity.domain in _STALE_DOMAINS:
            _LOGGER.info("Removing stale entity %s", entity.entity_id)
            registry.async_remove(entity.entity_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SOSSEN from a config entry."""
    _LOGGER.info("SOSSEN setup starting")
    hass.data.setdefault(DOMAIN, {})

    _cleanup_stale_entities(hass, entry)

    coordinator = SossenCoordinator(hass, entry)

    # This activates the periodic polling timer.
    # _async_update_data returns None quickly if no data yet (not blocking).
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.info(
        "SOSSEN setup complete, polling every %ss",
        coordinator.update_interval.total_seconds(),
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: SossenCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()
    return unload_ok
