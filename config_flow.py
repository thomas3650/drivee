"""Config flow for Drivee integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from driveeClient import DriveeClient

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class DriveeConfigFlow(config_entries.ConfigFlow, domain="drivee"):
    """Handle a config flow for Drivee."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: Any | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Test the connection using async context manager
                async with DriveeClient(
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                ) as client:
                    await client.authenticate()
                await self.async_set_unique_id(user_input[CONF_USERNAME])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input,
                )
            except Exception:
                _LOGGER.exception("Failed to authenticate")
                errors["base"] = "auth"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
