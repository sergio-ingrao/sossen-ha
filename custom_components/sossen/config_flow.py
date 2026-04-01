"""Config flow for SOSSEN Microinverter."""

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_DAYTIME_ONLY,
    CONF_DEVICE_ID,
    CONF_DEVICE_IP,
    CONF_LOCAL_KEY,
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_IP): str,
        vol.Required(CONF_DEVICE_ID): str,
        vol.Required(CONF_LOCAL_KEY): str,
        vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): vol.All(
            int, vol.Range(min=5, max=60)
        ),
        vol.Optional(CONF_DAYTIME_ONLY, default=True): bool,
    }
)


class SossenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SOSSEN."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
            self._abort_if_unique_id_configured()

            # Don't test connection — the device takes 2 min to respond
            # and the UI mangles special characters in the key.
            # Just save and let the coordinator handle connection.
            return self.async_create_entry(
                title="SOSSEN Microinverter",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
        )
