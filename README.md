# BLE Device Discovery Add-on

## Overview
This Home Assistant add-on provides advanced Bluetooth Low Energy (BLE) device discovery and management.

## Features
- Continuous BLE device scanning
- Persistent device discovery tracking
- Configurable scan intervals
- Home Assistant notifications

## Configuration
```json
{
    "log_level": "info",
    "scan_interval": 60
}
```

### Options
- `log_level`: Logging verbosity (trace, debug, info, warning, error, fatal)
- `scan_interval`: Seconds between BLE scans (10-3600)

## Installation
1. Add this repository to Home Assistant
2. Install the "BLE Device Discovery" add-on
3. Configure and start the add-on

## Limitations
- Actual BLE scanning method depends on your hardware
- Current version uses simulated discovery

## Troubleshooting
- Check add-on logs for discovery details
- Ensure proper BLE gateway configuration

## Future Improvements
- Real BLE scanning support
- Advanced device filtering
- Integration with Home Assistant device registry