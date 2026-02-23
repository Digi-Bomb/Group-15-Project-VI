import datetime

class AuditLogger:
    def __init__(self):
        self.file_path = "logs/audit_events.txt"

    def log_audit_event(self, title: str, message: str=""):
        with open(self.file_path, 'a') as f:
            f.write(f"[{datetime.datetime.now()}] {title}: {message}\n")
