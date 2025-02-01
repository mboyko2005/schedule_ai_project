class Teacher:
    _id_counter = 1

    def __init__(self, name: str, available: bool = True, assignments=None, absences=None, preferred_rooms=None):
        self.id = Teacher._id_counter
        Teacher._id_counter += 1
        self.name = name
        self.available = available
        # Список назначений – список словарей, например: {"subject": "Математика", "group_id": 2, "time": "10:00"}
        self.assignments = assignments if assignments is not None else []
        # Словарь отсутствий: ключ – день (например, "Понедельник"), значение – список номеров пар
        self.absences = absences if absences is not None else {}
        # Список предпочтительных кабинетов (идентификаторы кабинетов)
        self.preferred_rooms = preferred_rooms if preferred_rooms is not None else []

    def __str__(self):
        status = "Доступен" if self.available else "Недоступен"
        assign_info = f", назначено групп: {len(self.assignments)}" if self.assignments else ""
        return f"Преподаватель {self.id}: {self.name} ({status}{assign_info})"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "available": self.available,
            "assignments": self.assignments,
            "absences": self.absences,
            "preferred_rooms": self.preferred_rooms
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(
            data["name"],
            data.get("available", True),
            data.get("assignments", []),
            data.get("absences", {}),
            data.get("preferred_rooms", [])
        )
        obj.id = data["id"]
        if data["id"] >= cls._id_counter:
            cls._id_counter = data["id"] + 1
        return obj
