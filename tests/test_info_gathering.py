import unittest
from unittest.mock import patch

from pipeline.compaction import run as compact_request
from pipeline.info_gathering import run
from pipeline.state import new_session_state


class InformationGatheringTests(unittest.TestCase):
    def test_standalone_knowledge_question_does_not_request_employee_id(self):
        state = new_session_state("knowledge-search-test")
        state["conversation_history"].append(
            {"role": "user", "content": "How do I reserve a parking space?", "timestamp": "now"}
        )

        result = run(state)

        self.assertFalse(result["awaiting_clarification"])
        self.assertEqual(len(result["conversation_history"]), 1)

    def test_ticket_request_still_requires_missing_information(self):
        state = new_session_state("ticket-clarification-test")
        state["conversation_history"].append(
            {"role": "user", "content": "I need IT help.", "timestamp": "now"}
        )

        result = run(state)

        self.assertFalse(result["awaiting_clarification"])
        self.assertEqual(len(result["conversation_history"]), 1)

    def test_replacement_laptop_question_routes_to_knowledge_search(self):
        state = new_session_state("replacement-laptop-knowledge-test")
        state["conversation_history"].extend([
            {"role": "user", "content": "What do I need to request a replacement laptop?", "timestamp": "now"},
            {"role": "assistant", "content": "What is your employee ID?", "timestamp": "now"},
            {"role": "user", "content": "EMP1024", "timestamp": "now"},
            {"role": "assistant", "content": "What is the reason for the replacement laptop request?", "timestamp": "now"},
            {"role": "user", "content": "breakdown", "timestamp": "now"},
        ])
        extracted = {
            "issue_summary": "What do I need to request a replacement laptop?",
            "intent": "knowledge_search",
            "employee_id": None,
            "ticket_id": None,
            "category": "hardware",
            "priority": "medium",
            "info_complete": True,
            "missing_fields": [],
        }

        with patch("pipeline.compaction.complete_support_request", return_value=extracted):
            result = compact_request(state)

        self.assertEqual(result["compacted_info"].intent.value, "knowledge_search")
        self.assertEqual(
            result["compacted_info"].issue_summary,
            "What do I need to request a replacement laptop?",
        )

    def test_latest_knowledge_question_replaces_earlier_search_query(self):
        state = new_session_state("latest-knowledge-query-test")
        state["conversation_history"].extend([
            {"role": "user", "content": "How do I reset my VPN password?", "timestamp": "now"},
            {"role": "assistant", "content": "VPN guidance", "timestamp": "now"},
            {"role": "user", "content": "how to troubleshoot email outage", "timestamp": "now"},
        ])
        extracted = {
            "issue_summary": "how to troubleshoot email outage",
            "intent": "knowledge_search",
            "employee_id": None,
            "ticket_id": None,
            "category": None,
            "priority": "medium",
            "info_complete": True,
            "missing_fields": [],
        }

        with patch("pipeline.compaction.complete_support_request", return_value=extracted):
            result = compact_request(state)

        self.assertEqual(
            result["compacted_info"].issue_summary,
            "how to troubleshoot email outage",
        )

    def test_quoted_knowledge_query_is_extracted_without_wrapper_text(self):
        state = new_session_state("quoted-knowledge-query-test")
        state["conversation_history"].append(
            {"role": "user", "content": 'Can you search the knowledge base for "a"?', "timestamp": "now"}
        )
        extracted = {
            "issue_summary": "search the knowledge base for a",
            "intent": "knowledge_search",
            "employee_id": None,
            "ticket_id": None,
            "category": None,
            "priority": "medium",
            "info_complete": True,
            "missing_fields": [],
        }

        with patch("pipeline.compaction.complete_support_request", return_value=extracted):
            result = compact_request(state)

        self.assertEqual(result["compacted_info"].issue_summary, "a")


if __name__ == "__main__":
    unittest.main()