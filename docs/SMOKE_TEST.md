# Smoke Test Script (Manual)

1) Start services
- docker compose up --build
- Open http://localhost:5173

2) Upload documents
- In Document Management, upload all PDFs in `data/`.
- Confirm request IDs appear.

3) Create project
- Use questionnaire `data/ILPA_Due_Diligence_Questionnaire_v1.2.pdf`
- Scope: [] for ALL_DOCS

4) Generate answers
- Use Project Detail -> Generate All Answers
- Confirm citations and confidence.

5) Review and evaluate
- Update a few answers manually.
- Run evaluation and export CSV/Excel.

6) Validate OUTDATED
- Upload a new document after indexing.
- Confirm ALL_DOCS project becomes OUTDATED.
