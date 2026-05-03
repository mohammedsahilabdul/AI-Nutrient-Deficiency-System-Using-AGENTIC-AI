import os
import uuid
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .defect_service import analyze_image
from .schemas import AnalyzeResponse


BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
FRONTEND_DIR = BASE_DIR / "frontend"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Launch Vehicle PCB Defect API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "launch-vehicle-pcb-defect-api"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_defect(image: UploadFile = File(...)):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload a valid image file.")

    extension = os.path.splitext(image.filename or "")[1] or ".jpg"
    file_name = f"{uuid.uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / file_name

    contents = await image.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    predictions, image_meta, model_used = analyze_image(str(file_path))
    return AnalyzeResponse(
        status="success",
        file_name=image.filename or file_name,
        image_size=image_meta,
        predictions=predictions,
        model_used=model_used,
    )


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
