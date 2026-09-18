import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

import db.connection as db_connection
import db.init_db as init_db
from pipeline.graph import _final_response_node, _knowledge_search_node, run_customer_turn
from pipeline.state import CompactedTicketInfo, new_session_state


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = db_connection.DB_PATH
        db_connection.DB_PATH = str(Path(self.temp_dir.name) / "support.db")
        init_db.build_database()

    def tearDown(self):
        db_connection.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    @staticmethod
    def _extracted(intent, issue_summary, employee_id=None, ticket_id=None, priority="medium"):
        return {
            "issue_summary": issue_summary,
            "intent": intent,
            "employee_id": employee_id,
            "ticket_id": ticket_id,
            "category": "general",
            "priority": priority,
            "info_complete": True,
            "missing_fields": [],
        }

    def test_end_to_end_knowledge_search(self):
        with patch(
            "pipeline.compaction.complete_support_request",
            return_value=self._extracted("knowledge_search", "How do I reset my VPN password?"),
        ):
            state = run_customer_turn(f"e2e-knowledge-{id(self)}", "How do I reset my VPN password?")

        self.assertEqual(state["selected_tool"], "knowledge_search")
        self.assertEqual(state["tool_calls"][0]["tool"], "search_knowledge_base")
        self.assertEqual(state["tool_result"]["results"][0]["article_id"], "KB-001")
        self.assertIn("Reset VPN access", state["conversation_history"][-1]["content"])

    def test_end_to_end_ticket_lookup(self):
        with patch(
            "pipeline.compaction.complete_support_request",
            return_value=self._extracted("ticket_lookup", "VPN issue", "EMP1024"),
        ):
            state = run_customer_turn(f"e2e-lookup-{id(self)}", "What is the status of my VPN issue?")

        self.assertEqual(state["selected_tool"], "ticket_lookup")
        self.assertEqual(state["tool_result"]["ticket"]["ticket_id"], "TKT-1001")
        self.assertIn("in_progress", state["conversation_history"][-1]["content"])

    def test_end_to_end_ticket_lookup_accepts_id_without_issue_summary(self):
        with patch(
            "pipeline.compaction.complete_support_request",
            return_value=self._extracted("ticket_lookup", "", "EMP1024", "TKT-1001"),
        ):
            state = run_customer_turn(f"e2e-id-only-{id(self)}", "What is the status of TKT-1001?")

        self.assertEqual(state["selected_tool"], "ticket_lookup")
        self.assertEqual(state["tool_result"]["ticket"]["ticket_id"], "TKT-1001")
        self.assertEqual(state["tool_calls"][0]["args"]["issue_summary"], "")

    def test_end_to_end_ticket_creation(self):
        with patch(
            "pipeline.compaction.complete_support_request",
            return_value=self._extracted(
                "ticket_creation", "Printer is not working", "EMP1024", priority="high"
            ),
        ):
            state = run_customer_turn(f"e2e-create-{id(self)}", "Please create a printer ticket for EMP1024.")

        self.assertEqual(state["selected_tool"], "ticket_creation")
        self.assertTrue(state["tool_result"]["created"])
        self.assertRegex(state["tool_result"]["ticket_id"], r"^TKT-[A-F0-9]{8}$")

    def test_end_to_end_clarification_then_creation(self):
        incomplete_extraction = self._extracted("ticket_creation", "VPN is not working")
        complete_extraction = self._extracted("ticket_creation", "VPN is not working", "EMP1024")
        with patch(
            "pipeline.compaction.complete_support_request",
            side_effect=[incomplete_extraction, complete_extraction],
        ):
            session_id = f"e2e-clarification-{id(self)}"
            first = run_customer_turn(session_id, "Please create a ticket for my VPN issue.")
            second = run_customer_turn(session_id, "EMP1024")

        self.assertTrue(first["awaiting_clarification"])
        self.assertTrue(second["tool_result"]["created"])
        self.assertEqual(second["active_request"], "Please create a ticket for my VPN issue.")

    def test_deterministic_validation_blocks_creation_without_employee(self):
        with patch(
            "pipeline.compaction.complete_support_request",
            return_value=self._extracted("ticket_creation", "VPN is not working"),
        ):
            state = run_customer_turn(f"validation-{id(self)}", "Create a ticket for my VPN issue.")

        self.assertTrue(state["awaiting_clarification"])
        self.assertEqual(state["tool_calls"], [])
        self.assertIn("employee ID", state["conversation_history"][-1]["content"])

    def test_extraction_missing_fields_block_tool_execution(self):
        extracted = self._extracted("ticket_lookup", "", "EMP1024")
        extracted["info_complete"] = False
        extracted["missing_fields"] = ["ticket ID or issue description"]
        with patch("pipeline.compaction.complete_support_request", return_value=extracted):
            state = run_customer_turn(
                f"validation-missing-reference-{id(self)}",
                "I am EMP1024. Can you tell me about my support ticket?",
            )

        self.assertTrue(state["awaiting_clarification"])
        self.assertEqual(state["tool_calls"], [])
        self.assertIn("ticket ID or issue description", state["conversation_history"][-1]["content"])

    def test_invalid_priority_is_rejected_before_creation(self):
        extracted = self._extracted("ticket_creation", "VPN disconnects", "EMP1024", priority="urgent")
        with patch("pipeline.compaction.complete_support_request", return_value=extracted):
            state = run_customer_turn(
                f"validation-priority-{id(self)}",
                "I am EMP1024. Create a VPN ticket with priority urgent.",
            )

        self.assertTrue(state["awaiting_clarification"])
        self.assertEqual(state["tool_calls"], [])
        self.assertIn("valid priority", state["conversation_history"][-1]["content"])

    def test_duplicate_result_has_duplicate_specific_response(self):
        state = new_session_state(f"duplicate-response-{id(self)}")
        state["selected_tool"] = "ticket_creation"
        state["compacted_info"] = CompactedTicketInfo(
            issue_summary="Wi-Fi failure",
            intent="ticket_creation",
            employee_id="EMP3072",
            info_complete=True,
        )
        state["tool_result"] = {
            "ok": True,
            "created": False,
            "duplicate": True,
            "ticket_id": "TKT-EXISTING",
            "error": "A matching open ticket already exists.",
        }

        result = _final_response_node(state)

        self.assertIn("did not create a duplicate", result["conversation_history"][-1]["content"])

    def test_unsupported_intent_returns_safe_response_without_tool_call(self):
        with patch(
            "pipeline.compaction.complete_support_request",
            return_value=self._extracted("other", "Tell me a joke"),
        ):
            state = run_customer_turn(f"unsupported-{id(self)}", "Tell me a joke")

        self.assertEqual(state["tool_calls"], [])
        self.assertIn("search IT guidance", state["conversation_history"][-1]["content"])

    def test_tool_failure_is_returned_as_user_facing_error(self):
        with patch(
            "pipeline.compaction.complete_support_request",
            return_value=self._extracted("knowledge_search", "How do I reset my VPN password?"),
        ), patch(
            "pipeline.graph.search_knowledge_base",
            return_value={"ok": False, "error": "The knowledge base is temporarily unavailable."},
        ):
            state = run_customer_turn(f"tool-failure-{id(self)}", "How do I reset my VPN password?")

        self.assertEqual(state["tool_result"]["ok"], False)
        self.assertIn("temporarily unavailable", state["conversation_history"][-1]["content"])

    def test_single_turn_knowledge_search_uses_user_message(self):
        session_id = f"graph-test-knowledge-{id(self)}"
        state = new_session_state(session_id)
        state["active_request"] = "how to order ice cream"
        state["request_continued"] = False
        state["conversation_history"].append(
            {"role": "user", "content": "how to order ice cream", "timestamp": "now"}
        )

        with patch("pipeline.graph.search_knowledge_base") as search:
            search.return_value = {"ok": True, "found": False, "results": []}
            state["compacted_info"] = CompactedTicketInfo(
                issue_summary="how to order ice cream",
                intent="knowledge_search",
                info_complete=True,
            )
            result = _knowledge_search_node(state)

        search.assert_called_once_with("how to order ice cream")
        self.assertFalse(result["tool_result"]["found"])

    def test_knowledge_search_uses_latest_user_question(self):
        session_id = f"graph-test-knowledge-followup-{id(self)}"
        state = new_session_state(session_id)
        state["active_request"] = "how to reset my VPN password"
        state["request_continued"] = True
        state["conversation_history"].append(
            {"role": "user", "content": "can you help with the steps reserve parking space", "timestamp": "now"}
        )

        with patch("pipeline.graph.search_knowledge_base") as search:
            search.return_value = {"ok": True, "found": False, "results": []}
            state["compacted_info"] = CompactedTicketInfo(
                issue_summary="reserve parking space",
                intent="knowledge_search",
                info_complete=True,
            )
            _knowledge_search_node(state)

        search.assert_called_once_with("reserve parking space")

    def test_short_knowledge_query_is_not_replaced_by_conversation_wrapper(self):
        state = new_session_state(f"graph-test-short-query-{id(self)}")
        state["conversation_history"].append(
            {"role": "user", "content": 'Can you search the knowledge base for "a"?', "timestamp": "now"}
        )
        state["compacted_info"] = CompactedTicketInfo(
            issue_summary="a",
            intent="knowledge_search",
            info_complete=True,
        )

        with patch("pipeline.graph.search_knowledge_base") as search:
            search.return_value = {"ok": True, "found": False, "results": []}
            result = _knowledge_search_node(state)

        search.assert_called_once_with("a")
        self.assertFalse(result["tool_result"]["found"])

    def test_incomplete_request_stays_in_conversation_state(self):
        session_id = f"graph-test-clarification-{id(self)}"

        with patch(
            "pipeline.compaction.complete_support_request",
            return_value=self._extracted("ticket_creation", "I need IT help."),
        ):
            state = run_customer_turn(session_id, "I need IT help.")

        self.assertTrue(state["awaiting_clarification"])
        self.assertEqual(state["turn_count"], 1)
        self.assertEqual(state["conversation_history"][-1]["role"], "assistant")
        self.assertIn("employee ID", state["conversation_history"][-1]["content"])
        self.assertEqual(state["tool_calls"], [])

    def test_legacy_session_initializes_active_request(self):
        session_id = f"graph-test-legacy-session-{id(self)}"
        legacy_state = new_session_state(session_id)
        legacy_state.pop("active_request")
        session_store_state = __import__("session.session_store", fromlist=["save_session"])
        session_store_state.save_session(session_id, legacy_state)

        with patch(
            "pipeline.compaction.complete_support_request",
            return_value=self._extracted("knowledge_search", "how to order ice cream"),
        ):
            state = run_customer_turn(session_id, "how to order ice cream")

        self.assertEqual(state["active_request"], "how to order ice cream")


if __name__ == "__main__":
    unittest.main()