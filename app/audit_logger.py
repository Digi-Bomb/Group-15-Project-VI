class AuditLogger:
    def __init__(self,long_term_file_path: str, short_term_file_path: str):
        self.long_term_file_path = long_term_file_path
        self.short_term_file_path = short_term_file_path
