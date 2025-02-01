class ScheduleEntry:
    def __init__(self, day: str, period: int, start_time: str, end_time: str, teacher, room, group, subject: str):
        self.day = day
        self.period = period
        self.start_time = start_time
        self.end_time = end_time
        self.teacher = teacher    # Объект Teacher или None
        self.room = room          # Объект Room или None
        self.group = group        # Наименование группы (строка)
        self.subject = subject

    def __str__(self):
        teacher_str = self.teacher.name if self.teacher is not None else "Не назначен"
        room_str = self.room.name if self.room is not None else "Не назначена"
        return (f"{self.day} | Пара {self.period} ({self.start_time}-{self.end_time}): {self.subject}, "
                f"Преподаватель: {teacher_str}, Аудитория: {room_str}, Группа: {self.group}")
