"""Device tracker platform for Emlid GNSS integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import EmlidConfigEntry
from .const import DOMAIN, MANUFACTURER
from .coordinator import EmlidDataUpdateCoordinator

if TYPE_CHECKING:
    pass

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EmlidConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Emlid device tracker from a config entry."""
    coordinator = config_entry.runtime_data.coordinator

    async_add_entities([EmlidDeviceTracker(coordinator, config_entry)])


class EmlidDeviceTracker(CoordinatorEntity[EmlidDataUpdateCoordinator], TrackerEntity):
    """Representation of an Emlid GNSS device tracker."""

    _attr_has_entity_name = True
    _attr_name = "Location"
    _attr_icon = "mdi:map-marker"

    def __init__(
        self,
        coordinator: EmlidDataUpdateCoordinator,
        config_entry: EmlidConfigEntry,
    ) -> None:
        """Initialize the device tracker."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry.entry_id}_location"

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
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        nav_data = self.coordinator.data.get("navigation", {})
        return nav_data.get("latitude")

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        nav_data = self.coordinator.data.get("navigation", {})
        return nav_data.get("longitude")

    @property
    def source_type(self) -> SourceType:
        """Return the source type of the device."""
        return SourceType.GPS

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and "navigation" in self.coordinator.data
            and self.latitude is not None
            and self.longitude is not None
        )

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return extra attributes."""
        nav_data = self.coordinator.data.get("navigation", {})
        return {
            "altitude": nav_data.get("altitude"),
            "accuracy": nav_data.get("horizontal_accuracy"),
            "solution": nav_data.get("solution"),
            "satellites": nav_data.get("satellites_valid"),
        }
