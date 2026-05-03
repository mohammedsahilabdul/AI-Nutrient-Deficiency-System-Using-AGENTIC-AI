import json
import os
from datetime import datetime

LOG_FILE = "logs/conversations.json"
os.makedirs("logs", exist_ok=True)

def save_conversation(user_input, response):
    data = {
        "time": str(datetime.now()),
        "user": user_input,
        "agent": response
    }

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)

    with open(LOG_FILE, "r+") as f:
        logs = json.load(f)
        logs.append(data)
        f.seek(0)
        json.dump(logs, f, indent=4)