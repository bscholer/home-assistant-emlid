"""Constants for the Emlid GNSS integration."""

from __future__ import annotations

from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "emlid"
PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.DEVICE_TRACKER,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SELECT,
]

# Configuration
CONF_HOST: Final = "host"
CONF_UPDATE_RATE: Final = "update_rate"

# Default values
DEFAULT_UPDATE_RATE: Final = 1.0  # Hz
MIN_UPDATE_RATE: Final = 0.2  # Hz (5 seconds)
MAX_UPDATE_RATE: Final = 10.0  # Hz

# REST API polling interval (handled by Home Assistant coordinator)
# Default 30 seconds is fine for configuration data
REST_UPDATE_INTERVAL: Final = 30

# WebSocket connection
SOCKETIO_PATH: Final = "/socket.io"
WEBSOCKET_RECONNECT_DELAY: Final = 1
WEBSOCKET_RECONNECT_DELAY_MAX: Final = 5

# Device info
MANUFACTURER: Final = "Emlid"
