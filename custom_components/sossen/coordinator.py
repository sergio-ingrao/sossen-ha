"""Data update coordinator for SOSSEN Microinverter."""

import logging
import time
from datetime import timedelta

import tinytuya

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_DAYTIME_ONLY,
    CONF_DEVICE_ID,
    CONF_DEVICE_IP,
    CONF_LOCAL_KEY,
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
    TUYA_DP_COMMAND,
    TUYA_DP_DATA,
    TUYA_DP_POLL,
)
from .protocol import build_set_power_payload, decode_payload, decode_records

_LOGGER = logging.getLogger(__name__)


class SossenCoordinator(DataUpdateCoordinator):
    """Coordinator to manage polling the SOSSEN inverter."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        poll_interval = entry.data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=poll_interval),
        )
        self.entry = entry
        self._device_id = entry.data[CONF_DEVICE_ID]
        self._device_ip = entry.data[CONF_DEVICE_IP]
        self._local_key = entry.data[CONF_LOCAL_KEY]
        self._device: tinytuya.Device | None = None
        self._power_limit: int | None = entry.data.get("power_limit_last", 800)
        self._limit_read_pending: bool = self._power_limit is None
        self.daytime_only: bool = entry.data.get(CONF_DAYTIME_ONLY, True)

    def _is_sun_up(self) -> bool:
        """Check if the sun is above the horizon using HA's sun entity."""
        sun_state = self.hass.states.get("sun.sun")
        if sun_state is None:
            return True  # if sun entity unavailable, assume daytime
        return sun_state.state == "above_horizon"

    def _ensure_device(self) -> tinytuya.Device:
        """Create or return the TinyTuya device (called from executor thread)."""
        if self._device is None:
            self._device = tinytuya.Device(
                self._device_id, self._device_ip, self._local_key, version=3.5
            )
            self._device.set_socketTimeout(10)
            self._device.set_socketPersistent(True)
        return self._device

    def _disconnect(self) -> None:
        """Disconnect the TinyTuya device."""
        if self._device is not None:
            try:
                self._device.close()
            except Exception:
                pass
            self._device = None

    def _sync_poll(self) -> dict | None:
        """Poll the inverter (runs in executor thread, blocking is OK).

        After updatedps, the device sends DP25 first, then DP21.
        We need multiple receive() calls to get DP21.
        """
        try:
            device = self._ensure_device()
            device.updatedps(TUYA_DP_POLL)

            for attempt in range(5):
                result = device.receive()
                if not result or "dps" not in result:
                    continue

                for dp_key, val in result["dps"].items():
                    if isinstance(val, str) and len(val) > 20:
                        decoded = decode_payload(val)
                        if decoded:
                            return decoded

            return None
        except Exception as err:
            _LOGGER.debug("_sync_poll exception: %s", err)
            return None

    def _sync_read_power_limit(self) -> int | None:
        """Read the current power limit by querying DP 24 config."""
        try:
            device = self._ensure_device()
            device.updatedps([24])
            for _ in range(5):
                result = device.receive()
                if result and "dps" in result and "24" in result["dps"]:
                    val = result["dps"]["24"]
                    if isinstance(val, str) and len(val) > 10:
                        records = decode_records(val)
                        if 32771 in records:
                            return records[32771]
            return None
        except Exception:
            return None

    def _sync_set_power_limit(self, watts: int) -> bool:
        """Set the power limit (runs in executor thread)."""
        device = self._ensure_device()
        payload = build_set_power_payload(watts)
        result = device.set_value(TUYA_DP_COMMAND, payload)
        return result is not None

    async def _async_update_data(self) -> dict | None:
        """Fetch data from the inverter."""
        # TODO: re-enable daytime check once basic polling works
        # if self.daytime_only and not self._is_sun_up():
        #     await self.hass.async_add_executor_job(self._disconnect)
        #     return None

        try:
            data = await self.hass.async_add_executor_job(self._sync_poll)
            if data is not None:
                _LOGGER.debug("Got data: power=%sW", data.get("power_w"))
                # Read power limit once after first successful poll
                if self._limit_read_pending:
                    limit = await self.hass.async_add_executor_job(
                        self._sync_read_power_limit
                    )
                    if limit is not None:
                        self._power_limit = limit
                        self._limit_read_pending = False
                        _LOGGER.info("Read power limit from device: %dW", limit)
                return data
            if self.data is not None:
                return self.data
            return {}
        except Exception as err:
            _LOGGER.debug("Poll error: %s", err)
            if self.data is not None:
                return self.data
            return {}

    async def async_set_power_limit(self, watts: int) -> None:
        """Set the inverter power limit."""
        success = await self.hass.async_add_executor_job(
            self._sync_set_power_limit, watts
        )
        if success:
            self._power_limit = watts
            # Persist last set value so it survives restarts
            new_data = {**self.entry.data, "power_limit_last": watts}
            self.hass.config_entries.async_update_entry(self.entry, data=new_data)
            _LOGGER.info("Power limit set to %dW", watts)
        else:
            _LOGGER.error("Failed to set power limit to %dW", watts)

    async def async_set_daytime_only(self, enabled: bool) -> None:
        """Update the daytime-only setting."""
        self.daytime_only = enabled
        # Persist to config entry
        new_data = {**self.entry.data, CONF_DAYTIME_ONLY: enabled}
        self.hass.config_entries.async_update_entry(self.entry, data=new_data)

    async def async_shutdown(self) -> None:
        """Disconnect on shutdown."""
        await self.hass.async_add_executor_job(self._disconnect)

    @property
    def power_limit(self) -> int | None:
        """Return the last set power limit."""
        return self._power_limit
