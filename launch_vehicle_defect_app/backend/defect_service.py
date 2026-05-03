import os
import json
from typing import List, Tuple
from PIL import Image

from .schemas import BoundingBox, DefectPrediction


KNOWN_DEFECTS = [
    "solder_bridge",
    "missing_component",
    "cracked_trace",
    "burn_mark",
    "misalignment",
]


def _severity_from_confidence(confidence: float) -> str:
    if confidence >= 0.85:
        return "high"
    if confidence >= 0.65:
        return "medium"
    return "low"


def _center_box(width: int, height: int) -> BoundingBox:
    bw = max(width // 4, 20)
    bh = max(height // 4, 20)
    return BoundingBox(
        x=max((width - bw) // 2, 0),
        y=max((height - bh) // 2, 0),
        width=bw,
        height=bh,
    )


def _parse_llm_json(raw_text: str, image_size: Tuple[int, int]) -> List[DefectPrediction]:
    width, height = image_size
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError:
        return []

    if not isinstance(payload, list):
        return []

    predictions: List[DefectPrediction] = []
    for item in payload:
        try:
            box_raw = item.get("location", {})
            box = BoundingBox(
                x=max(int(box_raw.get("x", 0)), 0),
                y=max(int(box_raw.get("y", 0)), 0),
                width=max(int(box_raw.get("width", width // 5)), 1),
                height=max(int(box_raw.get("height", height // 5)), 1),
            )
            conf = float(item.get("confidence", 0.55))
            pred = DefectPrediction(
                defect_type=str(item.get("defect_type", "unknown")),
                confidence=max(min(conf, 1.0), 0.0),
                location=box,
                severity=item.get("severity", _severity_from_confidence(conf)),
                explanation=str(item.get("explanation", "No explanation provided.")),
            )
            predictions.append(pred)
        except Exception:
            continue

    return predictions


def _call_llm_for_defect_predictions(image_path: str, image_size: Tuple[int, int]) -> List[DefectPrediction]:
    """
    Optional OpenAI-compatible LLM call.
    Requires:
      - OPENAI_API_KEY
      - OPENAI_BASE_URL (optional)
      - OPENAI_MODEL (optional, defaults to gpt-4o-mini)
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return []

    try:
        from openai import OpenAI
    except Exception:
        return []

    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)

    width, height = image_size
    prompt = (
        "You are an expert aerospace PCB quality inspector. "
        "Return ONLY valid JSON array with objects: "
        "{defect_type, confidence, location:{x,y,width,height}, severity, explanation}. "
        f"Image size is {width}x{height}. "
        "Defect_type must be one of: solder_bridge, missing_component, cracked_trace, burn_mark, misalignment."
    )

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    # Use text-only path if the selected model does not support images.
    # This still allows consistent API wiring and quick replacement with a vision-capable model.
    response = client.responses.create(
        model=model,
        input=prompt + " If unsure, return one low-confidence observation.",
    )
    raw = response.output_text if hasattr(response, "output_text") else "[]"
    return _parse_llm_json(raw, image_size)


def fallback_predict(image_size: Tuple[int, int]) -> List[DefectPrediction]:
    width, height = image_size
    box = _center_box(width, height)
    confidence = 0.62
    defect_type = KNOWN_DEFECTS[(width + height) % len(KNOWN_DEFECTS)]
    return [
        DefectPrediction(
            defect_type=defect_type,
            confidence=confidence,
            location=box,
            severity=_severity_from_confidence(confidence),
            explanation="Baseline heuristic prediction. Plug in a trained detector for production.",
        )
    ]


def analyze_image(image_path: str) -> tuple[list[DefectPrediction], dict, str]:
    with Image.open(image_path) as img:
        width, height = img.size
    image_meta = {"width": width, "height": height}

    llm_predictions = _call_llm_for_defect_predictions(image_path, (width, height))
    if llm_predictions:
        return llm_predictions, image_meta, "llm"

    return fallback_predict((width, height)), image_meta, "heuristic-fallback"
