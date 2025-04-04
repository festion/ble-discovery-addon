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
- Configurable scan intervals
- Automatic MAC address formatting
- Device categorization

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

## Support
For issues, questions, or feature requests, please open an issue on GitHub.