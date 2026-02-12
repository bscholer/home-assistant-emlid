"""The Emlid GNSS integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import EmlidAPIClient, EmlidWebSocketClient
from .const import CONF_HOST, CONF_UPDATE_RATE, DEFAULT_UPDATE_RATE, DOMAIN, PLATFORMS
from .coordinator import EmlidDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


@dataclass
class EmlidData:
    """Dataclass for runtime data."""

    coordinator: EmlidDataUpdateCoordinator
    api_client: EmlidAPIClient
    ws_client: EmlidWebSocketClient


type EmlidConfigEntry = ConfigEntry[EmlidData]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EmlidConfigEntry,
) -> bool:
    """Set up Emlid GNSS integration using config entry."""
    _LOGGER.debug("Setting up Emlid GNSS integration")

    host = config_entry.data[CONF_HOST]
    update_rate = config_entry.data.get(CONF_UPDATE_RATE, DEFAULT_UPDATE_RATE)

    # Initialize API clients
    api_client = EmlidAPIClient(
        host=host,
        session=async_get_clientsession(hass),
    )

    ws_client = EmlidWebSocketClient(host=host)

    # Validate connection by fetching device info
    try:
        info = await api_client.get_info()
        device_info = info.get("device", {})
        _LOGGER.debug(
            "Connected to Emlid %s (SN: %s)",
            device_info.get("model", "Unknown"),
            device_info.get("serial_number", "Unknown"),
        )
    except Exception as err:
        _LOGGER.error("Failed to connect to Emlid device: %s", err)
        return False

    # Initialize coordinator
    coordinator = EmlidDataUpdateCoordinator(
        hass, config_entry, api_client, ws_client, update_rate
    )

    # Connect WebSocket
    try:
        await ws_client.connect()
    except Exception as err:
        _LOGGER.error("Failed to connect WebSocket: %s", err)
        return False

    # Perform first data fetch
    await coordinator.async_config_entry_first_refresh()

    config_entry.runtime_data = EmlidData(
        coordinator=coordinator,
        api_client=api_client,
        ws_client=ws_client,
    )

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: EmlidConfigEntry) -> bool:
    """Unload Emlid GNSS config entry."""
    # Disconnect WebSocket
    if entry.runtime_data.ws_client:
        await entry.runtime_data.ws_client.disconnect()

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        del entry.runtime_data
    return unload_ok
