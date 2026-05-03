# Launch Vehicle PCB Defect App

This module is a full-stack starter for circuit-board defect analysis:

- Backend: FastAPI (`/api/analyze`, `/health`)
- Frontend: upload UI with bounding-box overlay
- Inference mode:
  - Optional LLM mode (if `OPENAI_API_KEY` is set)
  - Safe heuristic fallback mode (works offline)

## 1) Install dependencies

From the root project, make sure these are installed:

- `fastapi`
- `uvicorn[standard]`
- `python-multipart`
- `pillow`

Optional for LLM mode:

- `openai`

## 2) Run backend + frontend

```bash
cd "launch_vehicle_defect_app"
python -m uvicorn backend.main:app --reload --port 8010
```

Open: `http://localhost:8010`

## 3) API usage

`POST /api/analyze` with multipart form-data field:

- `image`: image file

Response contains:

- defect class
- confidence
- bounding box (`x, y, width, height`)
- severity
- explanation

## 4) Production model integration

Replace the logic inside `backend/defect_service.py`:

- `_call_llm_for_defect_predictions` for LLM vision reasoning, or
- add your trained detector model (YOLO/Detectron/custom CNN) and map outputs into `DefectPrediction`.

The frontend and API contract remain unchanged.
