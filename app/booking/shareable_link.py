import uuid

class ShareableLink:
    def __init__(self, booking_id: int):
        self.link_id = self.generate_link_id()
        self.booking_id = booking_id
        
    def generate_link_id(self) -> str:
        return str(uuid.uuid4())
