#!/usr/bin/with-contenv bashio

# Get configuration options
LOG_LEVEL=$(bashio::config 'log_level')
SCAN_INTERVAL=$(bashio::config 'scan_interval')
GATEWAY_TOPIC=$(bashio::config 'gateway_topic')

# Ensure the data directory exists
mkdir -p /config/ble_discovery

# Install any additional dependencies if needed
if [ ! -f "/.dependencies_installed" ]; then
    bashio::log.info "Installing additional dependencies..."
    pip3 install --no-cache-dir requests
    touch "/.dependencies_installed"
fi

# Create dashboard if it doesn't exist
if [ ! -f "/config/dashboards/btle_dashboard.yaml" ]; then
    bashio::log.info "Creating BLE dashboard..."
    mkdir -p /config/dashboards
    cp /btle_dashboard.yaml /config/dashboards/
fi

# Create input helpers if they don't exist
if [ ! -f "/config/input_text.yaml" ] || ! grep -q "discovered_ble_devices" "/config/input_text.yaml"; then
    bashio::log.info "Ensuring input helpers are available..."
    
    # Check if file exists first
    if [ -f "/config/input_text.yaml" ]; then
        # Append to existing file
        cat /ble_input_text.yaml >> /config/input_text.yaml
    else
        # Create new file
        cp /ble_input_text.yaml /config/input_text.yaml
    fi
fi

# Announce startup
bashio::log.info "Starting Enhanced BLE Device Discovery..."

# Run the Python script
python3 /ble_discovery.py \
    --log-level "${LOG_LEVEL}" \
    --scan-interval "${SCAN_INTERVAL}" \
    --gateway-topic "${GATEWAY_TOPIC}"