class Room:
    _id_counter = 1

    def __init__(self, name: str, capacity: int, available: bool = True, absences=None):
        self.id = Room._id_counter
        Room._id_counter += 1
        self.name = name
        self.capacity = capacity
        self.available = available
        # Словарь отсутствий: ключ – день, значение – список номеров пар, когда аудитория недоступна
        self.absences = absences if absences is not None else {}

    def __str__(self):
        status = "Доступна" if self.available else "Недоступна"
        return f"Аудитория {self.id}: {self.name} (вместимость: {self.capacity}, {status})"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "capacity": self.capacity,
            "available": self.available,
            "absences": self.absences
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(data["name"], data["capacity"], data.get("available", True), data.get("absences", {}))
        obj.id = data["id"]
        if data["id"] >= cls._id_counter:
            cls._id_counter = data["id"] + 1
        return obj
