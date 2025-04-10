# Enhanced BLE Device Discovery Add-on

## Overview
This Home Assistant add-on provides advanced Bluetooth Low Energy (BLE) device discovery and management with a user-friendly dashboard interface.

## Features
- Continuous BLE device scanning
- User-friendly discovery dashboard
- Direct device management through the UI
- Signal strength testing for optimal threshold setting
- Easy device addition to Home Assistant
- Persistent device tracking
- Adaptive scan intervals based on time of day and activity
- Enhanced device type detection with extensive MAC address database
- Automatic device categorization based on advertisement data
- Energy-efficient operation
- Comprehensive device categorization with 12 device types
- Advanced device identification

## Compatibility
This add-on is designed to work with:
- ESP32 BLE Gateways
- Built-in Bluetooth adapters
- External Bluetooth adapters
- MQTT-based BLE proxies

## Configuration

```yaml
log_level: info
scan_interval: 60
gateway_topic: BTLE
```

### Options
- `log_level`: Logging verbosity (trace, debug, info, warning, error, fatal)
- `scan_interval`: Seconds between BLE scans (10-3600)
- `gateway_topic`: MQTT topic for the BLE gateway (default: BTLE)

## Installation
1. Add this repository to your Home Assistant Add-on Store
2. Install the "Enhanced BLE Device Discovery" add-on
3. Configure and start the add-on
4. Access the BLE dashboard from your sidebar

## Usage
1. Navigate to the BLE Dashboard from your Home Assistant sidebar
2. Click "Scan for BLE Devices" to discover nearby Bluetooth devices
3. Select a device from the discovered list to configure it
4. Set a friendly name and device type
5. Set the RSSI threshold (use the testing tool to determine optimal value)
6. Click "Add Selected Device" to add the device to Home Assistant

## Dashboard Tabs
- **Device Discovery**: Scan for and add new BLE devices
- **Managed Devices**: View and manage added BLE devices, test signal strength

## Troubleshooting
- If devices aren't showing up in scans, check:
  - BLE Gateway connection status
  - MQTT server configuration
  - Bluetooth adapter functionality
  - Proximity of BLE devices
- For signal strength issues:
  - Use the signal testing tool
  - Try different placements of your BLE gateway
  - Consider multiple gateways for better coverage

## New Features in v1.4.0

### Adaptive Scanning
The add-on now includes an intelligent adaptive scanning system that automatically adjusts scan intervals based on:
- Time of day (slower scans at night, faster during active hours)
- Home Assistant activity level
- Device movement detection (based on RSSI changes)
- Number of strong-signal devices present

This results in:
- Lower energy consumption
- Reduced network traffic
- Higher responsiveness when needed
- Longer battery life for host systems

### Enhanced Device Identification
The add-on now features:
- Comprehensive database of 200+ device manufacturer MAC prefixes
- Automatic device type detection from advertisement data
- Classification into 12 specific device categories:
  - Presence devices
  - Temperature sensors
  - Humidity sensors
  - Motion sensors
  - Contact sensors
  - Buttons/remotes
  - Lights
  - Smart locks
  - Scales
  - Wearables
  - Speakers
  - Other devices

### Monitoring
- New sensor.ble_scan_interval entity showing current scan settings
- Enhanced BLE Gateway sensor with additional metadata
- Improved diagnostic information and logging

## Support
For issues, questions, or feature requests, please open an issue on GitHub.
## New Features in v1.4.0

### Adaptive Scanning
The add-on now includes an intelligent adaptive scanning system that automatically adjusts scan intervals based on:
- Time of day (slower scans at night, faster during active hours)
- Home Assistant activity level
- Device movement detection (based on RSSI changes)
- Number of strong-signal devices present

This results in:
- Lower energy consumption
- Reduced network traffic
- Higher responsiveness when needed
- Longer battery life for host systems

### Enhanced Device Identification
The add-on now features:
- Comprehensive database of 200+ device manufacturer MAC prefixes
- Automatic device type detection from advertisement data
- Classification into 12 specific device categories:
  - Presence devices
  - Temperature sensors
  - Humidity sensors
  - Motion sensors
  - Contact sensors
  - Buttons/remotes
  - Lights
  - Smart locks
  - Scales
  - Wearables
  - Speakers
  - Other devices

### Monitoring
- New sensor.ble_scan_interval entity showing current scan settings
- Enhanced BLE Gateway sensor with additional metadata
- Improved diagnostic information and logging
