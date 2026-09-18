# Sample Output Summary

This folder contains representative outputs for the IT support assistant workflow.

## Included examples
- Knowledge search result for VPN password reset
- Existing ticket lookup by ID
- New ticket creation and duplicate prevention result

The detailed JSON artifacts are in `output/sample_results/`.

## Expected behavior
- Knowledge base search returns relevant article matches from SQLite.
- Ticket lookup can find a ticket by ID or issue summary.
- Ticket creation validates employee identity and prevents duplicate open tickets.
- Missing required fields are validated before tool execution.
- Unsupported requests return a safe capability response without a tool call.
- Tool failures are surfaced as user-facing recovery messages.
- Issue lookup supports employee-scoped paraphrased descriptions.

## Verification

The project regression suite covers all three LangGraph tool paths, multi-turn
clarification, deterministic validation, unsupported intents, tool failures,
search boundaries, ticket lookup, and duplicate prevention.

Latest result:

```text
Ran 41 tests
OK
```

## Submission note
These artifacts are included as packaged sample outputs alongside the project code and documentation.
