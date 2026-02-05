class Room:
    def __init__(self, room_id: int, roomName: str, wingNumber: int, max_capacity: int, has_wheelchair_access: bool, has_projector: bool, has_whiteboard: bool):
        self.room_id = room_id
        self.roomName = roomName
        self.wingNumber = wingNumber
        self.max_capacity = max_capacity
        self.has_wheelchair_access = has_wheelchair_access
        self.has_projector = has_projector
        self.has_whiteboard = has_whiteboard