# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-02-13

### Added
- Initial release
- WebSocket support for real-time GNSS data
- REST API support for device configuration and status
- Configurable update rate for WebSocket data (default 1Hz)
- GPS position tracking (latitude, longitude, altitude)
- RTK solution status monitoring
- Battery monitoring sensors
- Satellite count and signal quality sensors
- LoRa radio status
- WiFi connection status
- Device tracker for map integration
- Support for both Base and Rover modes
- **Control entities** for device configuration:
  - Switch: Night mode, data logging, GNSS systems (GPS/GLONASS/Galileo/BeiDou/QZSS)
  - Number: Antenna height, update rate, elevation mask, SNR mask, acceleration limits
  - Select: Positioning mode, GPS AR mode
- Read-modify-write pattern to safely update settings without overwriting other fields
