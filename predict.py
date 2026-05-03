import cv2
import numpy as np
from tensorflow.keras.models import load_model
from llm_agent import get_response
from knowledge_base import get_knowledge
from hospital import book_nearest
from calendar_tool import add_to_calendar

model = load_model("models/nutrient_model.h5")

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

classes = ["abnormal", "healthy"]

def run_pipeline(img_path):

    img = cv2.imread(img_path)

    if img is None:
        return "❌ Error loading image"

    img = cv2.resize(img, (224,224)) / 255.0
    img = np.expand_dims(img, axis=0)

    pred = model.predict(img)[0]
    idx = np.argmax(pred)

    label = classes[idx]
    confidence = float(pred[idx])

    if confidence < 0.6:
        return "⚠️ Low confidence. Try again."

    knowledge = get_knowledge(label)

    explanation = get_response(label, confidence, knowledge)

    report = f"""
===============================
 AI MEDICAL REPORT
===============================

Diagnosis: {label.upper()}
Confidence: {confidence:.2f}

--------------------------------
{explanation}
"""

    if label == "abnormal":
        hospital_info = book_nearest()
        calendar_msg = add_to_calendar(hospital_info)

        report += f"""

🚨 ACTION REQUIRED

Doctor: {hospital_info['doctor']}
Hospital: {hospital_info['hospital']}
Time: {hospital_info['time']}

{calendar_msg}
"""

    else:
        report += """

✅ STATUS: HEALTHY
Maintain balanced diet and regular checkups.
"""

    return report