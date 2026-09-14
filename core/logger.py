MADE_BY = "Made by unbeau"

import json
from datetime import datetime
from core.config import LOG_DIR

def save_log(module, target, data):
    path = LOG_DIR / f"{module}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    payload = {
        "module": module,
        "target": target,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4, ensure_ascii=False, default=str)
    return path
