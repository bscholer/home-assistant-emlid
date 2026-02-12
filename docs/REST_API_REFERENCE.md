# REST API Reference

This document details the HTTP REST endpoints available on the Emlid RS4 GNSS receiver.

## Base URL

All endpoints are relative to: `http://<device_ip>/`

Example: `http://192.168.1.21/info`

## Authentication

Based on the captured traffic, **no authentication** appears to be required for local network access.

---

## Endpoints

### Device Information

#### GET `/info`
Returns comprehensive device information including model, firmware, serial number, and features.

**Response Example** (partial):
```json
{
  "device": {
    "cloud": {
      "supported": true,
      "usage_analysis_accepted": true
    },
    "country_code": "US",
    "critical_self_tests_passed": true,
    "app_version": "35.0",
    "model": "Reach RS4",
    "serial_number": "82435CF0A23977CB"
  }
}
```

**Use Case**: Read once on startup for device identification.

---

#### GET `/device`
Returns basic device information (subset of `/info`).

---

### Configuration

#### GET `/configuration`
Returns the complete device configuration including positioning settings, base mode, logging, and I/O settings.

**Response Example** (partial):
```json
{
  "base_mode": {
    "base_coordinates": {
      "accumulation": 120,
      "antenna_offset": 1.895,
      "coordinates": {
        "height": 0,
        "latitude": 0,
        "longitude": 0
      }
    }
  },
  "positioning_settings": {
    "elevation_mask_angle": 15,
    "glonass_ar_mode": false,
    "gnss_settings": {
      "positioning_systems": {
        "beidou": true,
        "galileo": true,
        "glonass": true,
        "gps": true,
        "qzss": true
      },
      "update_rate": 5
    },
    "gps_ar_mode": "fix-and-hold",
    "positioning_mode": "kinematic"
  }
}
```

**Use Case**: Read configuration state, especially device role and positioning mode.

---

#### GET `/configuration/device`
Returns device-specific configuration settings.

**Response Example**:
```json
{
  "antenna_height": 1.895,
  "night_mode": false,
  "onboarding_shown": false,
  "power_on_bottom_connector": true,
  "privacy_policy_accepted": true,
  "quick_release_v1": false,
  "role": "base",
  "usage_analysis_accepted": true
}
```

**Fields**:
- `role`: `"base"` or `"rover"`
- `antenna_height`: Antenna height above mark (meters)
- `night_mode`: UI night mode enabled
- `power_on_bottom_connector`: Enable power to bottom connector

---

#### POST `/configuration/device`
Update device configuration settings.

**Request Body**: Same as GET response
**Response**: Updated configuration

---

#### GET `/configuration/positioning_settings`
Returns positioning/GNSS configuration.

**Response Example**:
```json
{
  "elevation_mask_angle": 15,
  "glonass_ar_mode": false,
  "gnss_settings": {
    "positioning_systems": {
      "beidou": true,
      "galileo": true,
      "glonass": true,
      "gps": true,
      "qzss": true
    },
    "update_rate": 5
  },
  "gps_ar_mode": "fix-and-hold",
  "max_horizontal_acceleration": 1.0,
  "max_vertical_acceleration": 1.0,
  "positioning_mode": "kinematic",
  "snr_mask": 35,
  "tilt_compensation": {
    "enabled": false
  }
}
```

**Fields**:
- `update_rate`: GNSS update rate (Hz), typically 1, 5, or 10
- `positioning_mode`: `"kinematic"`, `"static"`, or `"stop-and-go"`
- `gps_ar_mode`: `"fix-and-hold"` or `"continuous"`
- `elevation_mask_angle`: Minimum satellite elevation (degrees)
- `snr_mask`: Minimum signal-to-noise ratio (dB-Hz)

---

#### POST `/configuration/positioning_settings`
Update positioning configuration.

---

#### GET `/configuration/sound/`
Returns sound/audio settings.

---

#### GET `/configuration/constraints`
Returns constraints/limits for configuration values (min/max frequencies, power levels, etc.).

**Response Example** (partial):
```json
{
  "lora": {
    "frequency": [
      [902000, 928000]
    ]
  },
  "uhf_radio": {
    "frequency": [
      [410000000, 470000000]
    ],
    "power": [[500, 1000, 2000]]
  }
}
```

**Use Case**: Validate configuration values before setting.

---

#### GET `/configuration/constraints/uhf_radio`
Returns UHF radio specific constraints.

---

#### GET `/configuration/base_mode/averager_state`
Returns the state of base coordinate averaging process.

**Response Example**:
```json
{
  "payload": {
    "progress": 8,
    "remaining_time": 110,
    "required_solution_status": "SINGLE",
    "state": "accumulating",
    "total_time": 120
  },
  "state": "in_progress"
}
```

**States**:
- `"not_started"` - Not averaging
- `"accumulating"` - Currently averaging
- `"completed"` - Averaging finished

**Use Case**: Monitor base station coordinate averaging progress.

---

### Battery & Power

#### GET `/battery`
Returns current battery status snapshot (alternative to WebSocket).

**Response Example**:
```json
{
  "charger_status": "Discharging",
  "current": -0.28,
  "otg": false,
  "state_of_charge": 81,
  "temperature": 26.2,
  "usb_charger_current": null,
  "usb_charger_voltage": null,
  "voltage": 8.17
}
```

**Use Case**: Fallback if WebSocket unavailable, or for initial state.

---

### Network & Connectivity

#### GET `/wifi/status`
Returns WiFi connection status.

**Response Example**:
```json
{
  "current_network": {
    "ip": "192.168.1.21",
    "security": "wpa-psk",
    "ssid": "GooseNet"
  },
  "enabled": true,
  "mode": "client"
}
```

**Fields**:
- `mode`: `"client"` (connected to network) or `"hotspot"` (AP mode)
- `enabled`: WiFi radio enabled
- `current_network`: null if not connected

---

#### GET `/wifi/hotspot`
Returns WiFi hotspot (AP mode) configuration.

**Response Example**:
```json
{
  "old_ssid": null,
  "password": "emlidreach",
  "ssid": "Reach:77:CB"
}
```

---

#### GET `/wifi/networks`
Returns list of available WiFi networks (scan results).

---

#### GET `/bluetooth/status`
Returns Bluetooth adapter status.

**Response Example**:
```json
{
  "enabled": true,
  "mac_address": "80:A1:97:5C:53:78",
  "name": "Reach"
}
```

---

#### GET `/bluetooth/devices`
Returns paired and connected Bluetooth devices.

**Response Example**:
```json
{
  "connected": [],
  "paired": []
}
```

---

#### GET `/modem/1/settings`
Returns cellular modem configuration.

**Response Example**:
```json
{
  "authentication": {
    "apn": "",
    "password": "",
    "type": null,
    "username": ""
  },
  "autoconnect": true,
  "data_sharing": false,
  "gsm_upgrades": false,
  "operator": null
}
```

---

#### GET `/modem/1/info`
Returns cellular modem information (model, signal strength, etc.).

---

### Radio Communication

#### GET `/lora/state`
Returns LoRa radio connection state.

**Response Example**:
```json
{
  "connected": true
}
```

**Use Case**: Check if LoRa radio is connected (receiving/transmitting).

---

#### GET `/lora/rssi`
Returns LoRa radio signal strength.

**Response Example**:
```json
{
  "rssi": -1,
  "signal_quality": -1
}
```

**Note**: `-1` typically means no signal or not applicable.

**Use Case**: Monitor LoRa link quality.

---

#### GET `/uhf_radio/rssi`
Returns UHF radio signal strength.

**Response Example**:
```json
{
  "rssi": -1,
  "signal_quality": -1
}
```

---

### Data Logging

#### GET `/logs`
Returns list of stored log files.

**Query Parameters**:
- `page`: Page number (default: 1)
- `limit`: Results per page (default: 50)
- `since`: Start timestamp (Unix time)
- `to`: End timestamp (Unix time)

**Example URL**:
```
GET /logs?page=1&limit=50&since=978307200&to=2147483647
```

---

### Surveying & Projects

#### GET `/surveying/projects_exporter_state`
Returns project export/download status.

**Response Example**:
```json
{
  "payload": {
    "progress": 100,
    "state": "no_data"
  },
  "state": "completed"
}
```

**States**:
- `"not_started"`
- `"in_progress"`
- `"completed"`
- `"no_data"`

---

### Firmware Updates

#### GET `/updater`
Returns updater/firmware manager status.

---

#### GET `/updater/upgrade_state`
Returns firmware upgrade status.

**Response Example**:
```json
{
  "is_upgraded": false,
  "new_version": null,
  "payload": null,
  "upgrade_task_state": "not_started"
}
```

**States**:
- `"not_started"`
- `"checking"`
- `"downloading"`
- `"upgrading"`
- `"completed"`

**Use Case**: Monitor firmware update progress.

---

#### GET `/updater/downgrade_state`
Returns firmware downgrade status.

---

#### GET `/updater/app_loading_state`
Returns application loading state (during boot or update).

**Response Example**:
```json
{
  "payload": {},
  "state": "not_started"
}
```

---

### Remote Access

#### GET `/remote_control_key`
Returns a signed JWT token for remote access/control via Emlid cloud services.

**Response Example**:
```json
"eyJzZXJpYWxfbnVtYmVyIjoiODI0MzVDRjBBMjM5NzdDQiIsInNpZ25hdHVyZSI6IjgxRUNBRThENzA4MzkwMzMwQ0IwMDBCRjcxNzMwRkQ3OEREQTJCOEU2QTNBREE5MzhBNDgzMjQyNTcyRDA3M0QwRTBFMjVBRENBMzlGNjQ1RjRFMEY3QUY1OTM3REI4NjBGQzFFNDlFQzY3MTQ5RTVCNzA0QkRFMTM1NThFQTE2IiwidGltZXN0YW1wIjoxNzcwOTM1OTQxLjQwOTUxNH0="
```

**Use Case**: Generate access token for cloud-based remote monitoring/control.

---

## Error Responses

When an error occurs, the API typically returns:

**HTTP Status Codes**:
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (invalid endpoint)
- `500` - Internal Server Error

**Example Error Response**:
```json
{
  "error": {
    "code": "invalid_parameter",
    "message": "Description of error"
  }
}
```

---

## Recommended Polling Intervals

| Endpoint | Recommended Interval | Notes |
|----------|---------------------|-------|
| `/info` | Once at startup, or 5 min | Device info rarely changes |
| `/battery` | 30 seconds | Or rely on WebSocket |
| `/wifi/status` | 30-60 seconds | Network status |
| `/bluetooth/status` | 60 seconds | BT status |
| `/lora/state` | 10-15 seconds | Or rely on WebSocket |
| `/lora/rssi` | 10-15 seconds | Signal quality |
| `/configuration` | Once at startup | Or on-demand |
| `/configuration/device` | Once at startup | Role/settings |
| `/updater/upgrade_state` | 60 seconds | Only when checking for updates |
| `/remote_control_key` | On-demand | Generate when needed |

**General Rule**: Use WebSocket for real-time data, REST API for infrequent configuration/status checks.

---

## Integration Tips

1. **Discovery**: The device responds to mDNS with service type `_reach._tcp.local`
   - Default hostname: `reach.local` or `reach-XXXXXX.local` (last 6 digits of serial)

2. **Default IP**:
   - Client mode: DHCP-assigned
   - Hotspot mode: `192.168.42.1`

3. **Web UI**: Full web interface available at `http://<device_ip>/`

4. **CORS**: No CORS restrictions observed for local network access

5. **Content-Type**: All POST requests should use `application/json`

6. **Idempotency**: GET requests are idempotent; POST requests may trigger state changes

---

## Complete Endpoint List

### GET Endpoints
- `/info`
- `/device`
- `/configuration`
- `/configuration/device`
- `/configuration/positioning_settings`
- `/configuration/sound/`
- `/configuration/constraints`
- `/configuration/constraints/uhf_radio`
- `/configuration/base_mode/averager_state`
- `/battery`
- `/wifi/status`
- `/wifi/hotspot`
- `/wifi/networks`
- `/bluetooth/status`
- `/bluetooth/devices`
- `/modem/1/settings`
- `/modem/1/info`
- `/lora/state`
- `/lora/rssi`
- `/uhf_radio/rssi`
- `/logs`
- `/surveying/projects_exporter_state`
- `/updater`
- `/updater/upgrade_state`
- `/updater/downgrade_state`
- `/updater/app_loading_state`
- `/remote_control_key`

### POST Endpoints
- `/configuration/device`
- `/configuration/positioning_settings`
- (Likely more POST/PUT/DELETE endpoints exist for configuration changes)

---

## Next Steps for Integration

1. Test all endpoints with your device to confirm structure
2. Identify which endpoints require POST vs GET
3. Document any authentication requirements (if device is configured with security)
4. Test error conditions (disconnection, invalid values, etc.)
5. Verify mDNS discovery for automatic device detection
