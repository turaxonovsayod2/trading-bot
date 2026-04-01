import logging
import json
from datetime import datetime

class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger("security")
        handler = logging.FileHandler("logs/security.log")
        handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.logger.addHandler(handler)

    def log_event(self, event_type, severity, details, user_id=None, ip=None):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "severity": severity,
            "details": details,
            "user_id": user_id,
            "ip": ip
        }
        if severity == "CRITICAL":
            self.logger.critical(json.dumps(entry))
        elif severity == "WARNING":
            self.logger.warning(json.dumps(entry))
        else:
            self.logger.info(json.dumps(entry))
