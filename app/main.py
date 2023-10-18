""" 
Copyright (c) 2023 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

import csv
import json
import meraki
import config as config

dashboard = meraki.DashboardAPI(config.api_key, single_request_timeout=999999,suppress_logging=True)

orgs = dashboard.organizations.getOrganizations()
org_id = config.org_id

networks_data = {}

for network in dashboard.organizations.getOrganizationNetworks(organizationId=org_id):
    devices_data = []
    for device in dashboard.networks.getNetworkDevices(networkId=network['id']):
        if device['model'].startswith('MS'):
            summary = dashboard.switch.getDeviceSwitchPortsStatuses(device['serial'])
            total_power_usage = sum([port['powerUsageInWh'] for port in summary if 'powerUsageInWh' in port])
            devices_data.append({'Device Serial': device['serial'], 'Total Power Usage (Wh)': total_power_usage})
    networks_data[network['name']] = devices_data

# Generate CSV report
with open('app/power_usage_report.csv', 'w', newline='') as csvfile:
    fieldnames = ['Network Name', 'Device Serial', 'Total Power Usage (Wh)']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for network_name, devices in networks_data.items():
        for device in devices:
            writer.writerow({'Network Name': network_name, **device})

# Prepare data for JSON report
json_data = [{'Network Name': network_name, 'Devices': devices} for network_name, devices in networks_data.items()]

# Generate JSON report
with open('app/power_usage_report.json', 'w') as jsonfile:
    json.dump(json_data, jsonfile, indent=4)

print("Reports generated successfully!")
