import tempfile
import unittest
from pathlib import Path

from database import count_emails, get_all_emails, initialize_database, is_registered


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.sqlite3"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_deterministic_initialization_and_exact_lookup(self):
        count = initialize_database(self.db_path, ["A@example.com", "b@example.com"])
        self.assertEqual(count, 2)
        self.assertTrue(is_registered(" A@EXAMPLE.COM ", self.db_path))
        self.assertFalse(is_registered("nope@example.org", self.db_path))

    def test_initialize_is_idempotent(self):
        initialize_database(self.db_path, ["a@example.com"])
        initialize_database(self.db_path, ["a@example.com"])
        self.assertEqual(count_emails(self.db_path), 1)

    def test_reset_replaces_collection(self):
        initialize_database(self.db_path, ["a@example.com", "b@example.com"])
        initialize_database(self.db_path, ["c@example.com"], reset=True)
        self.assertEqual(get_all_emails(self.db_path), ["c@example.com"])

    def test_default_dataset_has_1000_synthetic_addresses(self):
        self.assertEqual(initialize_database(self.db_path), 1000)
        self.assertTrue(all(email.endswith("@example.com") for email in get_all_emails(self.db_path)))


if __name__ == "__main__":
    unittest.main()
