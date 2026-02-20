import datetime

class AuditLogger:
    def __init__(self):
        self.long_term_file_path = "logs/long_term.txt"
        self.short_term_file_path = "logs/short_term.txt"

    def log_audit_term(self, message: str):
        with open(self.long_term_file_path, 'a') as f:
            f.write(f"[{datetime.datetime.now()}] {message}\n")

    def log_short_term(self, message: str):
        with open(self.short_term_file_path, 'a') as f:
            f.write(f"[{datetime.datetime.now()}] {message}\n")
