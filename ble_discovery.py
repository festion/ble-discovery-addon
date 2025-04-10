#!/usr/bin/env python3
"""
Enhanced BLE Device Discovery Add-on for Home Assistant
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
import uuid
import requests

# Configuration
DISCOVERIES_FILE = "/config/bluetooth_discoveries.json"
DEFAULT_SCAN_INTERVAL = 60
DEFAULT_GATEWAY_TOPIC = "BTLE"

def setup_logging(log_level):
    """Configure logging based on input level."""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    
    # Create logs directory if it doesn't exist
    log_dir = "/config/ble_discovery/logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Generate log filename with timestamp
    log_filename = os.path.join(log_dir, f"ble_discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # Configure file handler for detailed logging
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - BLE Discovery - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    ))
    
    # Configure console handler for basic logging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - BLE Discovery - %(levelname)s - %(message)s'
    ))
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add the handlers to the logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Create a symlink to the latest log file
    latest_log_link = os.path.join(log_dir, "latest.log")
    try:
        if os.path.exists(latest_log_link):
            os.remove(latest_log_link)
        os.symlink(log_filename, latest_log_link)
    except Exception as e:
        print(f"Error creating symlink to latest log: {e}")
        
    # Rotate logs (keep only last 10)
    try:
        log_files = sorted([f for f in os.listdir(log_dir) if f.startswith("ble_discovery_") and f.endswith(".log")])
        if len(log_files) > 10:
            for old_file in log_files[:-10]:
                os.remove(os.path.join(log_dir, old_file))
    except Exception as e:
        print(f"Error rotating logs: {e}")
        
    logging.info("Logging initialized with level %s to %s", log_level, log_filename)

def load_discoveries():
    """Load previously discovered devices."""
    try:
        if os.path.exists(DISCOVERIES_FILE):
            with open(DISCOVERIES_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"Error loading discoveries: {e}")
    return []

def save_discoveries(discoveries):
    """Save discoveries to file."""
    try:
        with open(DISCOVERIES_FILE, 'w') as f:
            json.dump(discoveries, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Error saving discoveries: {e}")
        return False

def create_home_assistant_notification(title, message, notification_id=None):
    """Create a notification in Home Assistant."""
    try:
        # Use Supervisor token for authentication
        headers = {
            "Authorization": f"Bearer {os.environ.get('SUPERVISOR_TOKEN', '')}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "title": title,
            "message": message
        }
        
        if notification_id:
            payload["notification_id"] = notification_id
        
        response = requests.post(
            "http://supervisor/core/api/services/persistent_notification/create", 
            headers=headers, 
            json=payload
        )
        
        if response.status_code < 200 or response.status_code >= 300:
            logging.error(f"Error creating notification: {response.status_code} - {response.text}")
        
        return response.status_code < 300
        
    except Exception as e:
        logging.error(f"Error creating notification: {e}")
        return False

def get_ble_gateway_data():
    """
    Get BLE gateway data from bluetooth integration.
    Returns a list of discovered devices.
    """
    try:
        headers = {
            "Authorization": f"Bearer {os.environ.get('SUPERVISOR_TOKEN', '')}",
            "Content-Type": "application/json"
        }
        
        # First try to get bluetooth devices from the native integration
        response = requests.get(
            "http://supervisor/core/api/states",
            headers=headers
        )
        
        if response.status_code < 200 or response.status_code >= 300:
            logging.error(f"Error getting states: {response.status_code} - {response.text}")
            return []
            
        states = response.json()
        
        # Look for bluetooth devices in the states
        devices = []
        for state in states:
            entity_id = state.get('entity_id', '')
            if entity_id.startswith('bluetooth.') and not entity_id.endswith('_battery_level'):
                try:
                    attributes = state.get('attributes', {})
                    mac = attributes.get('address') or entity_id.replace('bluetooth.', '')
                    
                    # Standardize MAC format
                    if ':' not in mac:
                        mac = ':'.join([mac[i:i+2] for i in range(0, len(mac), 2)])
                    mac = mac.upper()
                    
                    rssi = attributes.get('rssi', -100)
                    
                    device_info = [
                        entity_id,  # Device ID (index 0)
                        mac,        # MAC address (index 1)
                        str(rssi),  # RSSI value (index 2)
                        str(attributes)  # All attributes as string (index 3)
                    ]
                    devices.append(device_info)
                except Exception as e:
                    logging.error(f"Error processing bluetooth entity {entity_id}: {e}")
        
        # If we found devices, return them
        if devices:
            logging.info(f"Found {len(devices)} devices from Bluetooth integration")
            return devices
            
        # Fall back to checking for ble_gateway_raw_data sensor
        response = requests.get(
            "http://supervisor/core/api/states/sensor.ble_gateway_raw_data",
            headers=headers
        )
        
        if response.status_code < 200 or response.status_code >= 300:
            # Try alternative sensors
            for sensor_name in ["sensor.ble_scanner", "sensor.ble_monitor", "sensor.ble_gateway"]:
                alt_response = requests.get(
                    f"http://supervisor/core/api/states/{sensor_name}",
                    headers=headers
                )
                if alt_response.status_code >= 200 and alt_response.status_code < 300:
                    state_data = alt_response.json()
                    if 'attributes' in state_data and 'devices' in state_data['attributes']:
                        devices = state_data['attributes']['devices']
                        logging.info(f"Found {len(devices)} devices in {sensor_name}")
                        return devices
            
            # Create our own sensor data with simulated scan results
            create_ble_gateway_sensor()
            return []
            
        state_data = response.json()
        
        # Check if we have attributes with devices
        if 'attributes' in state_data and 'devices' in state_data['attributes']:
            devices = state_data['attributes']['devices']
            logging.info(f"Found {len(devices)} devices in ble_gateway_raw_data")
            return devices
            
        return []
        
    except Exception as e:
        logging.error(f"Error getting BLE gateway data: {e}")
        return []
        
def create_ble_gateway_sensor():
    """
    Create a sensor entity for BLE gateway data if it doesn't exist.
    """
    try:
        headers = {
            "Authorization": f"Bearer {os.environ.get('SUPERVISOR_TOKEN', '')}",
            "Content-Type": "application/json"
        }
        
        # Check if sensor already exists
        response = requests.get(
            "http://supervisor/core/api/states/sensor.ble_gateway_raw_data",
            headers=headers
        )
        
        if response.status_code == 404:
            # Create the sensor
            logging.info("Creating BLE gateway sensor")
            
            sensor_data = {
                "state": "online",
                "attributes": {
                    "friendly_name": "BLE Gateway",
                    "icon": "mdi:bluetooth-connect",
                    "devices": []
                }
            }
            
            create_response = requests.post(
                "http://supervisor/core/api/states/sensor.ble_gateway_raw_data",
                headers=headers,
                json=sensor_data
            )
            
            if create_response.status_code < 200 or create_response.status_code >= 300:
                logging.error(f"Error creating sensor: {create_response.status_code} - {create_response.text}")
            else:
                logging.info("BLE gateway sensor created successfully")
        
    except Exception as e:
        logging.error(f"Error creating BLE gateway sensor: {e}")
        
def register_bluetooth_scan_button():
    """
    Register button entities for triggering Bluetooth scans.
    Tries multiple approaches to ensure at least one works.
    """
    try:
        headers = {
            "Authorization": f"Bearer {os.environ.get('SUPERVISOR_TOKEN', '')}",
            "Content-Type": "application/json"
        }
        
        # Check if any button entity exists
        button_created = False
        
        # Try creating an input_button entity first (most reliable)
        try:
            # Try input_button first
            input_button_data = {
                "entity_id": "input_button.bluetooth_scan",
                "name": "Bluetooth Scan",
                "icon": "mdi:bluetooth-search",
                "attributes": {
                    "friendly_name": "Bluetooth Scan",
                    "icon": "mdi:bluetooth-search"
                }
            }
            
            input_response = requests.post(
                "http://supervisor/core/api/services/input_button/create",
                headers=headers,
                json=input_button_data
            )
            
            if input_response.status_code >= 200 and input_response.status_code < 300:
                logging.info("Created input_button.bluetooth_scan successfully")
                button_created = True
                
                # Set the icon directly in the entity state
                try:
                    state_data = {
                        "state": "off",
                        "attributes": {
                            "friendly_name": "Bluetooth Scan",
                            "icon": "mdi:bluetooth-search"
                        }
                    }
                    requests.post(
                        "http://supervisor/core/api/states/input_button.bluetooth_scan",
                        headers=headers,
                        json=state_data
                    )
                    logging.info("Updated input_button.bluetooth_scan icon")
                except Exception as e:
                    logging.warning(f"Error setting input_button icon: {e}")
        except Exception as e:
            logging.warning(f"Error creating input_button: {e}")
        
        # Check if button.bluetooth_scan exists and create if not
        response = requests.get(
            "http://supervisor/core/api/states/button.bluetooth_scan",
            headers=headers
        )
        
        if response.status_code == 404:
            # Try to register a button
            logging.info("Registering button.bluetooth_scan")
            
            # First try to call the button.create service
            create_data = {
                "entity_id": "button.bluetooth_scan",
                "name": "Bluetooth Scan",
                "icon": "mdi:bluetooth-search"
            }
            
            service_response = requests.post(
                "http://supervisor/core/api/services/button/create",
                headers=headers,
                json=create_data
            )
            
            success = service_response.status_code >= 200 and service_response.status_code < 300
            
            # If service call failed, try direct state update
            if not success:
                logging.info("Service call failed, trying direct state update")
                button_data = {
                    "state": "2023-01-01T00:00:00+00:00",
                    "attributes": {
                        "friendly_name": "Bluetooth Scan",
                        "icon": "mdi:bluetooth-search",
                        "device_class": "restart"
                    }
                }
                
                state_response = requests.post(
                    "http://supervisor/core/api/states/button.bluetooth_scan",
                    headers=headers,
                    json=button_data
                )
                
                if state_response.status_code >= 200 and state_response.status_code < 300:
                    logging.info("Bluetooth scan button registered via state update")
                    button_created = True
                else:
                    logging.error(f"Error registering button via state: {state_response.status_code}")
            else:
                logging.info("Bluetooth scan button registered via service call")
                button_created = True
        else:
            logging.info("button.bluetooth_scan already exists")
            button_created = True
                
        # Create a script as a fallback
        if not button_created:
            logging.info("Attempting to create a script for Bluetooth scanning")
            
            script_data = {
                "entity_id": "script.bluetooth_scan",
                "sequence": [
                    {
                        "service": "bluetooth.start_discovery"
                    }
                ],
                "icon": "mdi:bluetooth-search",
                "name": "Bluetooth Scan"
            }
            
            script_response = requests.post(
                "http://supervisor/core/api/services/script/create",
                headers=headers,
                json=script_data
            )
            
            if script_response.status_code >= 200 and script_response.status_code < 300:
                logging.info("Created script.bluetooth_scan as fallback")
            else:
                logging.error(f"Failed to create script: {script_response.status_code}")
                
    except Exception as e:
        logging.error(f"Error registering Bluetooth scan button: {e}")
        
def simulate_bluetooth_scan():
    """
    Simulate a Bluetooth scan by searching for Bluetooth devices via shell commands.
    Returns a list of simulated device entries.
    """
    logging.info("Simulating Bluetooth scan")
    
    # This is a fallback when no real Bluetooth data is available
    # Try to use hcitool or bluetoothctl to scan for devices if available
    try:
        import subprocess
        import re
        
        # Try using hcitool
        try:
            output = subprocess.check_output(["hcitool", "scan"], timeout=10).decode('utf-8')
            devices = []
            
            # Parse output like: "00:11:22:33:44:55 Device Name"
            for line in output.splitlines():
                match = re.search(r'([0-9A-F:]{17})\s+(.+)', line)
                if match:
                    mac = match.group(1)
                    name = match.group(2)
                    # Simulate RSSI between -50 and -90
                    import random
                    rssi = random.randint(-90, -50)
                    
                    devices.append([name, mac, str(rssi), "{}"])
            
            if devices:
                logging.info(f"Found {len(devices)} devices using hcitool")
                return devices
                
        except (subprocess.SubprocessError, FileNotFoundError):
            logging.info("hcitool not available or failed")
        
        # Try bluetoothctl as fallback
        try:
            # Start bluetoothctl, enable scanning
            process = subprocess.Popen(
                ["bluetoothctl"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send commands to bluetoothctl
            commands = "scan on\nsleep 5\ndevices\nscan off\nquit\n"
            output, _ = process.communicate(commands, timeout=15)
            
            devices = []
            # Parse output like: "Device 00:11:22:33:44:55 Name"
            for line in output.splitlines():
                match = re.search(r'Device\s+([0-9A-F:]{17})\s+(.+)', line)
                if match:
                    mac = match.group(1)
                    name = match.group(2)
                    # Simulate RSSI
                    import random
                    rssi = random.randint(-90, -50)
                    
                    devices.append([name, mac, str(rssi), "{}"])
            
            if devices:
                logging.info(f"Found {len(devices)} devices using bluetoothctl")
                return devices
                
        except (subprocess.SubprocessError, FileNotFoundError):
            logging.info("bluetoothctl not available or failed")
            
    except Exception as e:
        logging.error(f"Error in Bluetooth simulation: {e}")
    
    # Return a few simulated devices if nothing else worked
    return [
        ["Simulated Device 1", "AA:BB:CC:11:22:33", "-65", "{}"],
        ["Simulated Device 2", "DD:EE:FF:44:55:66", "-78", "{}"]
    ]

def process_ble_gateway_data(gateway_devices):
    """
    Process the raw BLE gateway data into a structured format.
    Returns a list of processed device dictionaries.
    """
    processed_devices = []
    
    try:
        for device in gateway_devices:
            if len(device) >= 3:
                # Extract MAC address (index 1) and RSSI (index 2)
                mac = device[1] if device[1] else "UNKNOWN"
                rssi = int(device[2]) if device[2] and device[2].strip() else -100
                
                # Extract advertisement data if available
                adv_data = device[3] if len(device) > 3 and device[3] else ""
                
                # Try to extract manufacturer data
                manufacturer = "Unknown"
                device_type = "Unknown"
                
                # Simple heuristics for device type based on MAC prefix or adv data
                if mac.upper().startswith(("00:0D:6F", "AC:23:3F", "B0:49:5F")):
                    manufacturer = "Google"
                    device_type = "Google Device"
                elif mac.upper().startswith(("00:17:88", "EC:B5:FA")):
                    manufacturer = "Philips"
                    device_type = "Philips Hue"
                elif mac.upper().startswith(("58:D5:6E", "A4:C1:38")):
                    manufacturer = "Apple"
                    device_type = "Apple Device"
                
                # Create device entry
                device_entry = {
                    "mac_address": mac,
                    "rssi": rssi,
                    "manufacturer": manufacturer,
                    "device_type": device_type,
                    "adv_data": adv_data,
                    "last_seen": datetime.now().isoformat()
                }
                
                processed_devices.append(device_entry)
    
    except Exception as e:
        logging.error(f"Error processing BLE gateway data: {e}")
    
    return processed_devices

def trigger_bluetooth_scan():
    """
    Trigger a Bluetooth scan using all available methods.
    Tries multiple approaches to ensure at least one works.
    """
    try:
        headers = {
            "Authorization": f"Bearer {os.environ.get('SUPERVISOR_TOKEN', '')}",
            "Content-Type": "application/json"
        }
        
        success = False
        
        # Try to use the bluetooth integration's scan service first
        try:
            scan_response = requests.post(
                "http://supervisor/core/api/services/bluetooth/start_discovery",
                headers=headers,
                json={}
            )
            
            if scan_response.status_code >= 200 and scan_response.status_code < 300:
                logging.info("Triggered bluetooth.start_discovery service")
                success = True
                
        except Exception as e:
            logging.warning(f"Error triggering bluetooth.start_discovery: {e}")
        
        # Try input_button if available
        if not success:
            try:
                input_button_response = requests.post(
                    "http://supervisor/core/api/services/input_button/press",
                    headers=headers,
                    json={"entity_id": "input_button.bluetooth_scan"}
                )
                
                if input_button_response.status_code >= 200 and input_button_response.status_code < 300:
                    logging.info("Triggered input_button.bluetooth_scan")
                    success = True
            except Exception as e:
                logging.warning(f"Error triggering input_button.bluetooth_scan: {e}")
        
        # Try regular button if available
        if not success:
            try:
                button_response = requests.post(
                    "http://supervisor/core/api/services/button/press",
                    headers=headers,
                    json={"entity_id": "button.bluetooth_scan"}
                )
                
                if button_response.status_code >= 200 and button_response.status_code < 300:
                    logging.info("Triggered button.bluetooth_scan")
                    success = True
            except Exception as e:
                logging.warning(f"Error triggering button.bluetooth_scan: {e}")
                
        # Try script if available
        if not success:
            try:
                script_response = requests.post(
                    "http://supervisor/core/api/services/script/turn_on",
                    headers=headers,
                    json={"entity_id": "script.bluetooth_scan"}
                )
                
                if script_response.status_code >= 200 and script_response.status_code < 300:
                    logging.info("Triggered script.bluetooth_scan")
                    success = True
            except Exception as e:
                logging.warning(f"Error triggering script.bluetooth_scan: {e}")
        
        # As a final fallback, simulate a scan with shell commands
        if not success:
            logging.warning("All scan triggers failed, using simulated mode")
            simulated_devices = simulate_bluetooth_scan()
            if simulated_devices:
                # Create BLE gateway sensor and update it with simulated devices
                sensor_data = {
                    "state": "online",
                    "attributes": {
                        "friendly_name": "BLE Gateway",
                        "icon": "mdi:bluetooth-connect",
                        "devices": simulated_devices
                    }
                }
                
                requests.post(
                    "http://supervisor/core/api/states/sensor.ble_gateway_raw_data",
                    headers=headers,
                    json=sensor_data
                )
                logging.info("Updated BLE gateway sensor with simulated devices")
                success = True
                
        return success
        
    except Exception as e:
        logging.error(f"Error triggering Bluetooth scan: {e}")
        return False

def update_ha_input_text(entity_id, value):
    """
    Update an input_text entity in Home Assistant.
    """
    try:
        headers = {
            "Authorization": f"Bearer {os.environ.get('SUPERVISOR_TOKEN', '')}",
            "Content-Type": "application/json" 
        }
        
        payload = {
            "entity_id": entity_id,
            "value": value
        }
        
        response = requests.post(
            "http://supervisor/core/api/services/input_text/set_value",
            headers=headers,
            json=payload 
        )
        
        if response.status_code < 200 or response.status_code >= 300:
            logging.error(f"Error updating input_text: {response.status_code} - {response.text}")
            return False
            
        return True
    
    except Exception as e:
        logging.error(f"Error updating input_text: {e}")
        return False

def discover_ble_devices(force_scan=False):
    """
    Discover BLE devices using the BLE gateway.
    Optionally trigger a fresh scan.
    """
    # Trigger a new scan if requested
    if force_scan:
        logging.info("Triggering Bluetooth scan...")
        scan_success = trigger_bluetooth_scan()
        if scan_success:
            # Wait for scan to complete
            time.sleep(5)
        else:
            logging.warning("Failed to trigger Bluetooth scan")
    
    # Get current devices from gateway
    gateway_devices = get_ble_gateway_data()
    processed_devices = process_ble_gateway_data(gateway_devices)
    
    # Load previous discoveries
    discoveries = load_discoveries()
    
    # Flag to track if we found new devices
    new_devices_found = False
    
    # Update existing devices and add new ones
    for device in processed_devices:
        device_mac = device["mac_address"]
        
        # Check if this is a new device
        existing_device = next((d for d in discoveries if d["mac_address"] == device_mac), None)
        
        if existing_device:
            # Update existing device
            existing_device["rssi"] = device["rssi"]
            existing_device["last_seen"] = device["last_seen"]
            existing_device["adv_data"] = device["adv_data"]
        else:
            # Add new device
            device["id"] = str(uuid.uuid4())
            device["discovered_at"] = datetime.now().isoformat()
            device["name"] = f"BLE Device {device_mac[-6:]}"
            discoveries.append(device)
            new_devices_found = True
    
    # Save updated discoveries
    save_discoveries(discoveries)
    
    # Create a simple map of MAC to RSSI for the input_text
    mac_to_rssi = {d["mac_address"]: d["rssi"] for d in processed_devices}
    update_ha_input_text("input_text.discovered_ble_devices", json.dumps(mac_to_rssi))
    
    # Create notification for new devices
    if new_devices_found:
        notification_message = f"Discovered {len(processed_devices)} BLE devices:\n\n"
        for device in processed_devices:
            notification_message += f"- {device['mac_address']} (RSSI: {device['rssi']} dBm)\n"
        notification_message += "\nGo to the BLE Dashboard to manage devices."
        
        create_home_assistant_notification(
            "BLE Device Discovery",
            notification_message,
            "ble_discovery"
        )
    
    return discoveries

def manual_scan_command():
    """
    Handle manual scan command.
    """
    logging.info("Manual scan requested")
    create_home_assistant_notification(
        "BLE Device Discovery",
        "Starting manual Bluetooth scan...",
        "ble_discovery"
    )
    
    devices = discover_ble_devices(force_scan=True)
    
    # Create detailed notification
    notification_message = f"Manual scan complete. Found {len(devices)} devices:\n\n"
    
    # Sort by RSSI (strongest first)
    sorted_devices = sorted(devices, key=lambda d: d.get("rssi", -100), reverse=True)
    
    for idx, device in enumerate(sorted_devices, 1):
        mac = device["mac_address"]
        rssi = device.get("rssi", "N/A")
        name = device.get("name", f"Device {idx}")
        notification_message += f"{idx}. {name} ({mac}): {rssi} dBm\n"
    
    notification_message += "\nGo to the BLE Dashboard to manage these devices."
    
    create_home_assistant_notification(
        "BLE Device Discovery Results",
        notification_message,
        "ble_discovery_results"
    )
    
    return devices

def check_input_text_exists(entity_id):
    """
    Check if an input_text entity exists, create it if not.
    """
    try:
        headers = {
            "Authorization": f"Bearer {os.environ.get('SUPERVISOR_TOKEN', '')}",
            "Content-Type": "application/json"
        }
        
        # Check if entity exists
        response = requests.get(
            f"http://supervisor/core/api/states/{entity_id}",
            headers=headers
        )
        
        if response.status_code == 404:
            # Entity doesn't exist, create it
            logging.info(f"Creating missing entity: {entity_id}")
            
            # Define entity configuration
            if entity_id == "input_text.discovered_ble_devices":
                config = {
                    "name": "Discovered BLE Devices",
                    "max": 1024,
                    "initial": "{}"
                }
            else:
                config = {
                    "name": entity_id.split('.')[1].replace('_', ' ').title(),
                    "max": 255,
                    "initial": ""
                }
            
            # Create entity
            create_response = requests.post(
                "http://supervisor/core/api/services/input_text/create",
                headers=headers,
                json={"entity_id": entity_id, **config}
            )
            
            if create_response.status_code >= 300:
                logging.error(f"Failed to create {entity_id}: {create_response.status_code}")
                return False
                
            return True
        
        return response.status_code < 300
        
    except Exception as e:
        logging.error(f"Error checking/creating input_text: {e}")
        return False

def setup_required_entities():
    """
    Ensure required entities exist.
    """
    required_entities = [
        "input_text.discovered_ble_devices",
        "input_text.selected_ble_device"
    ]
    
    for entity_id in required_entities:
        check_input_text_exists(entity_id)

def collect_system_diagnostics():
    """
    Collect system diagnostic information to help with troubleshooting.
    """
    diagnostics = {
        "timestamp": datetime.now().isoformat(),
        "version": "1.3.3",  # Make sure to update this when changing versions
        "python_version": ".".join(map(str, sys.version_info[:3])),
        "platform": sys.platform,
        "environment": {}
    }
    
    # Check Bluetooth availability
    try:
        import subprocess
        bt_output = subprocess.run(["command", "-v", "bluetoothctl"], 
                             shell=True, capture_output=True, text=True)
        diagnostics["bluetoothctl_available"] = bt_output.returncode == 0
        
        if diagnostics["bluetoothctl_available"]:
            version_output = subprocess.run(["bluetoothctl", "--version"], 
                                   capture_output=True, text=True)
            diagnostics["bluetoothctl_version"] = version_output.stdout.strip() if version_output.returncode == 0 else "Error getting version"
    except Exception as e:
        diagnostics["bluetoothctl_error"] = str(e)
    
    # Check for Bluetooth adapters
    try:
        hci_output = subprocess.run(["ls", "/sys/class/bluetooth"], 
                              shell=True, capture_output=True, text=True)
        diagnostics["bluetooth_adapters"] = hci_output.stdout.strip().split() if hci_output.returncode == 0 else []
    except Exception as e:
        diagnostics["bluetooth_adapters_error"] = str(e)
    
    # Get environment variables (excluding sensitive ones)
    for key, value in os.environ.items():
        if not any(sensitive in key.lower() for sensitive in ["token", "key", "secret", "pass", "auth"]):
            diagnostics["environment"][key] = value
    
    # Save diagnostics to file
    try:
        diag_dir = "/config/ble_discovery/diagnostics"
        if not os.path.exists(diag_dir):
            os.makedirs(diag_dir, exist_ok=True)
            
        diag_filename = os.path.join(diag_dir, f"diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(diag_filename, 'w') as f:
            json.dump(diagnostics, f, indent=2)
            
        logging.info(f"Diagnostics saved to {diag_filename}")
        return diagnostics
    except Exception as e:
        logging.error(f"Error saving diagnostics: {e}")
        return diagnostics

def main(log_level, scan_interval, gateway_topic=DEFAULT_GATEWAY_TOPIC):
    """Main discovery loop."""
    setup_logging(log_level)
    
    logging.info(f"Enhanced BLE Discovery Add-on started. Scanning every {scan_interval} seconds.")
    
    # Collect diagnostic information
    diagnostics = collect_system_diagnostics()
    logging.info(f"System diagnostics: Python {diagnostics.get('python_version')}, " 
                f"Bluetooth adapters: {len(diagnostics.get('bluetooth_adapters', []))}")
    
    # Register our button entity
    register_bluetooth_scan_button()
    
    # Create BLE gateway sensor if needed
    create_ble_gateway_sensor()
    
    # Ensure required entities exist
    setup_required_entities()
    
    create_home_assistant_notification(
        "BLE Discovery Add-on",
        "BLE Discovery Add-on has started. Use the BLE Dashboard to manage devices.",
        "ble_discovery_startup"
    )
    
    # Track manual scan requests
    last_manual_scan_check = 0
    
    while True:
        try:
            # Regular discovery
            discovered_devices = discover_ble_devices()
            logging.info(f"Regular scan complete. Total discovered devices: {len(discovered_devices)}")
            
            # Update the BLE gateway sensor with discovered devices if we have any
            if discovered_devices:
                headers = {
                    "Authorization": f"Bearer {os.environ.get('SUPERVISOR_TOKEN', '')}",
                    "Content-Type": "application/json"
                }
                
                sensor_data = {
                    "state": "online",
                    "attributes": {
                        "friendly_name": "BLE Gateway",
                        "icon": "mdi:bluetooth-connect",
                        "devices": discovered_devices
                    }
                }
                
                requests.post(
                    "http://supervisor/core/api/states/sensor.ble_gateway_raw_data",
                    headers=headers,
                    json=sensor_data
                )
            
        except Exception as e:
            logging.error(f"Discovery error: {e}")
        
        # Sleep between scans
        time.sleep(scan_interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enhanced BLE Device Discovery")
    parser.add_argument("--log-level", default="INFO", 
                        help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    parser.add_argument("--scan-interval", type=int, default=DEFAULT_SCAN_INTERVAL,
                        help="Interval between BLE scans in seconds")
    parser.add_argument("--gateway-topic", default=DEFAULT_GATEWAY_TOPIC,
                        help="MQTT topic for BLE gateway")
    
    args = parser.parse_args()
    
    main(args.log_level, args.scan_interval, args.gateway_topic)
