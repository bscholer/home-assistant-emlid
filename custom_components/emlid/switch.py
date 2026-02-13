"""Switch platform for Emlid GNSS integration."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import EmlidConfigEntry
from .const import DOMAIN, MANUFACTURER
from .coordinator import EmlidDataUpdateCoordinator

if TYPE_CHECKING:
    pass

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class EmlidSwitchEntityDescription(SwitchEntityDescription):
    """Describes Emlid switch entity."""

    value_fn: Callable[[dict[str, Any]], bool | None]
    turn_on_fn: Callable
    turn_off_fn: Callable
    available_fn: Callable[[dict[str, Any]], bool] = lambda data: True


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EmlidConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Emlid switches from a config entry."""
    coordinator = config_entry.runtime_data.coordinator
    api_client = config_entry.runtime_data.api_client

    # Create switch descriptions dynamically with API client
    switch_descriptions = [
        EmlidSwitchEntityDescription(
            key="night_mode",
            translation_key="night_mode",
            name="Night Mode",
            icon="mdi:weather-night",
            value_fn=lambda data: data.get("configuration", {})
            .get("device", {})
            .get("night_mode"),
            turn_on_fn=lambda: api_client.set_device_config(night_mode=True),
            turn_off_fn=lambda: api_client.set_device_config(night_mode=False),
            available_fn=lambda data: "configuration" in data,
        ),
        EmlidSwitchEntityDescription(
            key="data_logging",
            translation_key="data_logging",
            name="Data Logging",
            icon="mdi:database",
            value_fn=lambda data: data.get("logging_active"),
            turn_on_fn=lambda: api_client.set_logging_state(True),
            turn_off_fn=lambda: api_client.set_logging_state(False),
            available_fn=lambda data: "logging_active" in data,
        ),
        # GNSS System switches
        EmlidSwitchEntityDescription(
            key="gnss_gps",
            translation_key="gnss_gps",
            name="GPS",
            icon="mdi:satellite-variant",
            entity_registry_enabled_default=False,
            value_fn=lambda data: (
                data.get("configuration", {})
                .get("positioning_settings", {})
                .get("gnss_settings", {})
                .get("positioning_systems", {})
                .get("gps")
            ),
            turn_on_fn=lambda: api_client.set_positioning_settings(
                gnss_settings={
                    "positioning_systems": {"gps": True}
                }
            ),
            turn_off_fn=lambda: api_client.set_positioning_settings(
                gnss_settings={
                    "positioning_systems": {"gps": False}
                }
            ),
            available_fn=lambda data: "configuration" in data,
        ),
        EmlidSwitchEntityDescription(
            key="gnss_glonass",
            translation_key="gnss_glonass",
            name="GLONASS",
            icon="mdi:satellite-variant",
            entity_registry_enabled_default=False,
            value_fn=lambda data: (
                data.get("configuration", {})
                .get("positioning_settings", {})
                .get("gnss_settings", {})
                .get("positioning_systems", {})
                .get("glonass")
            ),
            turn_on_fn=lambda: api_client.set_positioning_settings(
                gnss_settings={
                    "positioning_systems": {"glonass": True}
                }
            ),
            turn_off_fn=lambda: api_client.set_positioning_settings(
                gnss_settings={
                    "positioning_systems": {"glonass": False}
                }
            ),
            available_fn=lambda data: "configuration" in data,
        ),
        EmlidSwitchEntityDescription(
            key="gnss_galileo",
            translation_key="gnss_galileo",
            name="Galileo",
            icon="mdi:satellite-variant",
            entity_registry_enabled_default=False,
            value_fn=lambda data: (
                data.get("configuration", {})
                .get("positioning_settings", {})
                .get("gnss_settings", {})
                .get("positioning_systems", {})
                .get("galileo")
            ),
            turn_on_fn=lambda: api_client.set_positioning_settings(
                gnss_settings={
                    "positioning_systems": {"galileo": True}
                }
            ),
            turn_off_fn=lambda: api_client.set_positioning_settings(
                gnss_settings={
                    "positioning_systems": {"galileo": False}
                }
            ),
            available_fn=lambda data: "configuration" in data,
        ),
        EmlidSwitchEntityDescription(
            key="gnss_beidou",
            translation_key="gnss_beidou",
            name="BeiDou",
            icon="mdi:satellite-variant",
            entity_registry_enabled_default=False,
            value_fn=lambda data: (
                data.get("configuration", {})
                .get("positioning_settings", {})
                .get("gnss_settings", {})
                .get("positioning_systems", {})
                .get("beidou")
            ),
            turn_on_fn=lambda: api_client.set_positioning_settings(
                gnss_settings={
                    "positioning_systems": {"beidou": True}
                }
            ),
            turn_off_fn=lambda: api_client.set_positioning_settings(
                gnss_settings={
                    "positioning_systems": {"beidou": False}
                }
            ),
            available_fn=lambda data: "configuration" in data,
        ),
        EmlidSwitchEntityDescription(
            key="gnss_qzss",
            translation_key="gnss_qzss",
            name="QZSS",
            icon="mdi:satellite-variant",
            entity_registry_enabled_default=False,
            value_fn=lambda data: (
                data.get("configuration", {})
                .get("positioning_settings", {})
                .get("gnss_settings", {})
                .get("positioning_systems", {})
                .get("qzss")
            ),
            turn_on_fn=lambda: api_client.set_positioning_settings(
                gnss_settings={
                    "positioning_systems": {"qzss": True}
                }
            ),
            turn_off_fn=lambda: api_client.set_positioning_settings(
                gnss_settings={
                    "positioning_systems": {"qzss": False}
                }
            ),
            available_fn=lambda data: "configuration" in data,
        ),
    ]

    entities = [
        EmlidSwitch(coordinator, description, config_entry)
        for description in switch_descriptions
    ]

    async_add_entities(entities)


class EmlidSwitch(CoordinatorEntity[EmlidDataUpdateCoordinator], SwitchEntity):
    """Representation of an Emlid switch."""

    entity_description: EmlidSwitchEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EmlidDataUpdateCoordinator,
        description: EmlidSwitchEntityDescription,
        config_entry: EmlidConfigEntry,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{config_entry.entry_id}_{description.key}"

        # Device info
        device_info = coordinator.data.get("device_info", {}).get("device", {})
        serial_number = device_info.get("serial_number", config_entry.entry_id)
        model = device_info.get("model", "GNSS Receiver")

        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial_number)},
            "name": model,
            "manufacturer": MANUFACTURER,
            "model": model,
            "serial_number": serial_number,
            "sw_version": device_info.get("app_version"),
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.entity_description.available_fn(self.coordinator.data)
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        try:
            await self.entity_description.turn_on_fn()
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to turn on %s: %s", self.name, err)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        try:
            await self.entity_description.turn_off_fn()
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to turn off %s: %s", self.name, err)
            raise
