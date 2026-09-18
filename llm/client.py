"""Centralized LiteLLM calls and structured error handling."""
import json
from typing import Any

import litellm

from config import LOGGER, LLM_MODEL


class LLMClientError(RuntimeError):
    """Raised when the configured model cannot produce a usable response."""


REQUEST_TOOL = {
    "type": "function",
    "function": {
        "name": "extract_support_request",
        "description": "Extract the structured facts needed to route an IT support request.",
        "parameters": {
            "type": "object",
            "properties": {
                "issue_summary": {"type": "string"},
                "intent": {
                    "type": "string",
                    "enum": ["knowledge_search", "ticket_lookup", "ticket_creation", "other"],
                },
                "employee_id": {"type": ["string", "null"]},
                "ticket_id": {"type": ["string", "null"]},
                "category": {"type": ["string", "null"]},
                "priority": {"type": "string"},
                "info_complete": {"type": "boolean"},
                "missing_fields": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "issue_summary",
                "intent",
                "employee_id",
                "ticket_id",
                "category",
                "priority",
                "info_complete",
                "missing_fields",
            ],
        },
    },
}


def _message_content(response: Any) -> str:
    message = response.choices[0].message
    content = getattr(message, "content", None)
    if not content:
        raise LLMClientError("The model returned an empty response.")
    return content


def complete_json(system_prompt: str, user_content: str, temperature: float = 0.0) -> dict:
    """Call the model in JSON mode for the clarification step."""
    try:
        response = litellm.completion(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        return json.loads(_message_content(response))
    except (json.JSONDecodeError, LLMClientError) as exc:
        LOGGER.exception("Invalid LLM response")
        raise LLMClientError("The model returned an invalid response.") from exc
    except Exception as exc:
        LOGGER.exception("LLM request failed")
        raise LLMClientError("The AI service is temporarily unavailable.") from exc


def complete_support_request(system_prompt: str, user_content: str) -> dict:
    """Use native function calling to extract the request-routing payload."""
    try:
        response = litellm.completion(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            tools=[REQUEST_TOOL],
            tool_choice={"type": "function", "function": {"name": "extract_support_request"}},
            temperature=0.0,
        )
        tool_calls = getattr(response.choices[0].message, "tool_calls", None) or []
        if not tool_calls:
            raise LLMClientError("The model did not call the request extraction function.")
        arguments = tool_calls[0].function.arguments
        return json.loads(arguments)
    except (json.JSONDecodeError, LLMClientError) as exc:
        LOGGER.exception("Invalid structured tool call")
        raise LLMClientError("The AI service returned an invalid structured request.") from exc
    except Exception as exc:
        LOGGER.exception("Structured LLM request failed")
        raise LLMClientError("The AI service is temporarily unavailable.") from exc
