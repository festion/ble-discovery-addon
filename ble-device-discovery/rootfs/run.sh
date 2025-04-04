#!/usr/bin/with-contenv bashio

# Get configuration options
LOG_LEVEL=$(bashio::config 'log_level')
SCAN_INTERVAL=$(bashio::config 'scan_interval')

# Run the Python script
python3 /ble_discovery.py --log-level "${LOG_LEVEL}" --scan-interval "${SCAN_INTERVAL}"