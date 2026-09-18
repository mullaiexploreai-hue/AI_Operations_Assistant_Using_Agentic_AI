import tempfile
import unittest
from pathlib import Path

import db.connection as db_connection
import db.init_db as init_db
from tools.support_tools import create_ticket, lookup_ticket, search_knowledge_base


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = str(Path(self.temp_dir.name) / "support.db")
        self.original_db_path = db_connection.DB_PATH
        db_connection.DB_PATH = self.database_path
        init_db.build_database()

    def tearDown(self):
        db_connection.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def test_knowledge_search_returns_seeded_article(self):
        result = search_knowledge_base("reset VPN password")
        self.assertTrue(result["found"])
        self.assertEqual(result["results"][0]["article_id"], "KB-001")

    def test_knowledge_search_returns_other_matching_article(self):
        result = search_knowledge_base("replacement laptop asset tag")
        self.assertTrue(result["found"])
        self.assertEqual(result["results"][0]["article_id"], "KB-002")

    def test_knowledge_search_returns_no_match(self):
        result = search_knowledge_base("reserve a parking space")
        self.assertTrue(result["ok"])
        self.assertFalse(result["found"])
        self.assertEqual(result["results"], [])

    def test_knowledge_search_does_not_match_substrings_inside_words(self):
        result = search_knowledge_base("how to order ice cream")
        self.assertTrue(result["ok"])
        self.assertFalse(result["found"])
        self.assertEqual(result["results"], [])

    def test_knowledge_search_ignores_common_query_filler(self):
        result = search_knowledge_base("help me with steps to reserve an office desk at 5th floor")
        self.assertTrue(result["ok"])
        self.assertFalse(result["found"])
        self.assertEqual(result["results"], [])

    def test_knowledge_search_rejects_short_only_query(self):
        result = search_knowledge_base("a")
        self.assertFalse(result["found"])
        self.assertEqual(result["results"], [])

    def test_knowledge_search_matches_any_term_and_limits_results(self):
        result = search_knowledge_base("email outage mail client troubleshooting")
        self.assertTrue(result["found"])
        self.assertLessEqual(len(result["results"]), 3)
        self.assertEqual(result["results"][0]["article_id"], "KB-003")

    def test_ticket_lookup_supports_id_and_issue_text(self):
        by_id = lookup_ticket("TKT-1001", "EMP1024")
        by_issue = lookup_ticket(None, "EMP1024", "VPN disconnects")
        self.assertEqual(by_id["ticket"]["status"], "in_progress")
        self.assertEqual(by_issue["ticket"]["ticket_id"], "TKT-1001")

    def test_ticket_lookup_matches_paraphrased_issue_text(self):
        result = lookup_ticket(None, "EMP1024", "my VPN problem")
        self.assertTrue(result["found"])
        self.assertEqual(result["ticket"]["ticket_id"], "TKT-1001")

    def test_ticket_lookup_id_takes_precedence_over_issue_text(self):
        result = lookup_ticket("TKT-1001", "EMP1024", "email delays")
        self.assertTrue(result["found"])
        self.assertEqual(result["ticket"]["ticket_id"], "TKT-1001")

    def test_ticket_lookup_returns_missing_ticket(self):
        result = lookup_ticket("TKT-9999", "EMP1024")
        self.assertTrue(result["ok"])
        self.assertFalse(result["found"])
        self.assertEqual(result["ticket_id"], "TKT-9999")

    def test_ticket_lookup_requires_id_or_issue(self):
        result = lookup_ticket(employee_id="EMP1024")
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "A ticket ID or issue description is required.")

    def test_ticket_lookup_returns_resolved_ticket(self):
        result = lookup_ticket(None, "EMP3072", "Email messages are delayed")
        self.assertTrue(result["found"])
        self.assertEqual(result["ticket"]["status"], "resolved")

    def test_ticket_creation_rejects_duplicates(self):
        first = create_ticket("EMP3072", "Wi-Fi cannot connect", "network", "high")
        second = create_ticket("EMP3072", "Wi-Fi cannot connect", "network", "high")
        self.assertTrue(first["created"])
        self.assertTrue(second["duplicate"])
        self.assertEqual(first["ticket_id"], second["ticket_id"])

    def test_ticket_creation_rejects_case_insensitive_duplicate(self):
        first = create_ticket("EMP3072", "Wi-Fi cannot connect", "network", "high")
        second = create_ticket("EMP3072", " WI-FI CANNOT CONNECT ", "network", "high")
        self.assertTrue(first["created"])
        self.assertTrue(second["duplicate"])
        self.assertEqual(second["ticket_id"], first["ticket_id"])

    def test_ticket_creation_accepts_optional_details(self):
        result = create_ticket(
            "EMP2048",
            "Replacement laptop will not start",
            "hardware",
            "critical",
        )
        self.assertTrue(result["created"])
        self.assertEqual(result["status"], "open")

    def test_ticket_creation_rejects_missing_fields(self):
        missing_employee = create_ticket("", "Printer failure")
        blank_issue = create_ticket("EMP1024", "   ")
        self.assertFalse(missing_employee["created"])
        self.assertFalse(blank_issue["created"])
        self.assertIn("required", missing_employee["error"])
        self.assertIn("required", blank_issue["error"])

    def test_ticket_creation_rejects_invalid_priority(self):
        result = create_ticket("EMP1024", "VPN disconnects", priority="urgent")
        self.assertFalse(result["created"])
        self.assertEqual(
            result["error"],
            "Priority must be low, medium, high, or critical.",
        )

    def test_ticket_creation_validates_employee(self):
        result = create_ticket("UNKNOWN", "Printer failure")
        self.assertFalse(result["created"])
        self.assertIn("not found", result["error"])

    def test_ticket_creation_allows_same_issue_after_resolved_ticket(self):
        result = create_ticket("EMP3072", "Email messages are delayed", "email", "medium")
        self.assertTrue(result["created"])
        self.assertEqual(result["status"], "open")


if __name__ == "__main__":
    unittest.main()
