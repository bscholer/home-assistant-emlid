"""Binary sensor platform for Emlid GNSS integration."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
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
class EmlidBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes Emlid binary sensor entity."""

    value_fn: Callable[[dict[str, Any]], bool | None]
    available_fn: Callable[[dict[str, Any]], bool] = lambda data: True


BINARY_SENSOR_DESCRIPTIONS: tuple[EmlidBinarySensorEntityDescription, ...] = (
    EmlidBinarySensorEntityDescription(
        key="lora_connected",
        translation_key="lora_connected",
        name="LoRa Connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda data: data.get("lora_connected"),
        available_fn=lambda data: "lora_connected" in data,
    ),
    EmlidBinarySensorEntityDescription(
        key="usb_power",
        translation_key="usb_power",
        name="USB Power",
        device_class=BinarySensorDeviceClass.PLUG,
        value_fn=lambda data: data.get("power_usb_connected"),
        available_fn=lambda data: "power_usb_connected" in data,
    ),
    EmlidBinarySensorEntityDescription(
        key="battery_present",
        translation_key="battery_present",
        name="Battery Present",
        device_class=BinarySensorDeviceClass.BATTERY,
        value_fn=lambda data: data.get("power_battery_present"),
        available_fn=lambda data: "power_battery_present" in data,
    ),
    EmlidBinarySensorEntityDescription(
        key="wifi_connected",
        translation_key="wifi_connected",
        name="WiFi Connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda data: (
            data.get("wifi_status", {}).get("enabled", False)
            and data.get("wifi_status", {}).get("current_network") is not None
        ),
        available_fn=lambda data: "wifi_status" in data,
    ),
    EmlidBinarySensorEntityDescription(
        key="bluetooth_enabled",
        translation_key="bluetooth_enabled",
        name="Bluetooth Enabled",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.get("bluetooth_status", {}).get("enabled"),
        available_fn=lambda data: "bluetooth_status" in data,
    ),
    EmlidBinarySensorEntityDescription(
        key="logging_active",
        translation_key="logging_active",
        name="Data Logging",
        icon="mdi:database",
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.get("logging_active"),
        available_fn=lambda data: "logging_active" in data,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EmlidConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Emlid binary sensors from a config entry."""
    coordinator = config_entry.runtime_data.coordinator

    entities = [
        EmlidBinarySensor(coordinator, description, config_entry)
        for description in BINARY_SENSOR_DESCRIPTIONS
    ]

    async_add_entities(entities)


class EmlidBinarySensor(
    CoordinatorEntity[EmlidDataUpdateCoordinator], BinarySensorEntity
):
    """Representation of an Emlid binary sensor."""

    entity_description: EmlidBinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EmlidDataUpdateCoordinator,
        description: EmlidBinarySensorEntityDescription,
        config_entry: EmlidConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
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
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.entity_description.available_fn(self.coordinator.data)
        )
