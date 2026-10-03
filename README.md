# AI Operations Assistant

Capstone Project 3: An agentic IT support assistant for a fictional organization. The assistant understands an employee request, selects one local tool, executes it through a LangGraph workflow, and returns a grounded response.

## Architecture

```mermaid
flowchart TD
    U[Employee message] --> G[Info gathering node]
    G --> X[Structured extraction]
    X --> V[Deterministic validation]
    V -->|Missing fields| C[Clarifying question]
    V -->|Valid| R[Intent routing]
    R --> K[Knowledge search]
    R --> L[Ticket lookup]
    R --> N[Ticket creation]
    K --> F[Final response]
    L --> F
    N --> F
```

The graph state carries conversation history, structured request facts, selected tool, tool calls, and the tool result. Only the structured facts are passed downstream after compaction. LiteLLM native function calling extracts the structured request before LangGraph routes it to the local tool.

### Workflow Components

1. **Receive a message and preserve state**
    - `views/customer_chat.py:render()` displays the chat history and sends a submitted message to the workflow.
    - `pipeline/graph.py:run_customer_turn()` loads the session, updates the active request, appends the user turn, invokes LangGraph, and saves the resulting state.
    - `session/session_store.py:get_or_create_session()` and `save_session()` retain sessions in memory. `pipeline/state.py:SessionState` defines the graph state, while `new_session_state()` initializes it.

2. **Extract intent and request fields**
    - `pipeline/info_gathering.py:run()` passes the turn through; it deliberately does not make a second LLM completeness decision.
    - `pipeline/compaction.py:run()` builds the transcript and requests structured extraction. `_request_issue()`, `_explicit_priority()`, and `_quoted_query()` normalize key values from the active request.
    - `llm/client.py:complete_support_request()` calls LiteLLM's function-calling interface. Its `REQUEST_TOOL` schema defines the extraction payload.
    - `pipeline/state.py:CompactedTicketInfo` holds the extracted fields; `RequestIntent` defines the four routing outcomes.

3. **Validate before acting**
    - `pipeline/graph.py:_validate_request()` checks the employee ID, issue/ticket reference, knowledge query, and ticket priority required for the selected intent.
    - Missing fields set `awaiting_clarification` and add a prompt to the conversation. `_route_after_validation()` then ends the graph before any tool can run.

4. **Select and execute a tool**
    - `pipeline/graph.py:_select_tool()` stores the selected intent, and `_build_graph()` defines the conditional edges.
    - `_knowledge_search_node()`, `_ticket_lookup_node()`, and `_ticket_creation_node()` call the corresponding functions in `tools/support_tools.py` and record arguments and results in state.
    - `tools/support_tools.py:search_knowledge_base()`, `lookup_ticket()`, and `create_ticket()` perform the SQLite operations. `db/connection.py` manages read-only and write connections; `db/schema.sql` and `db/seed_data.sql` define and populate the local data.

5. **Build the final response**
    - `pipeline/graph.py:_final_response_node()` converts the tool result into a user-facing reply, including no-match, duplicate, and error outcomes. Unsupported intent uses a safe capability response and does not call a tool.
    - The updated history is saved by `run_customer_turn()` and rendered on the next Streamlit rerun by `views/customer_chat.py:render()`.

Shared policies such as priorities, ticket statuses, search limits, defaults,
and extraction patterns are centralized in `config.py` for reuse.

## Technology Stack

| Area | Technology | How it is used |
|---|---|---|
| Language and runtime | Python 3.11+ | Implements the application, tools, and tests. |
| User interface | Streamlit | Provides the chat interface, session controls, and teaching views for extracted data and tool traces. |
| Workflow orchestration | LangGraph | Models the assistant as stateful nodes, edges, and conditional routes. |
| LLM integration | LiteLLM | Calls the configured model and uses function calling to extract a structured support request. The default model is `gpt-4o-mini`; the provider must be configured with credentials. |
| Structured data | Pydantic | Defines and validates `CompactedTicketInfo`, the structured request passed through the graph. |
| Local persistence | SQLite (`sqlite3`) | Stores sample employees, knowledge articles, and support tickets without requiring external infrastructure. |
| Configuration | `python-dotenv` and environment variables | Loads local settings such as `OPENAI_API_KEY`, `LLM_MODEL`, `DB_PATH`, and logging configuration. |
| Testing | `unittest` and `unittest.mock` | Tests the tools and graph paths, mocking LLM extraction so the regression suite does not make API calls. |

The project uses keyword/token matching for local knowledge retrieval; it does
not currently use embeddings, a vector database, LangChain, or a separate
reranker. Its main GenAI concepts are structured function calling, intent
extraction, tool use, stateful orchestration, deterministic validation, and
tool-grounded responses.

## Tools

1. `search_knowledge_base`: searches local IT articles in SQLite.
2. `lookup_ticket`: retrieves an existing ticket by ID or by employee plus issue description.
3. `create_ticket`: validates the employee, prevents an identical open duplicate, and creates a new ticket.

## Setup

Requires Python 3.11+.

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m db.init_db
streamlit run streamlit_app.py
```

Set `OPENAI_API_KEY` in `.env`. `LLM_MODEL` defaults to `gpt-4o-mini`; LiteLLM can target another compatible provider. `DB_PATH` defaults to `data/support.db`.

The Streamlit workflow uses the configured LLM for structured request
extraction. The bundled tool and graph tests do not require an API key and
provide a quick installation check before starting Streamlit.

## Sample output artifacts

A packaged sample-output bundle is included in `output/sample_results/` for
review and submission. It contains:

- `knowledge_search_example.json`: real-run KB-001 response and tool result
- `ticket_lookup_example.json`: real-run TKT-1001 lookup and response
- `ticket_creation_example.json`: real-run creation plus duplicate prevention
- `submission_summary.md`: artifact description and 41-test verification

The top-level `output/submission_summary.md` provides the same submission
summary for evaluators browsing the output folder.

The runnable sample input data is in `db/seed_data.sql` and contains employees,
knowledge articles, and existing tickets. The database is created automatically
on first use; run `python -m db.init_db` when you want to reset it to the
packaged sample state.

## Sample requests

The complete replayable scenario catalogue is documented in
[output/conversation.md](output/conversation.md). It covers positive,
negative, and boundary cases for knowledge search, ticket lookup, and ticket
creation. These are demonstration conversations; automated regression tests
are under `tests/`.

- `How do I reset my VPN password?`
- `I am EMP1024. What is the status of ticket TKT-1001?`
- `I am EMP1024. What is the status of my VPN issue?`
- `I am EMP3072 and my laptop will not connect to Wi-Fi. Please create a ticket.`

Example outputs:

- Knowledge search returns the `KB-001` VPN reset article and its source.
- Issue-based lookup returns `TKT-1001` with `in_progress` status.
- Ticket creation returns a generated `TKT-XXXXXXXX` ID; repeating the same request reports the existing duplicate instead of creating another ticket.

The Streamlit sidebar exposes the session ID, a new-session action, structured extraction, and the tool-call trace for demonstration.

## Project structure

- `pipeline/`: LangGraph state, prompts, routing, and tool orchestration
- `tools/`: the three SQLite-backed IT support tools (`support_tools.py`)
- `db/`: SQLite schema, seed data, and connection helpers
- `session/`: in-memory multi-turn conversation state
- `views/`: Streamlit chat UI
- `llm/`: LiteLLM JSON response wrapper

## Error handling and safety

The assistant asks for missing employee IDs or issue details before acting. Ticket creation rejects unknown employees, invalid priorities, and identical open duplicates. Tool results are recorded and final responses distinguish missing data, existing tickets, newly created tickets, and temporary tool failures. LLM, database, and graph exceptions are logged and converted into user-facing recovery messages. The local database is sample data for a POC and is not production persistence or access control.

## Tests

Run the local regression checks with:

```powershell
python -m unittest discover -s tests -v
```

This command runs without `OPENAI_API_KEY` because it exercises local tools
and mocks only structured extraction. The latest run completed 41 tests
successfully. The interactive application requires a valid key in `.env`.

## Limitations

Session state is in memory and is lost when the process restarts. Knowledge search uses SQLite keyword matching rather than embeddings. A production system would add authentication, durable storage, audit logging, retries, and stronger search/reranking.
