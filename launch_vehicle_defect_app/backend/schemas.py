from pydantic import BaseModel, Field
from typing import List


class BoundingBox(BaseModel):
    x: int = Field(..., ge=0, description="Left coordinate in pixels")
    y: int = Field(..., ge=0, description="Top coordinate in pixels")
    width: int = Field(..., gt=0, description="Box width in pixels")
    height: int = Field(..., gt=0, description="Box height in pixels")


class DefectPrediction(BaseModel):
    defect_type: str = Field(..., description="Detected defect class")
    confidence: float = Field(..., ge=0.0, le=1.0)
    location: BoundingBox
    severity: str = Field(..., description="low | medium | high")
    explanation: str = Field(..., description="Human-readable reason for prediction")


class AnalyzeResponse(BaseModel):
    status: str
    file_name: str
    image_size: dict
    predictions: List[DefectPrediction]
    model_used: str
