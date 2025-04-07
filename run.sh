#!/usr/bin/with-contenv bash
source /usr/lib/bashio/bashio.sh

LOG_LEVEL=$(bashio::config 'log_level')
SCAN_INTERVAL=$(bashio::config 'scan_interval')
GATEWAY_TOPIC=$(bashio::config 'gateway_topic')

mkdir -p /config/ble_discovery

if [ ! -f "/.dependencies_installed" ]; then
    bashio::log.info "Installing additional dependencies..."
    pip3 install --no-cache-dir requests
    touch "/.dependencies_installed"
fi

if [ ! -f "/config/dashboards/btle_dashboard.yaml" ]; then
    bashio::log.info "Creating BLE dashboard..."
    mkdir -p /config/dashboards
    cp /btle_dashboard.yaml /config/dashboards/
fi

if [ ! -f "/config/input_text.yaml" ] || ! grep -q "discovered_ble_devices" "/config/input_text.yaml"; then
    bashio::log.info "Ensuring input helpers are available..."
    if [ -f "/config/input_text.yaml" ]; then
        cat /ble_input_text.yaml >> /config/input_text.yaml
    else
        cp /ble_input_text.yaml /config/input_text.yaml
    fi
fi

bashio::log.info "Starting Enhanced BLE Device Discovery..."

python3 /ble_discovery.py \
    --log-level "${LOG_LEVEL}" \
    --scan-interval "${SCAN_INTERVAL}" \
    --gateway-topic "${GATEWAY_TOPIC}"
