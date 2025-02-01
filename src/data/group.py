class Group:
    _id_counter = 1

    def __init__(self, name: str):
        self.id = Group._id_counter
        Group._id_counter += 1
        self.name = name

    def __str__(self):
        return f"{self.name}"

    def to_dict(self):
        return {"id": self.id, "name": self.name}

    @classmethod
    def from_dict(cls, data):
        obj = cls(data["name"])
        obj.id = data["id"]
        if data["id"] >= cls._id_counter:
            cls._id_counter = data["id"] + 1
        return obj
