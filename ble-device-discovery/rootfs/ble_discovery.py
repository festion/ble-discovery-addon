#!/usr/bin/env python3
"""
Enhanced BLE Device Discovery Add-on for Home Assistant
"""

import argparse
import json
import logging
import os
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
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - BLE Discovery - %(levelname)s - %(message)s'
    )

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
    Get BLE gateway data from MQTT state.
    Returns a list of discovered devices.
    """
    try:
        headers = {
            "Authorization": f"Bearer {os.environ.get('SUPERVISOR_TOKEN', '')}",
            "Content-Type": "application/json"
        }
        
        # Get the current state of the BLE gateway sensor
        response = requests.get(
            "http://supervisor/core/api/states/sensor.ble_gateway_raw_data",
            headers=headers
        )
        
        if response.status_code < 200 or response.status_code >= 300:
            logging.error(f"Error getting BLE gateway state: {response.status_code} - {response.text}")
            return []
            
        state_data = response.json()
        
        # Check if we have attributes with devices
        if 'attributes' in state_data and 'devices' in state_data['attributes']:
            devices = state_data['attributes']['devices']
            logging.info(f"Found {len(devices)} devices in BLE gateway data")
            return devices
            
        return []
        
    except Exception as e:
        logging.error(f"Error getting BLE gateway data: {e}")
        return []

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
    Trigger a Bluetooth scan using the button entity.
    """
    try:
        headers = {
            "Authorization": f"Bearer {os.environ.get('SUPERVISOR_TOKEN', '')}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "entity_id": "button.bluetooth_scan"
        }
        
        response = requests.post(
            "http://supervisor/core/api/services/button/press",
            headers=headers,
            json=payload
        )
        
        if response.status_code < 200 or response.status_code >= 300:
            logging.error(f"Error triggering Bluetooth scan: {response.status_code} - {response.text}")
            return False
            
        return True
        
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

def main(log_level, scan_interval, gateway_topic=DEFAULT_GATEWAY_TOPIC):
    """Main discovery loop."""
    setup_logging(log_level)
    
    logging.info(f"Enhanced BLE Discovery Add-on started. Scanning every {scan_interval} seconds.")
    
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