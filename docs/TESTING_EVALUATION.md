# Testing & Evaluation — Questionnaire Agent

## Dataset Testing Plan
- Use the provided questionnaire PDF as input.
- Use the reference PDFs as the document corpus.
- Validate parsing, indexing, and answer generation.
- Add a new document after indexing to confirm ALL_DOCS -> OUTDATED.

## QA Checklist
- Upload document -> indexing request status updates correctly.
- Questionnaire parses into ordered sections and questions.
- Answer includes: answerability statement, citations, confidence score.
- Review actions update answer status and preserve manual edits.
- Evaluation produces numeric score and explanation.

## Evaluation Metrics
- Retrieval: precision@k, recall@k, MRR
- Generation: semantic similarity and faithfulness
- Report: per-question score + overall summary
