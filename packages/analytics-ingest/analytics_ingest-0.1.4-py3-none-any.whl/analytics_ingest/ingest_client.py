from analytics_ingest.internal.graphql_executor import GraphQLExecutor
from analytics_ingest.internal.mutations import GraphQLMutations
from analytics_ingest.internal.batching import Batcher
from analytics_ingest.internal.message_utils import create_message

import os
from datetime import datetime
from typing import Optional


class AnalyticsIngestClient:
    def __init__(
        self,
        device_id: int,
        vehicle_id: int,
        fleet_id: int,
        org_id: int,
        *,
        batch_interval_seconds: int = 10,
        batch_size: int = 100,
        graphql_endpoint: Optional[str] = None,
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

        self.executor = GraphQLExecutor(self.graphql_endpoint, self.jwt_token)

        try:
            config_resp = self.executor.execute(
                GraphQLMutations.create_configuration(),
                {
                    "input": {
                        "deviceId": self.device_id,
                        "fleetId": self.fleet_id,
                        "organizationId": self.org_id,
                        "vehicleId": self.vehicle_id,
                    }
                }
            )
            self.configuration_id = config_resp["data"]["createConfiguration"]["id"]
        except Exception as e:
            raise RuntimeError(f"Failed to create configuration: {e}")

    def add_signal(self, variables: Optional[dict] = None):
        if not variables:
            raise ValueError("Missing 'variables' dictionary")

        try:
            message_id = create_message(self.executor, variables)
        except Exception as e:
            raise RuntimeError(f"Failed to create message: {e}")

        if "data" not in variables:
            raise ValueError("Missing required field: 'data'")

        batched_data = Batcher.create_batches(variables["data"], self.batch_size)

        for batch in batched_data:
            try:
                self.executor.execute(
                    GraphQLMutations.upsert_signal_data(),
                    {
                        "input": {
                            "signals": {
                                "configurationId": self.configuration_id,
                                "data": batch,
                                "messageId": message_id,
                                "name": variables["name"],
                                "paramId": variables.get("paramId", ""),
                                "paramType": variables.get("paramType", ""),
                                "signalType": variables.get("signalType", ""),
                                "unit": variables["unit"],
                            }
                        }
                    }
                )
            except Exception as e:
                raise RuntimeError(f"Failed to upsert signal data: {e}")
   
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
