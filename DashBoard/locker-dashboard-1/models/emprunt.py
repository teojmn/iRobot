class Emprunt:
    def __init__(self, id, locker_id, user_id, start_time, end_time):
        self.id = id
        self.locker_id = locker_id
        self.user_id = user_id
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return f"<Emprunt {self.id} - Locker ID: {self.locker_id}, User ID: {self.user_id}>"

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            locker_id=data.get('locker_id'),
            user_id=data.get('user_id'),
            start_time=data.get('start_time'),
            end_time=data.get('end_time')
        )