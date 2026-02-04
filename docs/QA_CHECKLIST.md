# QA Checklist

## Ingestion
- Upload all PDFs from `data/` and confirm each request completes.
- Verify documents appear in `/list-documents`.

## Questionnaire Parsing
- Upload `ILPA_Due_Diligence_Questionnaire_v1.2.pdf` as questionnaire input.
- Verify questions are parsed and listed in Project Detail.

## Answer Generation
- Run Generate All Answers.
- Verify each answer includes answerability, citations, and confidence.

## Review Workflow
- Manually update at least two answers.
- Confirm status updates appear in Project Detail.

## Evaluation
- Run evaluation.
- Confirm evaluation run appears in Evaluation Report with scores.

## Status
- After indexing a new document, confirm ALL_DOCS projects change to OUTDATED.
- Verify request status records update to SUCCEEDED/FAILED.
