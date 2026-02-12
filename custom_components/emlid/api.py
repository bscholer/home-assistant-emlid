"""API client for Emlid GNSS devices."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable

import socketio
from aiohttp import ClientSession

from .const import SOCKETIO_PATH, WEBSOCKET_RECONNECT_DELAY, WEBSOCKET_RECONNECT_DELAY_MAX

_LOGGER = logging.getLogger(__name__)


class EmlidAPIError(Exception):
    """Base exception for Emlid API errors."""


class EmlidAPIClient:
    """Client for Emlid REST API."""

    def __init__(self, host: str, session: ClientSession) -> None:
        """Initialize the API client."""
        self.host = host
        self.session = session
        self.base_url = f"http://{host}"

    async def _get(self, endpoint: str) -> dict[str, Any]:
        """Make a GET request to the API."""
        url = f"{self.base_url}{endpoint}"
        try:
            async with self.session.get(url, timeout=10) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as err:
            _LOGGER.error("Error fetching %s: %s", endpoint, err)
            raise EmlidAPIError(f"Failed to fetch {endpoint}") from err

    async def get_info(self) -> dict[str, Any]:
        """Get device information."""
        return await self._get("/info")

    async def get_battery(self) -> dict[str, Any]:
        """Get battery status."""
        return await self._get("/battery")

    async def get_configuration(self) -> dict[str, Any]:
        """Get device configuration."""
        return await self._get("/configuration")

    async def get_wifi_status(self) -> dict[str, Any]:
        """Get WiFi status."""
        return await self._get("/wifi/status")

    async def get_bluetooth_status(self) -> dict[str, Any]:
        """Get Bluetooth status."""
        return await self._get("/bluetooth/status")

    async def get_lora_state(self) -> dict[str, Any]:
        """Get LoRa radio state."""
        return await self._get("/lora/state")

    async def get_lora_rssi(self) -> dict[str, Any]:
        """Get LoRa RSSI."""
        return await self._get("/lora/rssi")


class EmlidWebSocketClient:
    """Client for Emlid WebSocket (Socket.IO) connection."""

    def __init__(self, host: str) -> None:
        """Initialize the WebSocket client."""
        self.host = host
        self.url = f"http://{host}"
        self.sio: socketio.AsyncClient | None = None
        self._callbacks: dict[str, list[Callable]] = {}
        self._connected = False
        self._connect_lock = asyncio.Lock()

    def on(self, event: str, callback: Callable) -> None:
        """Register a callback for a specific event."""
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)

    def _emit_callback(self, event: str, data: Any) -> None:
        """Emit callbacks for an event."""
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                try:
                    callback(data)
                except Exception as err:
                    _LOGGER.error("Error in callback for %s: %s", event, err)

    async def connect(self) -> None:
        """Connect to the WebSocket."""
        async with self._connect_lock:
            if self._connected:
                return

            self.sio = socketio.AsyncClient(
                logger=False,
                engineio_logger=False,
                reconnection=True,
                reconnection_delay=WEBSOCKET_RECONNECT_DELAY,
                reconnection_delay_max=WEBSOCKET_RECONNECT_DELAY_MAX,
            )

            @self.sio.event
            async def connect():
                """Handle connection event."""
                _LOGGER.info("WebSocket connected to %s", self.host)
                self._connected = True

            @self.sio.event
            async def disconnect():
                """Handle disconnection event."""
                _LOGGER.warning("WebSocket disconnected from %s", self.host)
                self._connected = False

            @self.sio.on("broadcast")
            async def on_broadcast(data):
                """Handle broadcast events from device."""
                if isinstance(data, dict) and "name" in data and "payload" in data:
                    event_name = data["name"]
                    payload = data["payload"]
                    self._emit_callback(event_name, payload)

            try:
                await self.sio.connect(
                    self.url,
                    socketio_path=SOCKETIO_PATH,
                    transports=["polling", "websocket"],
                    namespaces=["/"],
                )
                _LOGGER.debug("WebSocket client initialized for %s", self.host)
            except Exception as err:
                _LOGGER.error("Failed to connect WebSocket to %s: %s", self.host, err)
                raise EmlidAPIError("Failed to connect WebSocket") from err

    async def disconnect(self) -> None:
        """Disconnect from the WebSocket."""
        if self.sio and self._connected:
            await self.sio.disconnect()
            self._connected = False
            _LOGGER.info("WebSocket disconnected from %s", self.host)

    @property
    def connected(self) -> bool:
        """Return whether the WebSocket is connected."""
        return self._connected
