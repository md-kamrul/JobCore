# Project

This folder contains the production code for JobCore.

## Modules

- Frontend: ./Frontend
- Backend: ./Backend

## Run Order

1. Start backend services needed for your workflow:
   - Job Agent (5001)
   - Resume Checker (5004)
   - Mock Interview (5002, required for the text interview page)
2. Start frontend Vite app (5173)
3. Open browser and use feature pages.

## Detailed Docs

- Frontend guide: ./Frontend/README.md
- Backend guide: ./Backend/README.md
- Job Agent API integration: ./Backend/jobAgent/jobFinderAgent/API_INTEGRATION.md
