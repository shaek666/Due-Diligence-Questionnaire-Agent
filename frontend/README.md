Frontend Implementation (Retro Console UI)

Purpose
This folder holds the frontend implementation for the Questionnaire Agent.
It uses a Vite + React setup with Zustand state management and a retro-inspired
layout.

Screens
- Project List: view all projects and their status
- Project Detail: sections, questions, and answers with review actions
- Question Review: approve/reject/manual edit with citations and confidence
- Document Management: upload, scope, and indexing status
- Evaluation Report: compare AI vs human answers with similarity scores
- Request Status: async task tracking and error details

Modules
- src/pages/       Page-level containers
- src/components/  Reusable UI components
- src/services/    API clients and request helpers
- src/state/       Client state management
- src/utils/       CSV/Excel export helpers

Configuration
- VITE_API_URL: base URL for the FastAPI service (default: http://localhost:8000)

Run
- npm install
- npm run dev
