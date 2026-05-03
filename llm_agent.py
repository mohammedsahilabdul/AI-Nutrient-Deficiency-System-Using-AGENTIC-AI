import requests
from memory import save_conversation

def get_response(prediction, confidence, knowledge):

    prompt = f"""
You are a professional medical AI assistant.

Patient Analysis:
- Condition: {prediction}
- Confidence: {confidence:.2f}

Reference Knowledge:
Symptoms: {knowledge.get("symptoms")}
Possible Deficiency: {knowledge.get("possible_deficiency")}

Generate a structured medical report in this EXACT format:

=== MEDICAL REPORT ===

Diagnosis:
<short result>

Explanation:
<clear simple explanation>

Possible Causes:
- Cause 1
- Cause 2

Recommended Diet:
- Food 1
- Food 2

Lifestyle Advice:
- Advice 1
- Advice 2

Doctor Recommendation:
<Yes or No + reason>
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "medical-agent",  # or llama3
                "prompt": prompt,
                "stream": False
            }
        )

        result = response.json()["response"]

        save_conversation(prompt, result)

        return result

    except Exception as e:
        return f"❌ LLM Error: {str(e)}"