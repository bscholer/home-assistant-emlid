"""Data coordinator for Emlid GNSS integration."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, TypedDict

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EmlidAPIClient, EmlidAPIError, EmlidWebSocketClient
from .const import DOMAIN, REST_UPDATE_INTERVAL

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from . import EmlidConfigEntry

_LOGGER = logging.getLogger(__name__)


class NavigationData(TypedDict, total=False):
    """Type for navigation data."""

    solution: str
    latitude: float
    longitude: float
    altitude: float
    horizontal_accuracy: float
    vertical_accuracy: float
    baseline: float
    satellites_rover: int
    satellites_base: int
    satellites_valid: int
    hdop: float
    positioning_mode: str
    velocity_east: float
    velocity_north: float
    velocity_up: float


class BatteryData(TypedDict, total=False):
    """Type for battery data."""

    state_of_charge: int
    voltage: float
    current: float
    temperature: float
    charger_status: str
    usb_charger_current: float | None
    usb_charger_voltage: float | None


class EmlidCoordinatorData(TypedDict, total=False):
    """Type for coordinator data."""

    # From WebSocket (real-time)
    navigation: NavigationData
    battery: BatteryData
    lora_connected: bool
    power_usb_connected: bool
    power_battery_present: bool
    correction_input_state: str
    logging_active: bool
    satellite_observations: dict[str, Any]

    # From REST API (periodic)
    device_info: dict[str, Any]
    configuration: dict[str, Any]
    wifi_status: dict[str, Any]
    bluetooth_status: dict[str, Any]
    lora_rssi: int


class EmlidDataUpdateCoordinator(DataUpdateCoordinator[EmlidCoordinatorData]):
    """Class to manage fetching Emlid data."""

    config_entry: EmlidConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: EmlidConfigEntry,
        api_client: EmlidAPIClient,
        ws_client: EmlidWebSocketClient,
        update_rate: float,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger=_LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=REST_UPDATE_INTERVAL),
        )
        self.api_client = api_client
        self.ws_client = ws_client
        self.update_rate = update_rate
        self._throttle_interval = timedelta(seconds=1.0 / update_rate)
        self._last_update: dict[str, datetime] = {}

        # Current data (updated by WebSocket)
        self._ws_data: EmlidCoordinatorData = {}

        # Satellite position history for trails (last 20 positions per satellite)
        self._satellite_trails: dict[str, list[dict[str, Any]]] = {}
        self._max_trail_length = 20

        # Register WebSocket callbacks
        self.ws_client.on("navigation", self._handle_navigation)
        self.ws_client.on("battery_status", self._handle_battery)
        self.ws_client.on("lora_state", self._handle_lora_state)
        self.ws_client.on("power_supply_status", self._handle_power_supply)
        self.ws_client.on("stream_status", self._handle_stream_status)
        self.ws_client.on("active_logs", self._handle_active_logs)
        self.ws_client.on("observations", self._handle_observations)

    def _should_update(self, key: str, interval: timedelta | None = None) -> bool:
        """Check if enough time has passed for throttled update.

        Args:
            key: The throttle key to check
            interval: Optional custom interval, defaults to self._throttle_interval
        """
        now = datetime.now()
        check_interval = interval or self._throttle_interval
        if key not in self._last_update:
            self._last_update[key] = now
            return True
        if now - self._last_update[key] >= check_interval:
            self._last_update[key] = now
            return True
        return False

    def _handle_navigation(self, data: dict[str, Any]) -> None:
        """Handle navigation event from WebSocket."""
        if not self._should_update("navigation"):
            return

        nav_data: NavigationData = {
            "solution": data.get("solution", "no_solution"),
            "positioning_mode": data.get("positioning_mode", "unknown"),
            "baseline": data.get("baseline", 0.0),
            "hdop": data.get("dop", {}).get("h", 0.0),
        }

        # Satellites
        satellites = data.get("satellites", {})
        nav_data["satellites_rover"] = satellites.get("rover", 0)
        nav_data["satellites_base"] = satellites.get("base", 0)
        nav_data["satellites_valid"] = satellites.get("valid", 0)

        # Position
        rover_pos = data.get("rover_position", {})
        coords = rover_pos.get("coordinates", {})
        nav_data["latitude"] = coords.get("lat", 0.0)
        nav_data["longitude"] = coords.get("lon", 0.0)
        nav_data["altitude"] = coords.get("h", 0.0)

        # Accuracy
        accuracy = rover_pos.get("accuracy", {})
        # Horizontal accuracy is the RMS of east and north
        e_acc = accuracy.get("e", 0.0)
        n_acc = accuracy.get("n", 0.0)
        nav_data["horizontal_accuracy"] = (e_acc**2 + n_acc**2) ** 0.5
        nav_data["vertical_accuracy"] = accuracy.get("u", 0.0)

        # Velocity
        velocity = data.get("velocity", {})
        nav_data["velocity_east"] = velocity.get("e", 0.0)
        nav_data["velocity_north"] = velocity.get("n", 0.0)
        nav_data["velocity_up"] = velocity.get("u", 0.0)

        self._ws_data["navigation"] = nav_data
        self.async_set_updated_data(self._merge_data())

    def _handle_battery(self, data: dict[str, Any]) -> None:
        """Handle battery_status event from WebSocket."""
        if not self._should_update("battery"):
            return

        battery_data: BatteryData = {
            "state_of_charge": data.get("state_of_charge", 0),
            "voltage": data.get("voltage", 0.0),
            "current": data.get("current", 0.0),
            "temperature": data.get("temperature", 0.0),
            "charger_status": data.get("charger_status", "Unknown"),
            "usb_charger_current": data.get("usb_charger_current"),
            "usb_charger_voltage": data.get("usb_charger_voltage"),
        }

        self._ws_data["battery"] = battery_data
        self.async_set_updated_data(self._merge_data())

    def _handle_lora_state(self, data: dict[str, Any]) -> None:
        """Handle lora_state event from WebSocket."""
        self._ws_data["lora_connected"] = data.get("connected", False)
        self.async_set_updated_data(self._merge_data())

    def _handle_power_supply(self, data: dict[str, Any]) -> None:
        """Handle power_supply_status event from WebSocket."""
        self._ws_data["power_usb_connected"] = data.get("usb_cable_status", False)
        self._ws_data["power_battery_present"] = data.get("battery_status", False)
        self.async_set_updated_data(self._merge_data())

    def _handle_stream_status(self, data: dict[str, Any]) -> None:
        """Handle stream_status event from WebSocket."""
        correction_input = data.get("correction_input", [])
        if correction_input and len(correction_input) > 0:
            state = correction_input[0].get("state", "unknown")
            self._ws_data["correction_input_state"] = state
            self.async_set_updated_data(self._merge_data())

    def _handle_active_logs(self, data: dict[str, Any]) -> None:
        """Handle active_logs event from WebSocket."""
        # Check if any log is actively writing
        is_logging = False
        for log_type in ["raw", "solution", "base"]:
            if log_type in data:
                if data[log_type].get("is_writing", False):
                    is_logging = True
                    break

        self._ws_data["logging_active"] = is_logging
        self.async_set_updated_data(self._merge_data())

    def _handle_observations(self, data: dict[str, Any]) -> None:
        """Handle observations event from WebSocket."""
        # Process and structure satellite observation data
        observations = {
            "satellites_count": data.get("satellites_count", {}),
            "rover_satellites": data.get("satellites", {}).get("rover", []),
            "base_satellites": data.get("satellites", {}).get("base", []),
            "timestamp": datetime.now().isoformat(),
        }

        # Group satellites by constellation
        constellations = {"GPS": [], "GLONASS": [], "Galileo": [], "BeiDou": [], "QZSS": [], "SBAS": []}
        for sat in observations["rover_satellites"]:
            sat_id = sat.get("satellite_index", "")
            if sat_id.startswith("G"):
                constellations["GPS"].append(sat)
            elif sat_id.startswith("R"):
                constellations["GLONASS"].append(sat)
            elif sat_id.startswith("E"):
                constellations["Galileo"].append(sat)
            elif sat_id.startswith("C"):
                constellations["BeiDou"].append(sat)
            elif sat_id.startswith("J"):
                constellations["QZSS"].append(sat)
            elif sat_id.startswith("S"):
                constellations["SBAS"].append(sat)

        observations["by_constellation"] = constellations

        # Update satellite trails (position history for sky plot)
        # Only update trails every 60 seconds to show meaningful movement
        # 20 points × 60 seconds = 20 minutes of satellite movement history
        if self._should_update("satellite_trails", timedelta(seconds=60)):
            for sat in observations["rover_satellites"]:
                sat_id = sat.get("satellite_index", "")
                if sat_id:
                    # Initialize trail if needed
                    if sat_id not in self._satellite_trails:
                        self._satellite_trails[sat_id] = []

                    # Add current position to trail
                    self._satellite_trails[sat_id].append({
                        "azimuth": sat.get("azimuth", 0),
                        "elevation": sat.get("elevation", 0),
                        "snr": sat.get("signal_to_noise_ratio", 0),
                        "timestamp": datetime.now().isoformat(),
                    })

                    # Keep only last N positions
                    if len(self._satellite_trails[sat_id]) > self._max_trail_length:
                        self._satellite_trails[sat_id] = self._satellite_trails[sat_id][-self._max_trail_length:]

            # Clean up trails for satellites no longer visible
            current_sat_ids = {sat.get("satellite_index") for sat in observations["rover_satellites"]}
            trails_to_remove = [sat_id for sat_id in self._satellite_trails if sat_id not in current_sat_ids]
            for sat_id in trails_to_remove:
                del self._satellite_trails[sat_id]

        # Add trails to observations
        observations["satellite_trails"] = self._satellite_trails

        self._ws_data["satellite_observations"] = observations
        self.async_set_updated_data(self._merge_data())

    def _merge_data(self) -> EmlidCoordinatorData:
        """Merge WebSocket data with REST data."""
        # Start with REST data if available
        merged = self.data.copy() if self.data else {}
        # Overlay WebSocket data
        merged.update(self._ws_data)
        return merged

    async def _async_update_data(self) -> EmlidCoordinatorData:
        """Fetch data from REST API (periodic polling)."""
        try:
            async with asyncio.TaskGroup() as tg:
                info_task = tg.create_task(self.api_client.get_info())
                config_task = tg.create_task(self.api_client.get_configuration())
                wifi_task = tg.create_task(self.api_client.get_wifi_status())
                bluetooth_task = tg.create_task(self.api_client.get_bluetooth_status())
                lora_rssi_task = tg.create_task(self.api_client.get_lora_rssi())

            rest_data: EmlidCoordinatorData = {
                "device_info": info_task.result(),
                "configuration": config_task.result(),
                "wifi_status": wifi_task.result(),
                "bluetooth_status": bluetooth_task.result(),
                "lora_rssi": lora_rssi_task.result().get("rssi", -1),
            }

            # Merge with WebSocket data
            return {**rest_data, **self._ws_data}

        except EmlidAPIError as err:
            raise UpdateFailed(f"Error communicating with Emlid device: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err
