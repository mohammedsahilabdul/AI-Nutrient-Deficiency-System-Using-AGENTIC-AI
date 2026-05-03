import random

def book_nearest():
    doctors = [
        {"doctor": "Dr. Sharma", "hospital": "City Care Hospital"},
        {"doctor": "Dr. Mehta", "hospital": "Apollo Clinic"},
        {"doctor": "Dr. Reddy", "hospital": "HealthPlus Center"}
    ]

    selected = random.choice(doctors)

    return {
        "doctor": selected["doctor"],
        "hospital": selected["hospital"],
        "time": "Tomorrow 10:00 AM"
    }