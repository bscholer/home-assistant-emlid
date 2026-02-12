# WebSocket Data Reference

This document provides the exact data structures from the Emlid RS4 WebSocket for implementation reference.

## Connection Details

- **URL**: `http://<device_ip>/socket.io/`
- **Protocol**: Socket.IO (Engine.IO v3)
- **Transport**: Polling initially, can upgrade to WebSocket
- **Event Name**: `broadcast`
- **Data Format**: JSON with `name` and `payload` fields

## Event Structures

### 1. navigation
**Update Frequency**: 5Hz (every 0.2 seconds)

```json
{
  "name": "navigation",
  "payload": {
    "dop": {
      "g": 2.02,      // Geometric DOP
      "p": 1.71,      // Position DOP
      "h": 1.07,      // Horizontal DOP
      "v": 1.34       // Vertical DOP
    },
    "aod": 0.0,       // Age of differential (seconds)
    "solution": "fix", // Solution status: "fix", "float", "single", "no_solution"
    "time": 1770936914.0,  // GNSS time (Unix timestamp)
    "ar_ratio": 0.0,  // Ambiguity resolution ratio
    "satellites": {
      "rover": 33,    // Total satellites tracked by rover
      "base": 20,     // Total satellites tracked by base
      "valid": 21     // Satellites used in solution
    },
    "positioning_mode": "kinematic",  // "kinematic", "static", or "stop-and-go"
    "rover_position": {
      "coordinates": {
        "lat": 44.015409987999995,    // Latitude (degrees)
        "lon": -121.34619369400001,   // Longitude (degrees)
        "h": 1155.7523999999999       // Height (meters, ellipsoid)
      },
      "accuracy": {
        "e": 0.009999999776482582,    // East accuracy (meters)
        "n": 0.009999999776482582,    // North accuracy (meters)
        "u": 0.017000000923871994     // Up accuracy (meters)
      }
    },
    "base_position": {
      "coordinates": {
        "lat": 44.089390914365396,    // Base station latitude
        "lon": -121.30752189651675,   // Base station longitude
        "h": 1070.736914537847        // Base station height
      },
      "antenna_height": 0.0           // Base antenna height offset
    },
    "baseline": 8786.957389216073,    // Distance to base station (meters)
    "velocity": {
      "e": -0.01,     // East velocity (m/s)
      "n": 0.0,       // North velocity (m/s)
      "u": 0.01       // Up velocity (m/s)
    }
  }
}
```

### 2. battery_status
**Update Frequency**: ~1 Hz (varies)

```json
{
  "name": "battery_status",
  "payload": {
    "usb_charger_current": null,      // USB charger current (A), null if not charging
    "usb_charger_voltage": null,      // USB charger voltage (V), null if not charging
    "state_of_charge": 78,            // Battery percentage (0-100)
    "charger_status": "Discharging",  // "Charging", "Discharging", "Full", etc.
    "temperature": 24.2,              // Battery temperature (°C)
    "voltage": 8.17,                  // Battery voltage (V)
    "current": -0.26,                 // Battery current (A, negative = discharging)
    "otg": false                      // USB OTG power output enabled
  }
}
```

### 3. power_supply_status
**Update Frequency**: ~1 Hz (on changes)

```json
{
  "name": "power_supply_status",
  "payload": {
    "battery_status": false,    // Battery present/detected
    "usb_cable_status": false   // USB cable connected
  }
}
```

### 4. lora_state
**Update Frequency**: ~1 Hz (on changes)

```json
{
  "name": "lora_state",
  "payload": {
    "connected": true    // LoRa radio connection status
  }
}
```

### 5. observations
**Update Frequency**: ~1 Hz

Detailed satellite observation data including signal-to-noise ratio, elevation, and azimuth for each satellite.

```json
{
  "name": "observations",
  "payload": {
    "satellites_count": {
      "rover": 33,
      "base": 20,
      "valid": 22
    },
    "satellites": {
      "rover": [
        {
          "satellite_index": "G5",           // Satellite ID (G=GPS, E=Galileo, R=GLONASS, C=BeiDou, S=SBAS)
          "signal_to_noise_ratio": 44,      // SNR in dB-Hz
          "elevation": 19,                   // Elevation angle (degrees)
          "azimuth": 157                     // Azimuth angle (degrees)
        },
        {
          "satellite_index": "E23",
          "signal_to_noise_ratio": 47,
          "elevation": 75,
          "azimuth": 135
        }
        // ... more satellites
      ],
      "base": [
        {
          "satellite_index": "G5",
          "signal_to_noise_ratio": 40,
          "elevation": 0,                    // Note: Base satellites don't report elevation/azimuth
          "azimuth": 0
        }
        // ... more satellites
      ]
    }
  }
}
```

**Satellite Constellation Prefixes**:
- `G` - GPS (USA)
- `E` - Galileo (EU)
- `R` - GLONASS (Russia)
- `C` - BeiDou (China)
- `S` - SBAS (WAAS/EGNOS/MSAS)

### 6. active_logs
**Update Frequency**: ~2 seconds

```json
{
  "name": "active_logs",
  "payload": {
    "raw": {
      "is_writing": true,
      "format": "RINEX",
      "file_name": "Reach_raw_20260212223749_RINEX_3_03",
      "log_type": "raw",
      "size": 14322742.0,                    // File size in bytes
      "recording_time": 1044.3013310432434,  // Duration recorded (seconds)
      "remaining_time": 85355.69866895676,   // Time until storage full (seconds)
      "start_time": 1770935870.0642452       // Start timestamp (Unix)
    },
    "solution": {
      "is_writing": true,
      "format": "LLH",
      "file_name": "Reach_solution_20260212223749.LLH",
      "log_type": "solution",
      "size": 725868.0,
      "recording_time": 1044.3013310432434,
      "remaining_time": 85355.69866895676,
      "start_time": 1770935870.0642452
    },
    "base": {
      "is_writing": true,
      "format": "RTCM3",
      "file_name": "Reach_base_20260212223749.RTCM3",
      "log_type": "base",
      "size": 604459.0,
      "recording_time": 1044.3013310432434,
      "remaining_time": 85355.69866895676,
      "start_time": 1770935870.0642452
    },
    "archive_name": "Reach_20260212223749"
  }
}
```

### 7. stream_status
**Update Frequency**: ~1 Hz

```json
{
  "name": "stream_status",
  "payload": {
    "correction_input": [
      {
        "state": "active",    // "active", "inactive", "error", "preparing"
        "rtcm_messages": [
          {
            "type": 1006,     // RTCM message type number
            "count": 206      // Number of messages received
          },
          {
            "type": 1074,     // GPS MSM4
            "count": 1028
          },
          {
            "type": 1084,     // GLONASS MSM4
            "count": 1028
          },
          {
            "type": 1094,     // Galileo MSM4
            "count": 1028
          }
          // ... more message types
        ]
      }
    ],
    "position_output": [
      {
        "error": {
          "code": "write",
          "message": "Write error"
        },
        "state": "error"
      },
      {
        "state": "preparing"
      }
    ],
    "correction_output": [
      {
        "state": "preparing"
      },
      {
        "state": "inactive"
      }
    ]
  }
}
```

**Important RTCM Message Types**:
- `1005/1006` - Base station position
- `1074` - GPS MSM4 (Multi-Signal Message)
- `1084` - GLONASS MSM4
- `1094` - Galileo MSM4
- `1124` - BeiDou MSM4
- `1230` - GLONASS code-phase biases

### 8. notifications
**Update Frequency**: On changes

```json
{
  "name": "notifications",
  "payload": {
    "notifications": []    // Array of notification objects (empty when none)
  }
}
```

When notifications are present:
```json
{
  "name": "notifications",
  "payload": {
    "notifications": [
      {
        "id": "notification_id",
        "type": "warning",           // "info", "warning", "error"
        "message": "Description of issue",
        "timestamp": 1770935870
      }
    ]
  }
}
```

---

## Solution Status Values

The `navigation.payload.solution` field can have these values:

- `"fix"` - **RTK Fixed** - Highest accuracy (cm-level), ambiguities resolved
- `"float"` - **RTK Float** - Good accuracy (dm-level), ambiguities not fully resolved
- `"single"` - **Single Point** - Standard GPS accuracy (m-level), no corrections
- `"no_solution"` - No valid position solution

**Quality Hierarchy**: `fix` > `float` > `single` > `no_solution`

---

## Positioning Mode Values

The `navigation.payload.positioning_mode` field:

- `"kinematic"` - Moving receiver (default for rover)
- `"static"` - Stationary receiver
- `"stop-and-go"` - Intermittent movement with static periods

---

## Connection Code Example

```python
import socketio

sio = socketio.Client(
    logger=False,           # Set True for debugging
    engineio_logger=False,
    reconnection=True,
)

@sio.event
def connect():
    print(f"Connected: {sio.sid}")

@sio.event
def disconnect():
    print("Disconnected")

@sio.on('broadcast')
def on_broadcast(data):
    event_name = data['name']
    payload = data['payload']

    if event_name == 'navigation':
        lat = payload['rover_position']['coordinates']['lat']
        lon = payload['rover_position']['coordinates']['lon']
        solution = payload['solution']
        print(f"Position: {lat:.10f}, {lon:.10f} | Solution: {solution}")

    elif event_name == 'battery_status':
        soc = payload['state_of_charge']
        voltage = payload['voltage']
        print(f"Battery: {soc}% @ {voltage}V")

# Connect to device
sio.connect(
    'http://192.168.1.21',
    socketio_path='/socket.io',
    transports=['polling', 'websocket'],
)

# Keep connection alive
sio.wait()
```

---

## Data Rate Summary

| Event Type | Frequency | Notes |
|------------|-----------|-------|
| `navigation` | 5 Hz | **Most critical** - throttle for HASS |
| `observations` | 1 Hz | Large payload, optional |
| `battery_status` | ~1 Hz | Variable rate |
| `power_supply_status` | On change | Low frequency |
| `lora_state` | On change | Low frequency |
| `active_logs` | ~0.5 Hz | Every 2 seconds |
| `stream_status` | ~1 Hz | Variable rate |
| `notifications` | On change | Event-driven |

**Total Data Rate**: Approximately 6-7 messages per second when all events are active.
