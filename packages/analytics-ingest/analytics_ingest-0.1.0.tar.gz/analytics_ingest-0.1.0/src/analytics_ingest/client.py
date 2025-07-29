import os
import requests
from graphql import parse, print_ast

create_configuration_mutation = """
mutation createConfiguration($input: CreateConfigurationInput!) {
  createConfiguration(input: $input) {
    id
    deviceId
    vehicleId
    organizationId
    fleetId
  }
}
"""

class AnalyticsIngestClient:
    def __init__(
        self,
        device_id: int,
        vehicle_id: int,
        fleet_id: int,
        org_id: int,
        *,
        graphql_endpoint: Optional[str] = None,
        batch_interval_seconds: int = 10,
        batch_size: int = 100,
        jwt_token: Optional[str] = None,
        cert_path: Optional[str] = None
    ):
        self.device_id = device_id
        self.vehicle_id = vehicle_id
        self.fleet_id = fleet_id
        self.org_id = org_id
        self.batch_interval_seconds = batch_interval_seconds
        self.batch_size = batch_size
        self.jwt_token = jwt_token or os.getenv("SEC_AUTH_TOKEN")
        self.cert_path = cert_path

        self.graphql_endpoint = graphql_endpoint or os.getenv("GRAPH_ENDPOINT")
        if not self.graphql_endpoint:
            raise ValueError("GraphQL endpoint must be provided or set in GRAPH_ENDPOINT")

        headers = {}
        if self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"

        request_data = {
            "query": print_ast(parse(create_configuration_mutation)),
            "variables": {
                "input": {
                    "deviceId": self.device_id,
                    "vehicleId": self.vehicle_id,
                    "fleetId": self.fleet_id,
                    "organizationId": self.org_id
                }
            }
        }

        response = requests.post(self.graphql_endpoint, json=request_data, headers=headers)

        if not response.ok:
            raise RuntimeError(f"GraphQL request failed: {response.status_code} {response.text}")

        result = response.json()
        if "errors" in result or "data" not in result or not result["data"].get("createConfiguration"):
            raise RuntimeError(f"GraphQL mutation failed: {result.get('errors')}")

        self.configuration_id = result["data"]["createConfiguration"]["id"]

    def add_signal(
        self,
        signal_name: str,
        message_name: str,
        network_name: str,
        ecu_name: str,
        value: Optional[float],
        time: datetime,
        unit: str,
        svalue: Optional[str] = None,
        param_type: Optional[str] = None,
        param_id: Optional[str] = None,
        signal_type: Optional[str] = None,
    ):
        """
        Queues a signal for batching and ingestion.
        """
        pass

    def add_dtc(
        self,
        message_name: str,
        network_name: str,
        ecu_name: str,
        dtc_id: str,
        status: str,
        description: str,
        time: datetime,
        message_date: datetime,
        file_id: Optional[str] = None,
        snapshot_bytes: Optional[str] = None,
        extended_bytes: Optional[str] = None,
    ):
        """
        Queues a DTC event.
        """
        pass

    def add_gps(
        self,
        time: datetime,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        accuracy: Optional[float] = None,
        altitude: Optional[float] = None,
        speed: Optional[float] = None,
        bearing: Optional[float] = None,
        available: Optional[float] = None,
    ):
        """
        Queues a GPS reading.
        """
        pass

    def add_network_stats(
        self,
        name: str,
        upload_id: int,
        total_messages: int,
        matched_messages: int,
        unmatched_messages: int,
        error_messages: int,
        long_message_parts: int,
        rate: float,
        min_time: Optional[datetime] = None,
        max_time: Optional[datetime] = None
    ):
        """
        Sends a network stats object immediately (not batched).
        """
        pass

    def flush(self):
        """
        Flushes all queued data to Graph immediately.
        """
        pass

    def close(self):
        """
        Flushes remaining data and shuts down internal batching workers.
        """
        pass
