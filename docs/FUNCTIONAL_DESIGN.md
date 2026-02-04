# Functional Design — Questionnaire Agent

## User Flows
1) Upload documents -> Index -> Track status
2) Upload questionnaire -> Parse -> Create project
3) Generate answers -> Review -> Update status
4) Run evaluation -> Inspect report
5) Optional: Chat -> Retrieve + answer with citations (read-only)

## API Behaviors
- POST /index-document-async
  - Accepts document metadata + file
  - Returns request_id
- POST /create-project-async
  - Accepts questionnaire file + scope
  - Returns project_id + request_id
- POST /generate-all-answers
  - Accepts project_id
  - Returns request_id
- POST /generate-single-answer
  - Accepts project_id + question_id
  - Returns answer with citations + confidence
- POST /update-project-async
  - Updates project scope or settings, triggers regen
- POST /update-answer
  - Manual edits or status updates
  - Emits review events for audit trail
- GET /get-project-info
  - Project summary + questions + answers
- GET /get-project-status
  - Project + last request status
- GET /get-request-status
  - Request status and error details
- GET /list-review-events
  - Review event history for a given answer
- POST /create-chat-session
  - Creates a chat session for follow-up questions
- POST /chat-message-async
  - Accepts session_id + message
  - Returns request_id + session_id
- GET /list-chat-messages
  - Returns chat history with citations and confidence

## Status Transitions
- Any indexing or answer generation request must create a Request record.
- Requests move from QUEUED -> RUNNING -> SUCCEEDED or FAILED.
- Project status changes based on request completion and indexing updates.

## Edge Cases
- Missing data: answer should be MISSING_DATA with explanation.
- No relevant citations: answer is not allowed to cite unrelated chunks.
- Questionnaire parse errors: return FAILED with error detail.
- New documents: ALL_DOCS projects become OUTDATED.
- Config changes: pipeline signature mismatch triggers auto re-index and
  regeneration in the background.
- Chat is read-only and does not mutate questionnaire answers or project state.
