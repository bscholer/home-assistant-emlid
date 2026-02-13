# Satellite Visualization Guide

The Emlid integration provides detailed satellite observation data that can be visualized in Home Assistant using various custom cards.

## Available Data

The `sensor.emlid_satellite_observations` entity provides:

### State
Number of satellites currently tracked by the rover

### Attributes

```yaml
satellites_count:
  rover: 33      # Total satellites tracked
  base: 20       # Base station satellites
  valid: 21      # Satellites used in solution

rover_satellites:
  - satellite_index: "G5"              # GPS PRN 5
    signal_to_noise_ratio: 44          # SNR in dB-Hz
    elevation: 19                      # Degrees above horizon
    azimuth: 157                       # Compass direction (0-360°)
  - satellite_index: "E23"             # Galileo E23
    signal_to_noise_ratio: 47
    elevation: 75
    azimuth: 135
  # ... more satellites

by_constellation:
  GPS: [...]         # Array of GPS satellites
  GLONASS: [...]     # Array of GLONASS satellites
  Galileo: [...]     # Array of Galileo satellites
  BeiDou: [...]      # Array of BeiDou satellites
  QZSS: [...]        # Array of QZSS satellites
  SBAS: [...]        # Array of SBAS satellites

timestamp: "2026-02-13T15:30:45.123456"
```

### Satellite Index Format
- **G** = GPS (USA) - e.g., G5, G12
- **R** = GLONASS (Russia) - e.g., R7, R14
- **E** = Galileo (EU) - e.g., E21, E33
- **C** = BeiDou (China) - e.g., C29, C36
- **J** = QZSS (Japan) - e.g., J01, J02
- **S** = SBAS (augmentation) - e.g., S131, S135

## Visualization Examples

### 1. Bar Chart - Signal Strength by Constellation

Show satellite signal strength as a bar chart:

```yaml
type: custom:apexcharts-card
header:
  title: Satellite Signal Strength
  show: true
update_interval: 1s
experimental:
  color_threshold: true
all_series_config:
  type: column
series:
  - entity: sensor.emlid_satellite_observations
    name: GPS
    color: '#2196F3'
    data_generator: |
      return entity.attributes.by_constellation.GPS.map((sat) => {
        return [new Date().getTime(), sat.signal_to_noise_ratio];
      });
  - entity: sensor.emlid_satellite_observations
    name: Galileo
    color: '#4CAF50'
    data_generator: |
      return entity.attributes.by_constellation.Galileo.map((sat) => {
        return [new Date().getTime(), sat.signal_to_noise_ratio];
      });
  - entity: sensor.emlid_satellite_observations
    name: GLONASS
    color: '#FF9800'
    data_generator: |
      return entity.attributes.by_constellation.GLONASS.map((sat) => {
        return [new Date().getTime(), sat.signal_to_noise_ratio];
      });
  - entity: sensor.emlid_satellite_observations
    name: BeiDou
    color: '#F44336'
    data_generator: |
      return entity.attributes.by_constellation.BeiDou.map((sat) => {
        return [new Date().getTime(), sat.signal_to_noise_ratio];
      });
apex_config:
  chart:
    height: 300
    stacked: false
  yaxis:
    title:
      text: "Signal Strength (dB-Hz)"
    min: 0
    max: 60
  xaxis:
    labels:
      show: false
  legend:
    show: true
```

### 2. Satellite Count Timeline

Track satellite counts over time:

```yaml
type: custom:apexcharts-card
header:
  title: Satellites Over Time
  show: true
graph_span: 1h
all_series_config:
  type: line
  stroke_width: 2
series:
  - entity: sensor.emlid_satellites_rover
    name: Total Tracked
    color: '#2196F3'
  - entity: sensor.emlid_satellites_valid
    name: Used in Solution
    color: '#4CAF50'
apex_config:
  chart:
    height: 200
  yaxis:
    title:
      text: "Satellite Count"
    min: 0
  legend:
    show: true
```

### 3. Simple Satellite List by Constellation

Show satellite counts by constellation as an area chart:

```yaml
type: custom:apexcharts-card
header:
  title: Satellites by Constellation
  show: true
update_interval: 1s
graph_span: 5min
all_series_config:
  type: area
  stroke_width: 2
  opacity: 0.3
series:
  - entity: sensor.emlid_satellite_observations
    name: GPS
    color: '#2196F3'
    data_generator: |
      return [[new Date().getTime(), entity.attributes.by_constellation.GPS.length]];
  - entity: sensor.emlid_satellite_observations
    name: Galileo
    color: '#4CAF50'
    data_generator: |
      return [[new Date().getTime(), entity.attributes.by_constellation.Galileo.length]];
  - entity: sensor.emlid_satellite_observations
    name: GLONASS
    color: '#FF9800'
    data_generator: |
      return [[new Date().getTime(), entity.attributes.by_constellation.GLONASS.length]];
  - entity: sensor.emlid_satellite_observations
    name: BeiDou
    color: '#F44336'
    data_generator: |
      return [[new Date().getTime(), entity.attributes.by_constellation.BeiDou.length]];
apex_config:
  chart:
    height: 250
    stacked: false
  yaxis:
    title:
      text: "Satellites"
    min: 0
  legend:
    show: true
```

### 3a. Sky Plot - Visual Satellite Map

For a proper polar sky plot showing satellite positions, you have a few options:

#### Option 1: Plotly Graph Card (Best for Sky Plots)

Install **plotly-graph-card** via HACS, then use:

```yaml
type: custom:plotly-graph-card
title: Satellite Sky Plot
hours_to_show: 0
refresh_interval: 1
layout:
  height: 400
  polar:
    radialaxis:
      range: [0, 90]
      angle: 90
      direction: clockwise
    angularaxis:
      direction: clockwise
      rotation: 90
entities:
  - entity: sensor.emlid_satellite_observations
    name: GPS
    mode: markers
    marker:
      size: 10
      color: '#2196F3'
    type: scatterpolar
    theta: >
      $fn ({ys,meta}) =>
        meta.by_constellation.GPS.map(sat => sat.azimuth)
    r: >
      $fn ({ys,meta}) =>
        meta.by_constellation.GPS.map(sat => 90 - sat.elevation)
    text: >
      $fn ({ys,meta}) =>
        meta.by_constellation.GPS.map(sat => sat.satellite_index + ' (' + sat.signal_to_noise_ratio + ' dB)')
  - entity: sensor.emlid_satellite_observations
    name: Galileo
    mode: markers
    marker:
      size: 10
      color: '#4CAF50'
    type: scatterpolar
    theta: >
      $fn ({ys,meta}) =>
        meta.by_constellation.Galileo.map(sat => sat.azimuth)
    r: >
      $fn ({ys,meta}) =>
        meta.by_constellation.Galileo.map(sat => 90 - sat.elevation)
    text: >
      $fn ({ys,meta}) =>
        meta.by_constellation.Galileo.map(sat => sat.satellite_index + ' (' + sat.signal_to_noise_ratio + ' dB)')
```

#### Option 2: Simple Visual Grid (No Custom Cards)

Create a visual representation using emoji/symbols in markdown:

```yaml
type: markdown
content: |
  ## Satellite Sky View
  ```
         N (0°)
          |
      {% set sats = state_attr('sensor.emlid_satellite_observations', 'rover_satellites') %}
      {% for sat in sats %}
        {% if sat.elevation > 30 %}
  🛰️ {{ sat.satellite_index }} ({{ sat.signal_to_noise_ratio }}dB)
        {% endif %}
      {% endfor %}
  W —  🎯  — E
      (270°) (90°)
          |
         S (180°)
  ```

  **High Satellites (>60°):**
  {% for sat in sats | selectattr('elevation', '>', 60) %}
  • **{{ sat.satellite_index }}** - {{ sat.signal_to_noise_ratio }}dB @ {{ sat.azimuth }}°
  {% endfor %}

#### Option 3: Canvas-Based Custom Card (Advanced)

For a truly interactive sky plot, you'd need to create a custom Lovelace card. Here's a basic template:

**skyplot-card.js** (place in `www/community/skyplot-card/`):
```javascript
class SkyplotCard extends HTMLElement {
  setConfig(config) {
    this.config = config;
  }

  set hass(hass) {
    if (!this.content) {
      this.innerHTML = `
        <ha-card header="Satellite Sky Plot">
          <div class="card-content">
            <canvas id="skyplot" width="400" height="400"></canvas>
          </div>
        </ha-card>
      `;
      this.content = this.querySelector('canvas');
    }

    const entity = hass.states[this.config.entity];
    if (entity) {
      this.drawSkyPlot(entity.attributes.rover_satellites);
    }
  }

  drawSkyPlot(satellites) {
    const canvas = this.content;
    const ctx = canvas.getContext('2d');
    const centerX = 200;
    const centerY = 200;
    const radius = 180;

    // Clear canvas
    ctx.clearRect(0, 0, 400, 400);

    // Draw compass circles
    ctx.strokeStyle = '#ccc';
    [30, 60, 90].forEach(angle => {
      const r = (angle / 90) * radius;
      ctx.beginPath();
      ctx.arc(centerX, centerY, r, 0, 2 * Math.PI);
      ctx.stroke();
    });

    // Draw compass directions
    ctx.fillStyle = '#666';
    ctx.font = '14px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('N', centerX, 20);
    ctx.fillText('S', centerX, 380);
    ctx.fillText('E', 380, centerY);
    ctx.fillText('W', 20, centerY);

    // Draw satellites
    satellites.forEach(sat => {
      const elevation = sat.elevation;
      const azimuth = (sat.azimuth - 90) * Math.PI / 180;
      const r = ((90 - elevation) / 90) * radius;
      const x = centerX + r * Math.cos(azimuth);
      const y = centerY + r * Math.sin(azimuth);

      // Color by constellation
      const colors = {
        'G': '#2196F3', // GPS
        'E': '#4CAF50', // Galileo
        'R': '#FF9800', // GLONASS
        'C': '#F44336', // BeiDou
      };
      ctx.fillStyle = colors[sat.satellite_index[0]] || '#999';

      // Draw satellite dot
      ctx.beginPath();
      ctx.arc(x, y, 5, 0, 2 * Math.PI);
      ctx.fill();

      // Label
      ctx.fillStyle = '#000';
      ctx.font = '10px sans-serif';
      ctx.fillText(sat.satellite_index, x + 8, y + 3);
    });
  }

  getCardSize() {
    return 5;
  }
}

customElements.define('skyplot-card', SkyplotCard);
```

**resources.yaml:**
```yaml
- url: /local/community/skyplot-card/skyplot-card.js
  type: module
```

**Lovelace:**
```yaml
type: custom:skyplot-card
entity: sensor.emlid_satellite_observations
```

### 4. Constellation Distribution (Simple Stats)

Show satellite counts by constellation:

```yaml
type: markdown
content: |
  ## Active Constellations

  {% set gps = state_attr('sensor.emlid_satellite_observations', 'by_constellation')['GPS'] | length %}
  {% set glonass = state_attr('sensor.emlid_satellite_observations', 'by_constellation')['GLONASS'] | length %}
  {% set galileo = state_attr('sensor.emlid_satellite_observations', 'by_constellation')['Galileo'] | length %}
  {% set beidou = state_attr('sensor.emlid_satellite_observations', 'by_constellation')['BeiDou'] | length %}
  {% set qzss = state_attr('sensor.emlid_satellite_observations', 'by_constellation')['QZSS'] | length %}
  {% set total = gps + glonass + galileo + beidou + qzss %}

  🇺🇸 **GPS**: {{ gps }} ({{ (gps/total*100) | round(0) }}%)
  🇪🇺 **Galileo**: {{ galileo }} ({{ (galileo/total*100) | round(0) }}%)
  🇷🇺 **GLONASS**: {{ glonass }} ({{ (glonass/total*100) | round(0) }}%)
  🇨🇳 **BeiDou**: {{ beidou }} ({{ (beidou/total*100) | round(0) }}%)
  🇯🇵 **QZSS**: {{ qzss }} ({{ (qzss/total*100) | round(0) }}%)

  **Total**: {{ total }} satellites
```

### 5. Real-time Satellite Table

Use a Markdown card to show detailed satellite info:

```yaml
type: markdown
content: |
  ## Satellites in View

  {% set sats = state_attr('sensor.emlid_satellite_observations', 'rover_satellites') %}
  {% for sat in sats | sort(attribute='signal_to_noise_ratio', reverse=true) %}
  **{{ sat.satellite_index }}** - SNR: {{ sat.signal_to_noise_ratio }} dB-Hz | El: {{ sat.elevation }}° | Az: {{ sat.azimuth }}°
  {% endfor %}
```

### 6. Historical Tracking (with InfluxDB)

For tracking satellites over longer periods, use InfluxDB and Grafana:

**InfluxDB Configuration:**
```yaml
influxdb:
  host: localhost
  database: homeassistant
  include:
    entities:
      - sensor.emlid_satellite_observations
```

**Grafana Query:**
```sql
SELECT
  count("rover_satellites")
FROM "sensor.emlid_satellite_observations"
WHERE $timeFilter
GROUP BY time(1m)
```

## Advanced: Custom Sky Plot Card

For a true polar sky plot, you can create a custom Lovelace card or use the `canvas-gauge-card`:

**Install:**
```bash
# Via HACS
# Search for "Canvas Gauge Card"
```

**Configuration:**
```yaml
type: custom:canvas-gauge-card
entity: sensor.emlid_satellite_observations
card_height: 400
gauge:
  type: radial-gauge
  renderTo: satellite-skyplot
  # ... custom configuration for polar plot
```

## Automation Ideas

### Alert on Low Satellite Count
```yaml
automation:
  - alias: "Low satellite warning"
    trigger:
      - platform: numeric_state
        entity_id: sensor.emlid_satellites_valid
        below: 8
        for: "00:01:00"
    action:
      - service: notify.mobile_app
        data:
          message: "Low satellite count: {{ states('sensor.emlid_satellites_valid') }}"
```

### Track Satellite Visibility Throughout Day
```yaml
automation:
  - alias: "Log satellite visibility"
    trigger:
      - platform: time_pattern
        minutes: "/15"
    action:
      - service: logbook.log
        data:
          name: Satellite Count
          message: >
            GPS: {{ state_attr('sensor.emlid_satellite_observations', 'by_constellation')['GPS'] | length }}
            Galileo: {{ state_attr('sensor.emlid_satellite_observations', 'by_constellation')['Galileo'] | length }}
            Total: {{ states('sensor.emlid_satellites_rover') }}
```

## Tips

1. **Update Rate**: The satellite observations update at ~1Hz. Match your ApexCharts `update_interval` accordingly.

2. **SNR Threshold**: Satellites with SNR > 35 dB-Hz typically provide good positioning quality.

3. **Elevation**: Satellites below 15° elevation are often excluded due to multipath and atmospheric effects.

4. **Constellation Performance**:
   - GPS is most mature and widely available
   - Galileo often has highest accuracy
   - BeiDou provides good coverage in Asia-Pacific
   - GLONASS helps in high latitudes

5. **Database Impact**: The full satellite arrays can be large. Consider:
   - Using `recorder: exclude:` for the satellite_observations sensor
   - Using InfluxDB for long-term storage
   - Setting appropriate `purge_keep_days` in recorder

## Required HACS Cards

- [ApexCharts Card](https://github.com/RomRider/apexcharts-card) - For all chart types
- [Canvas Gauge Card](https://github.com/custom-cards/canvas-gauge-card) - Optional, for polar plots

## Future Enhancements

Potential additions to the integration:
- Pre-calculated sky plot coordinates
- Satellite trajectory predictions
- DOP value trends
- Constellation-specific signal quality metrics
- Historical satellite visibility statistics
