def make_configuration_input(device_id, fleet_id, org_id, vehicle_id):
    return {
        "input": {
            "deviceId": device_id,
            "fleetId": fleet_id,
            "organizationId": org_id,
            "vehicleId": vehicle_id,
        }
    }
