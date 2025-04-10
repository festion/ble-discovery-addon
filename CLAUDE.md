# Enhanced BLE Device Discovery Add-on

## How Claude Should Assist

Claude should help users with the following tasks related to this Home Assistant add-on for Bluetooth Low Energy (BLE) device discovery and management:

- Modifications to Python code in `ble_discovery.py`
- Adjustments to YAML configuration files
- Troubleshooting BLE device discovery issues
- Docker-related configuration and build issues
- Testing and verification of functionality

## Key Commands to Run

- Lint and check Python code: `flake8 ble_discovery.py`
- Run the add-on locally: `./run.sh`
- Build Docker image: `docker build -t ble-discovery-addon .`

## Important Files

- `ble_discovery.py`: Main Python code for BLE device discovery
- `ble_input_text.yaml`, `ble_scripts.yaml`, `btle_dashboard.yaml`: YAML configuration files
- `config.json`: Add-on configuration
- `Dockerfile`: Container build configuration
- `run.sh`: Script to run the add-on

## Key Concepts

- BLE device scanning and discovery
- MQTT integration with Home Assistant
- Signal strength (RSSI) threshold settings
- Dashboard UI components
- Device categorization and management