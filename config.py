"""Central place for every knob a student might want to turn.

Nothing here is hardcoded inline elsewhere in the codebase — the LLM model
name and the database path both flow through this module so a reader only
has to look in one place to change POC-wide behavior.
"""
import os
import logging

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv() -> None:
        """Keep local database tools usable before optional setup packages install."""
        return None


# Loads OPENAI_API_KEY and other settings from a local .env when available.
load_dotenv()

logging.basicConfig(
	level=os.getenv("LOG_LEVEL", "INFO"),
	format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
LOGGER = logging.getLogger("ai_operations_assistant")

# LiteLLM model identifier, e.g. "gpt-4o-mini", "gpt-4o", "claude-sonnet-5".
# See https://docs.litellm.ai/docs/providers for the full naming scheme.
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# Path to the embedded SQLite database backing the local IT tools.
DB_PATH = os.getenv("DB_PATH", "data/support.db")

# Shared application policies. Keeping these in one module avoids repeating
# business rules across graph nodes and local tools.
DEFAULT_CATEGORY = os.getenv("DEFAULT_CATEGORY", "general")
DEFAULT_PRIORITY = os.getenv("DEFAULT_PRIORITY", "medium")
SUPPORTED_PRIORITIES = frozenset({"low", "medium", "high", "critical"})
ACTIVE_TICKET_STATUSES = ("open", "in_progress")
MIN_SEARCH_TOKEN_LENGTH = 3
MIN_MATCHED_SEARCH_TERMS = 2
MAX_KNOWLEDGE_RESULTS = 3
QUOTED_QUERY_PATTERN = r"[\"']([^\"']+)[\"']"
ISSUE_EXTRACTION_PATTERNS = (
    r"\babout\s+(.+?)(?:[?.]|$)",
    r"\bticket\s+for\s+(.+?)(?:\s+with\s+priority\b|[?.]|$)",
    r"\band\s+(?:my\s+)?(.+?)(?:,?\s+please\s+create\b|\.?\s*create\s+(?:a|an)\s+ticket\b|[?.]|$)",
)
PRIORITY_PATTERN = r"\bpriority\s+([a-zA-Z]+)"
