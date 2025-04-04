#!/usr/bin/env python3
"""
BLE Device Discovery Add-on for Home Assistant
"""

import argparse
import json
import logging
import os
import time
from datetime import datetime
import uuid  # This is a built-in module, no need for separate installation

import requests

# Configuration
DISCOVERIES_FILE = "/config/bluetooth_discoveries.json"
DEFAULT_SCAN_INTERVAL = 60

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

def create_home_assistant_notification(message):
    """Create a notification in Home Assistant."""
    try:
        # This assumes you've set up a long-lived access token
        headers = {
            "Authorization": f"Bearer {os.environ.get('SUPERVISOR_TOKEN', '')}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "title": "BLE Device Discovery",
            "message": message
        }
        
        requests.post(
            "http://supervisor/core/api/services/persistent_notification/create", 
            headers=headers, 
            json=payload
        )
    except Exception as e:
        logging.error(f"Error creating notification: {e}")

def discover_ble_devices():
    """
    Discover BLE devices.
    This is a placeholder and should be replaced with actual scanning logic.
    """
    discoveries = load_discoveries()
    
    # Simulate device discovery - replace with actual BLE scanning
    test_device = {
        'id': str(uuid.uuid4()),
        'mac_address': f"00:11:22:33:44:{str(len(discoveries)).zfill(2)}",
        'name': f"Test Device {len(discoveries) + 1}",
        'rssi': -50 - (len(discoveries) * 5),
        'discovered_at': datetime.now().isoformat()
    }
    
    # Check for duplicates
    if not any(d['mac_address'] == test_device['mac_address'] for d in discoveries):
        discoveries.append(test_device)
        save_discoveries(discoveries)
        
        # Create notification
        create_home_assistant_notification(
            f"Discovered new BLE device: {test_device['name']} ({test_device['mac_address']})"
        )
    
    return discoveries

def main(log_level, scan_interval):
    """Main discovery loop."""
    setup_logging(log_level)
    
    logging.info(f"BLE Discovery Add-on started. Scanning every {scan_interval} seconds.")
    
    while True:
        try:
            discovered_devices = discover_ble_devices()
            logging.info(f"Total discovered devices: {len(discovered_devices)}")
        except Exception as e:
            logging.error(f"Discovery error: {e}")
        
        # Sleep between scans
        time.sleep(scan_interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BLE Device Discovery")
    parser.add_argument("--log-level", default="INFO", 
                        help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    parser.add_argument("--scan-interval", type=int, default=DEFAULT_SCAN_INTERVAL,
                        help="Interval between BLE scans in seconds")
    
    args = parser.parse_args()
    
    main(args.log_level, args.scan_interval)