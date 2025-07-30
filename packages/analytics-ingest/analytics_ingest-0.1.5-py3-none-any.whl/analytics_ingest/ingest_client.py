import os
from datetime import datetime
from typing import Optional

from analytics_ingest.internal.batching import Batcher
from analytics_ingest.internal.configuration import ConfigurationService
from analytics_ingest.internal.graphql_executor import GraphQLExecutor
from analytics_ingest.internal.message_utils import create_message
from analytics_ingest.internal.mutations import GraphQLMutations
from analytics_ingest.internal.schemas.ingest_config import IngestConfigSchema


class AnalyticsIngestClient:
    def __init__(self, **kwargs):

        try:
            self.config = IngestConfigSchema(**kwargs)

        except Exception as e:
            raise ValueError(f"Invalid config: {e}")

        self.executor = GraphQLExecutor(
            self.config.graphql_endpoint, self.config.jwt_token
        )

        self.configuration_id = ConfigurationService(self.executor).create(
            self.config.device_id,
            self.config.fleet_id,
            self.config.org_id,
            self.config.vehicle_id,
        )["data"]["createConfiguration"]["id"]

    def add_signal(self, variables: Optional[dict] = None):
        if not variables:
            raise ValueError("Missing 'variables' dictionary")

        try:
            message_id = create_message(self.executor, variables)
        except Exception as e:
            raise RuntimeError(f"Failed to create message: {e}")

        if "data" not in variables:
            raise ValueError("Missing required field: 'data'")

        batched_data = Batcher.create_batches(variables["data"], self.config.batch_size)

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
                    },
                )
            except Exception as e:
                raise RuntimeError(f"Failed to upsert signal data: {e}")

    def add_dtc(self, variables: Optional[dict] = None):
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
        max_time: Optional[datetime] = None,
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
