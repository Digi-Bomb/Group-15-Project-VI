import datetime

class AuditLogger:
    def __init__(self, long_term_file_path: str, short_term_file_path: str):
        self.long_term_file_path = long_term_file_path
        self.short_term_file_path = short_term_file_path
        
    def log_long_term(self, message: str):
        with open(self.long_term_file_path, 'a') as f:
            f.write(f"[{datetime.datetime.now()}] {message}\n")
    
    def log_short_term(self, message: str):
        with open(self.short_term_file_path, 'a') as f:
            f.write(f"[{datetime.datetime.now()}] {message}\n")
