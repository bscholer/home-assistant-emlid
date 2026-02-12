# Emlid GNSS Home Assistant Integration

This custom integration allows you to monitor your Emlid GNSS receivers (Reach RS4, etc.) in Home Assistant with real-time positioning data.

## Features

- **Real-time GPS Tracking**: Monitor position with centimeter-level RTK accuracy
- **RTK Solution Status**: Track fix quality (RTK fix, float, single, no solution)
- **Battery Monitoring**: Battery level, voltage, current, and temperature
- **Satellite Information**: Number of satellites and signal quality (DOP)
- **Baseline Distance**: Distance to RTK base station
- **Communication Status**: LoRa, WiFi, and Bluetooth monitoring
- **Device Tracker**: Show device location on Home Assistant map
- **Configurable Update Rate**: Control WebSocket data frequency (default 1Hz)

## Supported Devices

- Emlid Reach RS4
- Potentially compatible with Reach RS2/RS3 (untested)

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots in the top right → "Custom repositories"
3. Add `https://github.com/bscholer/home-assistant-emlid` as an Integration
4. Click "Explore & Download Repositories"
5. Search for "Emlid GNSS"
6. Click "Download"
7. Restart Home Assistant
8. Go to Settings → Devices & Services → Add Integration
9. Search for "Emlid GNSS"

### Manual Installation

1. Copy the `custom_components/emlid` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Emlid GNSS"

## Configuration

The integration is configured through the UI:

1. **Host**: IP address or hostname of your Emlid device (e.g., `192.168.1.21` or `reach.local`)
2. **Update Rate**: WebSocket data throttling in Hz (default: 1Hz, range: 0.2-10Hz)
   - 1Hz recommended for most users
   - 0.2Hz (5 seconds) for minimal database impact
   - Higher rates available for advanced automations

## Entities Created

### Sensors

#### Position & Navigation
- `sensor.emlid_solution` - RTK solution status (fix/float/single/no_solution)
- `sensor.emlid_latitude` - Current latitude (degrees)
- `sensor.emlid_longitude` - Current longitude (degrees)
- `sensor.emlid_altitude` - Current altitude (meters)
- `sensor.emlid_horizontal_accuracy` - Horizontal accuracy (meters)
- `sensor.emlid_vertical_accuracy` - Vertical accuracy (meters)
- `sensor.emlid_baseline` - Distance to base station (meters)
- `sensor.emlid_positioning_mode` - Operating mode (kinematic/static/stop-and-go)

#### Satellites & Signal Quality
- `sensor.emlid_satellites_rover` - Number of satellites tracked
- `sensor.emlid_satellites_valid` - Number of satellites used in solution
- `sensor.emlid_hdop` - Horizontal dilution of precision

#### Battery & Power
- `sensor.emlid_battery` - Battery level (%)
- `sensor.emlid_battery_voltage` - Battery voltage (V)
- `sensor.emlid_battery_current` - Battery current (A)
- `sensor.emlid_battery_temperature` - Battery temperature (°C)
- `sensor.emlid_charging_status` - Charging state
- `binary_sensor.emlid_usb_power` - USB power connected
- `binary_sensor.emlid_battery_present` - Battery detected

#### Communication
- `binary_sensor.emlid_lora_connected` - LoRa radio connection
- `sensor.emlid_lora_rssi` - LoRa signal strength (dBm)
- `binary_sensor.emlid_wifi_connected` - WiFi connection status
- `sensor.emlid_wifi_ssid` - Connected WiFi network
- `sensor.emlid_correction_input_state` - RTCM correction stream status

#### Device Info
- `sensor.emlid_role` - Device role (base/rover)
- `sensor.emlid_firmware` - Firmware version
- `sensor.emlid_model` - Device model

### Device Tracker
- `device_tracker.emlid_location` - GPS location for map display

## Usage Examples

### Automation: High-Accuracy Position Capture
```yaml
automation:
  - alias: "Notify when RTK fixed"
    trigger:
      - platform: state
        entity_id: sensor.emlid_solution
        to: "fix"
    condition:
      - condition: numeric_state
        entity_id: sensor.emlid_horizontal_accuracy
        below: 0.02  # 2cm accuracy
    action:
      - service: notify.mobile_app
        data:
          message: "RTK fix achieved with {{ states('sensor.emlid_horizontal_accuracy') }}m accuracy"
```

### Automation: Low Battery Alert
```yaml
automation:
  - alias: "Emlid low battery"
    trigger:
      - platform: numeric_state
        entity_id: sensor.emlid_battery
        below: 20
    condition:
      - condition: state
        entity_id: sensor.emlid_charging_status
        state: "Discharging"
    action:
      - service: notify.mobile_app
        data:
          message: "Emlid battery low: {{ states('sensor.emlid_battery') }}%"
```

### Automation: RTK Correction Loss
```yaml
automation:
  - alias: "RTK corrections lost"
    trigger:
      - platform: state
        entity_id: sensor.emlid_correction_input_state
        to: "error"
        for: "00:00:30"
    action:
      - service: notify.mobile_app
        data:
          message: "RTK correction stream lost!"
```

## Troubleshooting

### Device Not Found
- Ensure the device is powered on and connected to the network
- Try using the IP address instead of hostname
- Check that the device is accessible: `http://<device_ip>` in a browser

### WebSocket Connection Issues
- The integration requires Socket.IO support
- Check Home Assistant logs for connection errors
- Ensure no firewall is blocking WebSocket connections

### High Database Size
- Reduce the update rate to 0.2Hz (5 seconds)
- Exclude specific entities from recorder in `configuration.yaml`:
  ```yaml
  recorder:
    exclude:
      entities:
        - sensor.emlid_satellites_rover
        - sensor.emlid_hdop
  ```

### Sensors Show "Unavailable"
- Check that the device is online
- Verify WebSocket connection in Home Assistant logs
- Try reloading the integration

## Technical Details

- **Data Sources**:
  - WebSocket (Socket.IO) for real-time telemetry at configurable rates
  - REST API for device configuration (polled every 30 seconds)
- **Update Rate**: Configurable throttling (0.2-10Hz) to balance responsiveness and database size
- **IoT Class**: Local polling + push (WebSocket)
- **Supported Models**: Emlid Reach RS4 (others may work)

## API Information

This integration uses:
- Emlid's WebSocket API for real-time GNSS data
- Emlid's REST API for configuration and status

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

For issues with this integration:
1. Check the Home Assistant logs for detailed error messages
2. Verify device connectivity (`http://<device_ip>`)
3. Create an issue on GitHub with logs and device model

## License

MIT License - see LICENSE file for details
