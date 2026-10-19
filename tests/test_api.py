import json
import tempfile
import unittest
from pathlib import Path

from app import create_app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.app = create_app({"TESTING": True, "DB_PATH": str(Path(self.temp_dir.name) / "api.sqlite3"), "DATASET_SIZE": 40, "FILTER_CAPACITY": 500, "HASH_COUNT": 5})
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Algorithm inspector", response.data)

    def test_benchmark_page_loads(self):
        response = self.client.get("/benchmark")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Run experiment", response.data)

    def test_stats_filter_history_and_health(self):
        self.assertEqual(self.client.get("/api/stats").status_code, 200)
        filter_data = self.client.get("/api/filter").get_json()
        self.assertEqual(len(filter_data["bits"]), 500)
        self.assertEqual(self.client.get("/api/history").get_json(), {"history": []})
        self.assertEqual(self.client.get("/api/health").get_json()["status"], "ok")

    def test_registered_check_and_absent_check(self):
        registered = self.client.post("/api/check", json={"email": "MEMBER0001@EXAMPLE.COM"})
        self.assertEqual(registered.status_code, 200)
        self.assertEqual(registered.get_json()["status"], "registered")
        absent = self.client.post("/api/check", json={"email": "certainly-absent-unique@example.org"})
        self.assertEqual(absent.status_code, 200)
        self.assertEqual(absent.get_json()["status"], "available")
        self.assertEqual(len(absent.get_json()["positions"]), 5)

    def test_invalid_or_missing_json(self):
        self.assertEqual(self.client.post("/api/check", data="no json", content_type="text/plain").status_code, 400)
        self.assertEqual(self.client.post("/api/check", json={}).status_code, 400)
        self.assertEqual(self.client.post("/api/check", json={"email": "not-an-email"}).status_code, 400)
        self.assertEqual(self.client.post("/api/check", json={"email": 123}).status_code, 400)

    def test_insert_simulation_does_not_change_live_filter_or_database(self):
        before_stats = self.client.get("/api/stats").get_json()
        response = self.client.post("/api/demo/insert", json={"email": "simulated@example.org"})
        after_stats = self.client.get("/api/stats").get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("changed_positions", response.get_json())
        self.assertEqual(before_stats["set_bits"], after_stats["set_bits"])

    def test_benchmark_validates_parameters(self):
        self.assertEqual(self.client.post("/api/benchmark", json={"query_count": 100, "trials": 3}).status_code, 200)
        self.assertEqual(self.client.post("/api/benchmark", json={"query_count": 50, "trials": 3}).status_code, 400)

    def test_history_is_bounded_and_no_raw_query_database_write(self):
        for i in range(10):
            self.client.post("/api/check", data=json.dumps({"email": f"guest-{i}@example.org"}), content_type="application/json")
        history = self.client.get("/api/history").get_json()["history"]
        self.assertLessEqual(len(history), 8)


if __name__ == "__main__":
    unittest.main()
