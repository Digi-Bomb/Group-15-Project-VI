class Room:
    def __init__(self, room_id: int, room_name: str, wing_number: int, max_capacity: int, has_wheelchair_access: bool, has_projector: bool, has_whiteboard: bool):
        self.room_id = room_id
        self.room_name = room_name
        self.wing_number = wing_number
        self.max_capacity = max_capacity
        self.has_wheelchair_access = has_wheelchair_access
        self.has_projector = has_projector
        self.has_whiteboard = has_whiteboard
