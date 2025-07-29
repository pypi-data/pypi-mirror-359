import unittest
from datetime import datetime
from analytics_ingest.client import AnalyticsIngestClient

class TestAnalyticsIngestClient(unittest.TestCase):

    def setUp(self):
        self.client = AnalyticsIngestClient(
            device_id=1,
            vehicle_id=2,
            fleet_id=3,
            org_id=4,
            batch_interval_seconds=5,
            batch_size=50,
            jwt_token="mock-token",
            cert_path="/path/to/cert"
        )

    def test_init(self):
        self.assertEqual(self.client.device_id, 1)
        self.assertEqual(self.client.vehicle_id, 2)
        self.assertEqual(self.client.fleet_id, 3)
        self.assertEqual(self.client.org_id, 4)

    def test_add_signal(self):
        try:
            self.client.add_signal(
                signal_name="rpm",
                message_name="EngineStatus",
                network_name="CAN1",
                ecu_name="ECU1",
                value=3000.0,
                time=datetime.utcnow(),
                unit="rpm",
                svalue=None,
                param_type=None,
                param_id=None,
                signal_type="float"
            )
        except Exception as e:
            self.fail(f"add_signal raised Exception: {e}")

    def test_add_dtc(self):
        try:
            self.client.add_dtc(
                message_name="DTCReport",
                network_name="CAN1",
                ecu_name="ECU2",
                dtc_id="P0420",
                status="Active",
                description="Catalyst System Efficiency Below Threshold",
                time=datetime.utcnow(),
                message_date=datetime.utcnow(),
                file_id=None,
                snapshot_bytes=None,
                extended_bytes=None
            )
        except Exception as e:
            self.fail(f"add_dtc raised Exception: {e}")

    def test_add_gps(self):
        try:
            self.client.add_gps(
                time=datetime.utcnow(),
                latitude=31.5204,
                longitude=74.3587,
                speed=60.5,
                altitude=200.0
            )
        except Exception as e:
            self.fail(f"add_gps raised Exception: {e}")

    def test_add_network_stats(self):
        try:
            self.client.add_network_stats(
                name="UploadStats",
                upload_id=101,
                total_messages=10000,
                matched_messages=9500,
                unmatched_messages=300,
                error_messages=100,
                long_message_parts=50,
                rate=100.0,
                min_time=datetime.utcnow(),
                max_time=datetime.utcnow()
            )
        except Exception as e:
            self.fail(f"add_network_stats raised Exception: {e}")

    def test_flush(self):
        try:
            self.client.flush()
        except Exception as e:
            self.fail(f"flush raised Exception: {e}")

    def test_close(self):
        try:
            self.client.close()
        except Exception as e:
            self.fail(f"close raised Exception: {e}")


if __name__ == "__main__":
    unittest.main()
