"""Config flow for Emlid GNSS integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import EmlidAPIClient, EmlidAPIError
from .const import (
    CONF_HOST,
    CONF_UPDATE_RATE,
    DEFAULT_UPDATE_RATE,
    DOMAIN,
    MAX_UPDATE_RATE,
    MIN_UPDATE_RATE,
)

if TYPE_CHECKING:
    pass

_LOGGER = logging.getLogger(__name__)


class EmlidConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Emlid GNSS."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        super().__init__()
        self.errors = {}
        self.data = {}
        self.serial_number = ""

    async def validate_config(self) -> None:
        """Validate the host connection."""
        api_client = EmlidAPIClient(
            host=self.data[CONF_HOST],
            session=async_get_clientsession(self.hass),
        )
        try:
            info = await api_client.get_info()
            device_info = info.get("device", {})
            self.serial_number = device_info.get("serial_number", "Unknown")
            model = device_info.get("model", "Unknown")
            _LOGGER.debug("Successfully connected to %s (SN: %s)", model, self.serial_number)
        except EmlidAPIError as exc:
            _LOGGER.error("Connection failed: %s", exc)
            self.errors = {"base": "cannot_connect"}
        except Exception as exc:
            _LOGGER.error("Unexpected error: %s", exc)
            self.errors = {"base": "unknown"}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is not None:
            self.data[CONF_HOST] = user_input[CONF_HOST]
            self.data[CONF_UPDATE_RATE] = user_input.get(
                CONF_UPDATE_RATE, DEFAULT_UPDATE_RATE
            )
            await self.validate_config()

            if not self.errors:
                # Check if already configured
                await self.async_set_unique_id(self.serial_number)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Emlid GNSS ({self.serial_number})",
                    data=self.data,
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default="reach.local"): str,
                vol.Optional(
                    CONF_UPDATE_RATE,
                    default=DEFAULT_UPDATE_RATE,
                ): vol.All(vol.Coerce(float), vol.Range(min=MIN_UPDATE_RATE, max=MAX_UPDATE_RATE)),
            }
        )

        schema = self.add_suggested_values_to_schema(schema, user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=self.errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of the integration."""
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            self.data[CONF_HOST] = user_input[CONF_HOST]
            self.data[CONF_UPDATE_RATE] = user_input.get(
                CONF_UPDATE_RATE, DEFAULT_UPDATE_RATE
            )
            await self.validate_config()

            if not self.errors:
                return self.async_update_reload_and_abort(
                    entry,
                    data={
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_UPDATE_RATE: user_input[CONF_UPDATE_RATE],
                    },
                )

        # Pre-fill with existing values
        suggested_values = {
            CONF_HOST: entry.data.get(CONF_HOST, "reach.local"),
            CONF_UPDATE_RATE: entry.data.get(CONF_UPDATE_RATE, DEFAULT_UPDATE_RATE),
        }

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_UPDATE_RATE): vol.All(
                    vol.Coerce(float), vol.Range(min=MIN_UPDATE_RATE, max=MAX_UPDATE_RATE)
                ),
            }
        )

        schema = self.add_suggested_values_to_schema(schema, suggested_values)
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=schema,
            errors=self.errors,
        )
