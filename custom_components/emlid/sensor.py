"""Sensor platform for Emlid GNSS integration."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfLength,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import EmlidConfigEntry
from .const import DOMAIN, MANUFACTURER
from .coordinator import EmlidDataUpdateCoordinator

if TYPE_CHECKING:
    pass

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class EmlidSensorEntityDescription(SensorEntityDescription):
    """Describes Emlid sensor entity."""

    value_fn: Callable[[dict[str, Any]], StateType]
    available_fn: Callable[[dict[str, Any]], bool] = lambda data: True


SENSOR_DESCRIPTIONS: tuple[EmlidSensorEntityDescription, ...] = (
    # Navigation sensors
    EmlidSensorEntityDescription(
        key="solution",
        translation_key="solution",
        name="Solution Status",
        icon="mdi:crosshairs-gps",
        value_fn=lambda data: data.get("navigation", {}).get("solution"),
        available_fn=lambda data: "navigation" in data,
    ),
    EmlidSensorEntityDescription(
        key="latitude",
        translation_key="latitude",
        name="Latitude",
        icon="mdi:latitude",
        native_unit_of_measurement="°",
        suggested_display_precision=10,
        value_fn=lambda data: round(data.get("navigation", {}).get("latitude", 0), 10),
        available_fn=lambda data: "navigation" in data,
    ),
    EmlidSensorEntityDescription(
        key="longitude",
        translation_key="longitude",
        name="Longitude",
        icon="mdi:longitude",
        native_unit_of_measurement="°",
        suggested_display_precision=10,
        value_fn=lambda data: round(data.get("navigation", {}).get("longitude", 0), 10),
        available_fn=lambda data: "navigation" in data,
    ),
    EmlidSensorEntityDescription(
        key="altitude",
        translation_key="altitude",
        name="Altitude",
        icon="mdi:elevation-rise",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        value_fn=lambda data: round(data.get("navigation", {}).get("altitude", 0), 3),
        available_fn=lambda data: "navigation" in data,
    ),
    EmlidSensorEntityDescription(
        key="horizontal_accuracy",
        translation_key="horizontal_accuracy",
        name="Horizontal Accuracy",
        icon="mdi:target",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        value_fn=lambda data: round(
            data.get("navigation", {}).get("horizontal_accuracy", 0), 3
        ),
        available_fn=lambda data: "navigation" in data,
    ),
    EmlidSensorEntityDescription(
        key="vertical_accuracy",
        translation_key="vertical_accuracy",
        name="Vertical Accuracy",
        icon="mdi:target",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        value_fn=lambda data: round(data.get("navigation", {}).get("vertical_accuracy", 0), 3),
        available_fn=lambda data: "navigation" in data,
    ),
    EmlidSensorEntityDescription(
        key="baseline",
        translation_key="baseline",
        name="Baseline Distance",
        icon="mdi:map-marker-distance",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: round(data.get("navigation", {}).get("baseline", 0), 1),
        available_fn=lambda data: "navigation" in data,
    ),
    EmlidSensorEntityDescription(
        key="positioning_mode",
        translation_key="positioning_mode",
        name="Positioning Mode",
        icon="mdi:navigation-variant",
        value_fn=lambda data: data.get("navigation", {}).get("positioning_mode"),
        available_fn=lambda data: "navigation" in data,
    ),
    # Satellite sensors
    EmlidSensorEntityDescription(
        key="satellites_rover",
        translation_key="satellites_rover",
        name="Satellites (Rover)",
        icon="mdi:satellite-variant",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("navigation", {}).get("satellites_rover", 0),
        available_fn=lambda data: "navigation" in data,
    ),
    EmlidSensorEntityDescription(
        key="satellites_valid",
        translation_key="satellites_valid",
        name="Satellites (Valid)",
        icon="mdi:satellite-uplink",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("navigation", {}).get("satellites_valid", 0),
        available_fn=lambda data: "navigation" in data,
    ),
    EmlidSensorEntityDescription(
        key="hdop",
        translation_key="hdop",
        name="HDOP",
        icon="mdi:signal-variant",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: round(data.get("navigation", {}).get("hdop", 0), 2),
        available_fn=lambda data: "navigation" in data,
    ),
    # Battery sensors
    EmlidSensorEntityDescription(
        key="battery",
        translation_key="battery",
        name="Battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("battery", {}).get("state_of_charge"),
        available_fn=lambda data: "battery" in data,
    ),
    EmlidSensorEntityDescription(
        key="battery_voltage",
        translation_key="battery_voltage",
        name="Battery Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: round(data.get("battery", {}).get("voltage", 0), 2),
        available_fn=lambda data: "battery" in data,
    ),
    EmlidSensorEntityDescription(
        key="battery_current",
        translation_key="battery_current",
        name="Battery Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: round(data.get("battery", {}).get("current", 0), 2),
        available_fn=lambda data: "battery" in data,
    ),
    EmlidSensorEntityDescription(
        key="battery_temperature",
        translation_key="battery_temperature",
        name="Battery Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: round(data.get("battery", {}).get("temperature", 0), 1),
        available_fn=lambda data: "battery" in data,
    ),
    EmlidSensorEntityDescription(
        key="charging_status",
        translation_key="charging_status",
        name="Charging Status",
        icon="mdi:battery-charging",
        value_fn=lambda data: data.get("battery", {}).get("charger_status"),
        available_fn=lambda data: "battery" in data,
    ),
    # Communication sensors
    EmlidSensorEntityDescription(
        key="lora_rssi",
        translation_key="lora_rssi",
        name="LoRa RSSI",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.get("lora_rssi") if data.get("lora_rssi", -1) != -1 else None,
        available_fn=lambda data: "lora_rssi" in data and data["lora_rssi"] != -1,
    ),
    EmlidSensorEntityDescription(
        key="correction_input_state",
        translation_key="correction_input_state",
        name="Correction Input State",
        icon="mdi:antenna",
        value_fn=lambda data: data.get("correction_input_state"),
        available_fn=lambda data: "correction_input_state" in data,
    ),
    EmlidSensorEntityDescription(
        key="wifi_ssid",
        translation_key="wifi_ssid",
        name="WiFi SSID",
        icon="mdi:wifi",
        value_fn=lambda data: data.get("wifi_status", {})
        .get("current_network", {})
        .get("ssid"),
        available_fn=lambda data: "wifi_status" in data
        and data["wifi_status"].get("current_network") is not None,
    ),
    # Device info sensors
    EmlidSensorEntityDescription(
        key="role",
        translation_key="role",
        name="Device Role",
        icon="mdi:label",
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.get("configuration", {})
        .get("device", {})
        .get("role"),
        available_fn=lambda data: "configuration" in data,
    ),
    EmlidSensorEntityDescription(
        key="firmware",
        translation_key="firmware",
        name="Firmware Version",
        icon="mdi:chip",
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.get("device_info", {})
        .get("device", {})
        .get("app_version"),
        available_fn=lambda data: "device_info" in data,
    ),
    EmlidSensorEntityDescription(
        key="satellite_observations",
        translation_key="satellite_observations",
        name="Satellite Observations",
        icon="mdi:satellite-variant",
        entity_registry_enabled_default=False,
        value_fn=lambda data: len(
            data.get("satellite_observations", {}).get("rover_satellites", [])
        ),
        available_fn=lambda data: "satellite_observations" in data,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EmlidConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Emlid sensors from a config entry."""
    coordinator = config_entry.runtime_data.coordinator

    entities = [
        EmlidSensor(coordinator, description, config_entry)
        for description in SENSOR_DESCRIPTIONS
    ]

    async_add_entities(entities)


class EmlidSensor(CoordinatorEntity[EmlidDataUpdateCoordinator], SensorEntity):
    """Representation of an Emlid sensor."""

    entity_description: EmlidSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EmlidDataUpdateCoordinator,
        description: EmlidSensorEntityDescription,
        config_entry: EmlidConfigEntry,
    ) -> None:
        """Initialize the sensor."""
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
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.entity_description.available_fn(self.coordinator.data)
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        # Add detailed satellite observation data as attributes for the satellite_observations sensor
        if self.entity_description.key == "satellite_observations":
            obs_data = self.coordinator.data.get("satellite_observations", {})
            return {
                "satellites_count": obs_data.get("satellites_count", {}),
                "rover_satellites": obs_data.get("rover_satellites", []),
                "base_satellites": obs_data.get("base_satellites", []),
                "by_constellation": obs_data.get("by_constellation", {}),
                "satellite_trails": obs_data.get("satellite_trails", {}),
                "timestamp": obs_data.get("timestamp"),
            }
        return None
