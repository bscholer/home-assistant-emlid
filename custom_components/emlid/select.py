"""Select platform for Emlid GNSS integration."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
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
class EmlidSelectEntityDescription(SelectEntityDescription):
    """Describes Emlid select entity."""

    value_fn: Callable[[dict[str, Any]], str | None]
    set_value_fn: Callable[[str], Any]
    available_fn: Callable[[dict[str, Any]], bool] = lambda data: True


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EmlidConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Emlid select entities from a config entry."""
    coordinator = config_entry.runtime_data.coordinator
    api_client = config_entry.runtime_data.api_client

    select_descriptions = [
        EmlidSelectEntityDescription(
            key="positioning_mode",
            translation_key="positioning_mode",
            name="Positioning Mode",
            icon="mdi:navigation-variant",
            options=["kinematic", "static", "stop-and-go"],
            entity_registry_enabled_default=False,
            value_fn=lambda data: data.get("configuration", {})
            .get("positioning_settings", {})
            .get("positioning_mode"),
            set_value_fn=lambda value: api_client.set_positioning_settings(
                positioning_mode=value
            ),
            available_fn=lambda data: "configuration" in data,
        ),
        EmlidSelectEntityDescription(
            key="gps_ar_mode",
            translation_key="gps_ar_mode",
            name="GPS AR Mode",
            icon="mdi:radar",
            options=["fix-and-hold", "continuous"],
            entity_registry_enabled_default=False,
            value_fn=lambda data: data.get("configuration", {})
            .get("positioning_settings", {})
            .get("gps_ar_mode"),
            set_value_fn=lambda value: api_client.set_positioning_settings(
                gps_ar_mode=value
            ),
            available_fn=lambda data: "configuration" in data,
        ),
    ]

    entities = [
        EmlidSelect(coordinator, description, config_entry)
        for description in select_descriptions
    ]

    async_add_entities(entities)


class EmlidSelect(CoordinatorEntity[EmlidDataUpdateCoordinator], SelectEntity):
    """Representation of an Emlid select entity."""

    entity_description: EmlidSelectEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EmlidDataUpdateCoordinator,
        description: EmlidSelectEntityDescription,
        config_entry: EmlidConfigEntry,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{config_entry.entry_id}_{description.key}"

        # Device info
        device_info = coordinator.data.get("device_info", {}).get("device", {})
        serial_number = device_info.get("serial_number", config_entry.entry_id)
        model = device_info.get("model", "Reach RS4")

        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial_number)},
            "name": "Emlid",
            "manufacturer": MANUFACTURER,
            "model": model,
            "serial_number": serial_number,
            "sw_version": device_info.get("app_version"),
        }

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.entity_description.available_fn(self.coordinator.data)
        )

    async def async_select_option(self, option: str) -> None:
        """Select an option."""
        try:
            await self.entity_description.set_value_fn(option)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set %s to %s: %s", self.name, option, err)
            raise
