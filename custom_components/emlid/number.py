"""Number platform for Emlid GNSS integration."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.const import UnitOfLength
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
class EmlidNumberEntityDescription(NumberEntityDescription):
    """Describes Emlid number entity."""

    value_fn: Callable[[dict[str, Any]], float | None]
    set_value_fn: Callable[[float], Any]
    available_fn: Callable[[dict[str, Any]], bool] = lambda data: True


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EmlidConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Emlid number entities from a config entry."""
    coordinator = config_entry.runtime_data.coordinator
    api_client = config_entry.runtime_data.api_client

    number_descriptions = [
        EmlidNumberEntityDescription(
            key="antenna_height",
            translation_key="antenna_height",
            name="Antenna Height",
            icon="mdi:ruler",
            native_unit_of_measurement=UnitOfLength.METERS,
            native_min_value=0.0,
            native_max_value=10.0,
            native_step=0.001,
            mode=NumberMode.BOX,
            value_fn=lambda data: data.get("configuration", {})
            .get("device", {})
            .get("antenna_height"),
            set_value_fn=lambda value: api_client.set_device_config(antenna_height=value),
            available_fn=lambda data: "configuration" in data,
        ),
        EmlidNumberEntityDescription(
            key="update_rate",
            translation_key="update_rate",
            name="GNSS Update Rate",
            icon="mdi:update",
            native_unit_of_measurement="Hz",
            native_min_value=1,
            native_max_value=20,
            native_step=1,
            mode=NumberMode.SLIDER,
            entity_registry_enabled_default=False,
            value_fn=lambda data: data.get("configuration", {})
            .get("positioning_settings", {})
            .get("gnss_settings", {})
            .get("update_rate"),
            set_value_fn=lambda value: api_client.set_positioning_settings(
                gnss_settings={"update_rate": int(value)}
            ),
            available_fn=lambda data: "configuration" in data,
        ),
        EmlidNumberEntityDescription(
            key="elevation_mask",
            translation_key="elevation_mask",
            name="Elevation Mask Angle",
            icon="mdi:angle-acute",
            native_unit_of_measurement="°",
            native_min_value=0,
            native_max_value=90,
            native_step=1,
            mode=NumberMode.SLIDER,
            entity_registry_enabled_default=False,
            value_fn=lambda data: data.get("configuration", {})
            .get("positioning_settings", {})
            .get("elevation_mask_angle"),
            set_value_fn=lambda value: api_client.set_positioning_settings(
                elevation_mask_angle=int(value)
            ),
            available_fn=lambda data: "configuration" in data,
        ),
        EmlidNumberEntityDescription(
            key="snr_mask",
            translation_key="snr_mask",
            name="SNR Mask",
            icon="mdi:signal",
            native_unit_of_measurement="dB-Hz",
            native_min_value=0,
            native_max_value=55,
            native_step=1,
            mode=NumberMode.SLIDER,
            entity_registry_enabled_default=False,
            value_fn=lambda data: data.get("configuration", {})
            .get("positioning_settings", {})
            .get("snr_mask"),
            set_value_fn=lambda value: api_client.set_positioning_settings(
                snr_mask=int(value)
            ),
            available_fn=lambda data: "configuration" in data,
        ),
        EmlidNumberEntityDescription(
            key="max_horizontal_acceleration",
            translation_key="max_horizontal_acceleration",
            name="Max Horizontal Acceleration",
            icon="mdi:speedometer",
            native_unit_of_measurement="m/s²",
            native_min_value=0.1,
            native_max_value=10.0,
            native_step=0.1,
            mode=NumberMode.BOX,
            entity_registry_enabled_default=False,
            value_fn=lambda data: data.get("configuration", {})
            .get("positioning_settings", {})
            .get("max_horizontal_acceleration"),
            set_value_fn=lambda value: api_client.set_positioning_settings(
                max_horizontal_acceleration=float(value)
            ),
            available_fn=lambda data: "configuration" in data,
        ),
        EmlidNumberEntityDescription(
            key="max_vertical_acceleration",
            translation_key="max_vertical_acceleration",
            name="Max Vertical Acceleration",
            icon="mdi:speedometer",
            native_unit_of_measurement="m/s²",
            native_min_value=0.1,
            native_max_value=10.0,
            native_step=0.1,
            mode=NumberMode.BOX,
            entity_registry_enabled_default=False,
            value_fn=lambda data: data.get("configuration", {})
            .get("positioning_settings", {})
            .get("max_vertical_acceleration"),
            set_value_fn=lambda value: api_client.set_positioning_settings(
                max_vertical_acceleration=float(value)
            ),
            available_fn=lambda data: "configuration" in data,
        ),
    ]

    entities = [
        EmlidNumber(coordinator, description, config_entry)
        for description in number_descriptions
    ]

    async_add_entities(entities)


class EmlidNumber(CoordinatorEntity[EmlidDataUpdateCoordinator], NumberEntity):
    """Representation of an Emlid number entity."""

    entity_description: EmlidNumberEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EmlidDataUpdateCoordinator,
        description: EmlidNumberEntityDescription,
        config_entry: EmlidConfigEntry,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{config_entry.entry_id}_{description.key}"

        # Device info
        device_info = coordinator.data.get("device_info", {}).get("device", {})
        serial_number = device_info.get("serial_number", config_entry.entry_id)
        model = device_info.get("model", "Emlid GNSS")

        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial_number)},
            "name": f"Emlid {model}",
            "manufacturer": MANUFACTURER,
            "model": model,
            "serial_number": serial_number,
            "sw_version": device_info.get("app_version"),
        }

    @property
    def native_value(self) -> float | None:
        """Return the value of the number entity."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.entity_description.available_fn(self.coordinator.data)
        )

    async def async_set_native_value(self, value: float) -> None:
        """Set the number value."""
        try:
            await self.entity_description.set_value_fn(value)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set %s to %s: %s", self.name, value, err)
            raise
