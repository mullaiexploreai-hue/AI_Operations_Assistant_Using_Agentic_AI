# AI Operations Assistant - Technical Documentation

## Problem

Employees need a single assistant for IT guidance, existing ticket status, and new support requests. The assistant must use local data, retain context across turns, validate actions, and avoid inventing ticket information.

## Architecture

```text
Employee message
	|
	v
Information gathering node -- missing details --> Clarifying question
	|
	v
Compaction and structured extraction (Pydantic)
	|
	v
Conditional intent routing
	 /          |           \\
	v           v            v
Knowledge   Ticket       Ticket
search      lookup       creation
	 \          |           /
		v         v          v
	 Tool result and trace
		    |
		    v
	    Final response
		    |
		    v
	    Streamlit chat UI
```

The workflow is implemented as a LangGraph state machine. LiteLLM extracts structured request facts, the graph selects one local tool, and the final response is grounded in the tool result. Reusable validation, search, status, and extraction policies are centralized in `config.py`.

After structured extraction, a deterministic validation node checks the
required fields for the selected intent before routing to a tool. This keeps
validation independent from the LLM and prevents incomplete or unsupported
actions from executing.

## Workflow

`User message -> information gathering -> structured extraction -> conditional intent routing -> local tool -> final response`


## State

`pipeline/state.py` defines the request intent, active request, clarification state, employee ID, ticket ID, issue summary, category, priority, missing fields, conversation history, selected tool, tool calls, and tool result. `session/session_store.py` keeps sessions in memory so multiple Streamlit reruns can continue the same conversation. A clarification reply preserves the active request; a new request replaces it.

## Data and tools

`db/schema.sql` defines employees, knowledge articles, and support tickets. `db/seed_data.sql` supplies reproducible sample records. Read-only tools use SQLite read-only connections. Ticket creation uses a write connection only after validating the employee, priority, and duplicate status. Knowledge search uses generic token overlap and prefix matching; issue lookup ranks matching tokens and scopes candidates by employee when supplied.

## Sample outputs

The packaged examples are under `output/sample_results/`:

- `knowledge_search_example.json` shows the VPN knowledge search and KB-001 response.
- `ticket_lookup_example.json` shows the TKT-1001 status lookup and response.
- `ticket_creation_example.json` shows successful creation followed by duplicate prevention.
- `submission_summary.md` records the real-run coverage and current 41-test verification.

`output/submission_summary.md` is a top-level copy for evaluator convenience.

## Demonstration scenarios

The replayable positive, negative, and boundary scenarios are documented in
[output/conversation.md](../output/conversation.md). The file is a manual
demonstration guide and is not imported by the application. Automated checks
for the same workflows are maintained under `tests/`.

## Safety decisions

- Missing required information produces a clarification instead of a tool call.
- Ticket lookup can be scoped to an employee ID.
- Ticket creation rejects unknown employees and invalid priorities.
- An identical open or in-progress ticket is not created twice.
- The final response is built from the tool result, not fabricated ticket data.
- Unsupported intents return a safe capability message without executing a tool.
- Tool errors are preserved in state and converted into a user-facing recovery message.

## Limitations

This is a local teaching POC. Sessions are not durable, knowledge search is keyword-based, authentication is not implemented, and the LLM call has no retry or fallback policy.

The regression suite contains 41 tests covering direct tools, LangGraph
end-to-end paths, clarification state, deterministic validation, unsupported
requests, tool failures, duplicate handling, and search/lookup boundaries.

## Run sequence

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m db.init_db
streamlit run streamlit_app.py
```

Set `OPENAI_API_KEY` in `.env` before using the LLM-backed workflow.
