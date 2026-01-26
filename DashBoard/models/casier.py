class Casier:
    def __init__(self, id, location, status):
        self.id = id
        self.location = location
        self.status = status

    def __repr__(self):
        return f"<Casier {self.id} - Location: {self.location}, Status: {self.status}>"

    def is_available(self):
        return self.status == 'available'

    def rent(self):
        if self.is_available():
            self.status = 'rented'
            return True
        return False

    def return_locker(self):
        self.status = 'available'