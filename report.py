def generate_report(label, confidence, explanation):
    return f"""
===============================
 AI MEDICAL REPORT
===============================

Diagnosis: {label.upper()}
Confidence: {confidence:.2f}

--------------------------------
AI Explanation:
{explanation}

--------------------------------
Recommendation:
{'Consult doctor immediately' if label=='abnormal' else 'Maintain healthy lifestyle'}

===============================
"""