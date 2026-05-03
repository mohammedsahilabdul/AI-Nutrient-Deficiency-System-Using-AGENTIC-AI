def get_knowledge(label):
    knowledge = {
        "abnormal": {
            "symptoms": ["fissures", "marks", "discoloration"],
            "possible_deficiency": "Vitamin B / Iron deficiency"
        },
        "healthy": {
            "symptoms": ["normal texture", "pink color"],
            "possible_deficiency": "None"
        }
    }
    return knowledge.get(label, {})