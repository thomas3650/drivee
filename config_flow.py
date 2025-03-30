"""Config flow for Drivee integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from .const import DOMAIN, DEFAULT_DEVICE_ID, DEFAULT_APP_VERSION
from .client.drivee_client import DriveeClient

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

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Test the connection using async context manager
                async with DriveeClient(
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                    device_id="b1a9feedadc049ba",
                    app_version="2.126.0"
                ) as client:
                    await client.authenticate()
                
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input,
                )
            except Exception as e:
                _LOGGER.error("Failed to authenticate: %s", str(e))
                errors["base"] = "auth"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
