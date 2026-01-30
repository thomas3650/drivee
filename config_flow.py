"""Config flow for Drivee integration."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from aiohttp import ClientError
from drivee_client import DriveeClient
from drivee_client.errors import AuthenticationError, DriveeError
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

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

                _LOGGER.info(
                    "Successfully authenticated user: %s", user_input[CONF_USERNAME]
                )
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input,
                )
            except AuthenticationError:
                _LOGGER.warning(
                    "Authentication failed for user: %s", user_input.get(CONF_USERNAME)
                )
                errors["base"] = "invalid_auth"
            except (ClientError, TimeoutError) as err:
                _LOGGER.error("Connection error during setup: %s", err)
                errors["base"] = "cannot_connect"
            except DriveeError as err:
                _LOGGER.error("Drivee API error during setup: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during authentication")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> config_entries.ConfigFlowResult:
        """Handle re-authentication when credentials become invalid."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Confirm re-authentication with new credentials."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Test the new credentials
                async with DriveeClient(
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                ) as client:
                    await client.authenticate()

                # Update the config entry with new credentials
                entry = self.hass.config_entries.async_get_entry(
                    self.context["entry_id"]
                )
                if entry:
                    self.hass.config_entries.async_update_entry(
                        entry,
                        data=user_input,
                    )
                    await self.hass.config_entries.async_reload(entry.entry_id)
                    _LOGGER.info(
                        "Successfully re-authenticated user: %s",
                        user_input[CONF_USERNAME],
                    )
                    return self.async_abort(reason="reauth_successful")

            except AuthenticationError:
                _LOGGER.warning(
                    "Re-authentication failed for user: %s",
                    user_input.get(CONF_USERNAME),
                )
                errors["base"] = "invalid_auth"
            except (ClientError, TimeoutError) as err:
                _LOGGER.error("Connection error during re-authentication: %s", err)
                errors["base"] = "cannot_connect"
            except DriveeError as err:
                _LOGGER.error("Drivee API error during re-authentication: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during re-authentication")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={"username": self.context.get("username", "")},
        )
