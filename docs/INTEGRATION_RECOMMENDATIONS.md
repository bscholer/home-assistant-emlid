# Emlid RS4 GNSS Home Assistant Integration Recommendations

## Data Sources Overview

### 1. WebSocket (Real-time, 5-10Hz updates)
The WebSocket connection broadcasts real-time telemetry at high frequency via Socket.IO at `http://<device_ip>/socket.io/`.

**Event Types:**
- `navigation` - Primary positioning data
- `battery_status` - Battery telemetry
- `power_supply_status` - Power source status
- `lora_state` - LoRa radio connection
- `observations` - Detailed satellite visibility/signal
- `active_logs` - Data logging status
- `stream_status` - RTCM correction stream status
- `notifications` - System notifications

### 2. REST API (Configuration & Status)
HTTP endpoints for device configuration and less-frequently-changing data.

**Key Endpoints:**
- `GET /info` - Device information, firmware version, model
- `GET /configuration` - Full device configuration
- `GET /battery` - Battery status snapshot
- `GET /wifi/status` - Network connection info
- `GET /lora/state` & `/lora/rssi` - LoRa radio status
- `GET /bluetooth/status` - Bluetooth status
- `GET /modem/1/settings` - Cellular modem configuration
- `POST /configuration/device` - Device settings (role, antenna height, etc.)
- `POST /configuration/positioning_settings` - GNSS positioning parameters

---

## Recommended Home Assistant Entities

### 🌍 Core Navigation Entities (from WebSocket `navigation`)

#### Sensors (High Priority)
1. **GPS Solution Status** (`sensor.emlid_rs4_solution`)
   - Values: `fix`, `float`, `single`, `no_solution`
   - Update: Real-time from WebSocket
   - **Critical** - Shows positioning quality (RTK fix is best)

2. **Position (Latitude)** (`sensor.emlid_rs4_latitude`)
   - Unit: degrees
   - Precision: ~10 decimal places
   - Update: Real-time (but throttle to 1Hz for HASS recorder)

3. **Position (Longitude)** (`sensor.emlid_rs4_longitude`)
   - Unit: degrees
   - Precision: ~10 decimal places
   - Update: Real-time (throttled to 1Hz)

4. **Position (Altitude)** (`sensor.emlid_rs4_altitude`)
   - Unit: meters
   - Shows height above ellipsoid/mean sea level
   - Update: Real-time (throttled to 1Hz)

5. **Horizontal Accuracy** (`sensor.emlid_rs4_horizontal_accuracy`)
   - Unit: meters
   - Shows position accuracy (typically 0.01m in RTK fix mode)
   - **Important** - Indicates solution quality

6. **Vertical Accuracy** (`sensor.emlid_rs4_vertical_accuracy`)
   - Unit: meters
   - Vertical position accuracy

7. **Baseline Distance** (`sensor.emlid_rs4_baseline`)
   - Unit: meters
   - Distance to base station (RTK correction source)
   - Useful for troubleshooting RTK corrections

8. **Satellite Count (Rover)** (`sensor.emlid_rs4_satellites_rover`)
   - Number of satellites tracked by rover
   - Indicator of sky visibility

9. **Satellite Count (Valid)** (`sensor.emlid_rs4_satellites_valid`)
   - Number of satellites used in solution
   - **Important** - More satellites = better solution

10. **HDOP (Horizontal Dilution of Precision)** (`sensor.emlid_rs4_hdop`)
    - Dimensionless (lower is better, <1.5 is excellent)
    - Geometric quality indicator

11. **Positioning Mode** (`sensor.emlid_rs4_positioning_mode`)
    - Values: `kinematic`, `static`, `stop-and-go`
    - Shows current operating mode

#### Device Tracker (Optional but Cool)
12. **GPS Device Tracker** (`device_tracker.emlid_rs4`)
    - Uses lat/lon from navigation data
    - Shows device location on map
    - Update frequency configurable (recommend 1-5 seconds)

### 🔋 Power & Battery Entities (from WebSocket `battery_status`)

13. **Battery Level** (`sensor.emlid_rs4_battery`)
    - Unit: %
    - State of charge (0-100%)
    - Device class: `battery`

14. **Battery Voltage** (`sensor.emlid_rs4_battery_voltage`)
    - Unit: V
    - Typical range: 6-9V for 2S battery

15. **Battery Current** (`sensor.emlid_rs4_battery_current`)
    - Unit: A
    - Positive when charging, negative when discharging

16. **Battery Temperature** (`sensor.emlid_rs4_battery_temperature`)
    - Unit: °C
    - Device class: `temperature`
    - Monitoring for safety

17. **Charging Status** (`sensor.emlid_rs4_charging_status`)
    - Values: `Charging`, `Discharging`, `Full`, etc.
    - State indicator

#### Binary Sensors
18. **USB Power Connected** (`binary_sensor.emlid_rs4_usb_power`)
    - From `power_supply_status.usb_cable_status`
    - Device class: `plug`

19. **Battery Present** (`binary_sensor.emlid_rs4_battery_present`)
    - From `power_supply_status.battery_status`
    - Device class: `battery`

### 📡 Communication Status

20. **LoRa Connection** (`binary_sensor.emlid_rs4_lora_connected`)
    - From WebSocket `lora_state.connected`
    - Shows if LoRa radio is connected
    - Device class: `connectivity`

21. **LoRa RSSI** (`sensor.emlid_rs4_lora_rssi`)
    - Unit: dBm
    - From REST `/lora/rssi` (periodic polling)
    - Signal strength indicator
    - Device class: `signal_strength`

22. **WiFi Connection Status** (`binary_sensor.emlid_rs4_wifi_connected`)
    - From REST `/wifi/status`
    - Device class: `connectivity`

23. **WiFi SSID** (`sensor.emlid_rs4_wifi_ssid`)
    - From REST `/wifi/status.current_network.ssid`
    - Shows connected network name

24. **WiFi IP Address** (`sensor.emlid_rs4_ip_address`)
    - From REST `/wifi/status.current_network.ip`

25. **Bluetooth Status** (`binary_sensor.emlid_rs4_bluetooth_enabled`)
    - From REST `/bluetooth/status.enabled`
    - Device class: `connectivity`

### 📊 RTCM Correction Stream Status (from WebSocket `stream_status`)

26. **Correction Input State** (`sensor.emlid_rs4_correction_input_state`)
    - Values: `active`, `inactive`, `error`
    - Shows if receiving RTK corrections
    - **Critical** - Must be active for RTK fix

27. **RTCM Message Count** (`sensor.emlid_rs4_rtcm_message_count`)
    - Total number of RTCM messages received
    - Could track specific message types (1074, 1084, 1094, etc.)

### 📝 Data Logging Status (from WebSocket `active_logs`)

28. **Logging Active** (`binary_sensor.emlid_rs4_logging_active`)
    - Shows if any logs are being recorded
    - From `active_logs.*.is_writing`

29. **Log Recording Time** (`sensor.emlid_rs4_log_recording_time`)
    - Unit: seconds
    - Duration of current log session

30. **Log Remaining Time** (`sensor.emlid_rs4_log_remaining_time`)
    - Unit: seconds
    - Time until storage full

### ℹ️ Device Information (from REST `/info`)

31. **Device Model** (`sensor.emlid_rs4_model`)
    - Value: "Reach RS4"
    - From `/info.device.model`

32. **Firmware Version** (`sensor.emlid_rs4_firmware`)
    - From `/info.device.app_version`

33. **Serial Number** (`sensor.emlid_rs4_serial`)
    - From `/info.device.serial_number`

34. **Uptime** (`sensor.emlid_rs4_uptime`)
    - Unit: seconds
    - Device uptime (if available in API)

### 🎯 Configuration Attributes (from REST `/configuration`)

35. **Device Role** (`sensor.emlid_rs4_role`)
    - Values: `base`, `rover`
    - From `/configuration/device.role`

36. **Antenna Height** (`sensor.emlid_rs4_antenna_height`)
    - Unit: meters
    - From `/configuration/device.antenna_height`

37. **Positioning Mode Config** (`sensor.emlid_rs4_positioning_mode_config`)
    - From `/configuration/positioning_settings.positioning_mode`

---

## Implementation Architecture Recommendations

### WebSocket Handling
- **Connection**: Use `python-socketio` library (already in `listen.py`)
- **Update Frequency**:
  - Receive at 5-10Hz from device
  - **Throttle to 1Hz** for most sensors before updating Home Assistant
  - Use configurable throttling for position updates to avoid flooding recorder
- **Events to Subscribe**:
  - `navigation` (highest priority)
  - `battery_status`
  - `lora_state`
  - `stream_status`
  - `active_logs`
  - `observations` (optional, for advanced users)

### REST API Polling
- **Poll Frequency**:
  - Device info: Once at startup, or every 5 minutes
  - WiFi/Bluetooth status: Every 30-60 seconds
  - LoRa RSSI: Every 10-15 seconds
  - Battery: Every 30 seconds (or rely on WebSocket)
- **Error Handling**: Graceful degradation if REST endpoints unavailable

### Data Processing
1. **Throttling**: Implement configurable throttle for high-frequency WebSocket data
   - Default: 1Hz for position/navigation sensors
   - Option: 0.2Hz (every 5 seconds) for very low-bandwidth setups
   - Raw data available via WebSocket for automations that need it

2. **State Management**:
   - Track last known good values
   - Mark sensors as "unavailable" if no updates for >30 seconds
   - Handle reconnection logic for WebSocket

3. **Precision**:
   - Round lat/lon to 10 decimal places (~1cm precision)
   - Round accuracy values to 3 decimal places (mm)

### Configuration Options
Users should be able to configure:
- Device IP address
- Update frequency throttling (0.2Hz - 10Hz)
- Which entities to enable/disable
- Altitude reference (ellipsoid vs MSL if device supports it)

---

## Priority Ranking

### Must-Have (Core Functionality)
1. GPS Solution Status
2. Latitude/Longitude
3. Altitude
4. Horizontal/Vertical Accuracy
5. Baseline Distance
6. Satellite counts
7. Battery Level
8. Correction Input State

### Should-Have (Enhanced Monitoring)
9. HDOP
10. Positioning Mode
11. Battery Voltage/Current/Temperature
12. Charging Status
13. LoRa Connection Status
14. WiFi Connection Status
15. Device Role
16. Firmware Version

### Nice-to-Have (Advanced Users)
17. RTCM Message Counts
18. Logging Status
19. LoRa RSSI
20. Bluetooth Status
21. Satellite observations (detailed signal quality)
22. Device Tracker entity
23. WiFi SSID/IP

---

## Notes on Recorder Impact

**Warning**: The WebSocket sends data at 5-10Hz (5-10 updates per second). This will **overwhelm** the Home Assistant recorder if not throttled.

**Recommendations**:
1. Throttle all WebSocket-derived sensors to **1Hz maximum** by default
2. Add option to reduce to 0.2Hz (every 5 seconds) for users concerned about database size
3. Consider excluding some high-frequency sensors from recorder entirely:
   ```yaml
   recorder:
     exclude:
       entities:
         - sensor.emlid_rs4_satellites_rover
         - sensor.emlid_rs4_hdop
         # etc.
   ```
4. For device_tracker, use a reasonable update interval (5-10 seconds)

---

## Example Automation Ideas

Once integrated, users could create automations like:

- **Survey Point Capture**: Notify when solution is "fix" with accuracy <0.02m
- **Low Battery Alert**: Notification when battery <20% and discharging
- **RTK Correction Loss**: Alert when correction input state goes to "error" or "inactive"
- **Baseline Warning**: Alert if baseline >20km (may affect RTK accuracy)
- **Data Logging**: Automatically start logging when solution reaches RTK fix
- **Presence Detection**: Use device_tracker to know when surveying equipment is at job site

---

## Technical Implementation Notes

### WebSocket Connection
```python
import socketio

sio = socketio.Client(
    reconnection=True,
    reconnection_attempts=0,  # Infinite
    reconnection_delay=1,
    reconnection_delay_max=5,
)

@sio.on('broadcast')
def on_broadcast(data):
    event_name = data['name']
    payload = data['payload']
    # Handle different event types
    if event_name == 'navigation':
        handle_navigation(payload)
    elif event_name == 'battery_status':
        handle_battery(payload)
    # etc...

sio.connect('http://192.168.1.21', socketio_path='/socket.io')
```

### Throttling Strategy
```python
from datetime import datetime, timedelta

class ThrottledSensor:
    def __init__(self, min_interval=1.0):
        self.min_interval = timedelta(seconds=min_interval)
        self.last_update = None

    def should_update(self):
        now = datetime.now()
        if self.last_update is None:
            self.last_update = now
            return True
        if now - self.last_update >= self.min_interval:
            self.last_update = now
            return True
        return False
```

---

## Questions for User

Before finalizing the integration, consider:

1. **Update Frequency**: What's the preferred default throttle rate? (1Hz, 0.5Hz, 0.2Hz?)
2. **Entity Selection**: Should all entities be enabled by default, or opt-in?
3. **Device Discovery**: Should we support automatic discovery via mDNS/zeroconf?
4. **Multiple Devices**: Should the integration support multiple Emlid receivers on same network?
5. **Authentication**: Does the device support any authentication? (doesn't appear to from HAR file)
6. **Base Station Mode**: Should we add special entities when device is in "base" mode vs "rover" mode?
