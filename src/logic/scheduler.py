from src.data.schedule_entry import ScheduleEntry
from src.logic.validator import validate_schedule

def get_time_slots():
    MONDAY_SLOTS = [
        (0, "08:30", "09:15"),
        (1, "09:20", "10:50"),
        (2, "11:10", "12:40"),
        (3, "12:50", "14:20"),
        (4, "14:35", "16:05"),
        (5, "16:10", "17:40"),
        (6, "17:45", "19:15"),
    ]
    OTHER_DAYS_SLOTS = [
        (1, "08:30", "10:00"),
        (2, "10:10", "11:40"),
        (3, "12:00", "13:30"),
        (4, "14:00", "15:30"),
        (5, "15:40", "17:10"),
        (6, "17:15", "18:45"),
    ]
    slots = {"Понедельник": MONDAY_SLOTS}
    for day in ["Вторник", "Среда", "Четверг", "Пятница", "Суббота"]:
        slots[day] = OTHER_DAYS_SLOTS
    return slots

def generate_schedule(teachers, rooms, groups, time_slots):
    # Словарь для быстрого доступа по ID аудиторий.
    room_dict = {room.id: room for room in rooms}
    # occupancy[day][pair] – контролирует, какие преподаватели и кабинеты уже заняты в данном слоте.
    occupancy = {day: {} for day in time_slots}
    schedule = {day: [] for day in time_slots}
    # group_slots[day]: для каждой группы (по group_id) хранится список уже назначенных слотов,
    # чтобы обеспечить последовательность и не более 4 пар.
    group_slots = {day: {} for day in time_slots}

    for day, slots in time_slots.items():
        for pair, start, end in slots:
            occupancy[day][pair] = {"teachers": set(), "rooms": set()}

        # Обработка понедельника, слот 0 (ЧКР)
        if day == "Понедельник":
            for pair, start, end in slots:
                if pair == 0:
                    for group in groups:
                        chosen_room = None
                        for room in rooms:
                            if not room.available:
                                continue
                            if day in room.absences and pair in room.absences[day]:
                                continue
                            if room.id in occupancy[day][pair]["rooms"]:
                                continue
                            chosen_room = room
                            break
                        if chosen_room:
                            entry = ScheduleEntry(day, pair, start, end, None, chosen_room, group.name, "ЧКР")
                            schedule[day].append(entry)
                            occupancy[day][pair]["rooms"].add(chosen_room.id)
                            group_slots[day].setdefault(group.id, []).append(pair)
                        else:
                            entry = ScheduleEntry(day, pair, start, end, None, None, group.name, "ЧКР (Дистанционно)")
                            schedule[day].append(entry)
                            group_slots[day].setdefault(group.id, []).append(pair)
        # Обработка остальных слотов (исключая понедельник, слот 0)
        for teacher in teachers:
            if not teacher.available:
                continue
            for assignment in teacher.assignments:
                group_id = assignment.get("group_id")
                # Получаем наименование группы по ID (если не найден, оставляем строку с ID)
                group_name = next((g.name for g in groups if g.id == group_id), f"Группа {group_id}")
                # Если для группы уже назначено 4 пары, пропускаем.
                if group_id in group_slots[day] and len(group_slots[day][group_id]) >= 4:
                    continue
                slots_sorted = sorted(slots, key=lambda x: x[0])
                scheduled = False
                # Если для группы уже есть назначенные слоты, следующий должен быть ровно last + 1.
                desired_slot = None
                if group_id in group_slots[day]:
                    desired_slot = max(group_slots[day][group_id]) + 1

                # Создаём список доступных слотов (исключая слоты, где преподаватель отсутствует)
                available_slots = [ (pair, start, end) for pair, start, end in slots_sorted
                                    if not (day == "Понедельник" and pair == 0)
                                    and pair not in teacher.absences.get(day, []) ]

                # Если желаемый слот задан, ищем именно его.
                if desired_slot is not None:
                    candidate_slots = [s for s in available_slots if s[0] == desired_slot]
                    if candidate_slots:
                        pair, start, end = candidate_slots[0]
                        chosen_room = None
                        # Подбор кабинета: сначала по предпочтениям
                        if teacher.preferred_rooms:
                            for room_id in teacher.preferred_rooms:
                                if room_id not in room_dict:
                                    continue
                                room = room_dict[room_id]
                                if day in room.absences and pair in room.absences[day]:
                                    continue
                                if room.id in occupancy[day][pair]["rooms"]:
                                    continue
                                chosen_room = room
                                break
                        if not chosen_room:
                            for room in rooms:
                                if not room.available:
                                    continue
                                if day in room.absences and pair in room.absences[day]:
                                    continue
                                if room.id in occupancy[day][pair]["rooms"]:
                                    continue
                                chosen_room = room
                                break
                        if chosen_room:
                            subject_str = f"{assignment.get('subject', 'Без предмета')} ({teacher.name}), {group_name}"
                            entry = ScheduleEntry(day, pair, start, end, teacher, chosen_room, group_name, subject_str)
                            schedule[day].append(entry)
                            occupancy[day][pair]["teachers"].add(teacher.id)
                            occupancy[day][pair]["rooms"].add(chosen_room.id)
                            group_slots[day].setdefault(group_id, []).append(pair)
                            scheduled = True
                # Если не удалось найти слот с требуемой последовательностью,
                # выбираем самый ранний доступный слот из available_slots, при условии последовательности, если уже есть назначение.
                if not scheduled:
                    for pair, start, end in available_slots:
                        if group_id in group_slots[day]:
                            last_assigned = max(group_slots[day][group_id])
                            if pair != last_assigned + 1:
                                continue
                        if teacher.id in occupancy[day][pair]["teachers"]:
                            continue
                        chosen_room = None
                        if teacher.preferred_rooms:
                            for room_id in teacher.preferred_rooms:
                                if room_id not in room_dict:
                                    continue
                                room = room_dict[room_id]
                                if day in room.absences and pair in room.absences[day]:
                                    continue
                                if room.id in occupancy[day][pair]["rooms"]:
                                    continue
                                chosen_room = room
                                break
                        if not chosen_room:
                            for room in rooms:
                                if not room.available:
                                    continue
                                if day in room.absences and pair in room.absences[day]:
                                    continue
                                if room.id in occupancy[day][pair]["rooms"]:
                                    continue
                                chosen_room = room
                                break
                        if chosen_room:
                            subject_str = f"{assignment.get('subject', 'Без предмета')} ({teacher.name}), {group_name}"
                            entry = ScheduleEntry(day, pair, start, end, teacher, chosen_room, group_name, subject_str)
                            schedule[day].append(entry)
                            occupancy[day][pair]["teachers"].add(teacher.id)
                            occupancy[day][pair]["rooms"].add(chosen_room.id)
                            group_slots[day].setdefault(group_id, []).append(pair)
                            scheduled = True
                            break
                # Если ни один слот не подходит, не назначаем (не создаём запись дистанционно, т.к. distance должен выставляться только при явном отсутствии)
        schedule[day].sort(key=lambda e: e.period)
    return schedule

def export_schedule_to_excel(schedule, filename="schedule.xlsx"):
    from openpyxl import Workbook
    wb = Workbook()
    for idx, (day, entries) in enumerate(schedule.items()):
        if idx == 0:
            ws = wb.active
            ws.title = day
        else:
            ws = wb.create_sheet(title=day)
        ws.append(["Пара", "Время", "Предмет", "Преподаватель", "Аудитория", "Группа"])
        for entry in entries:
            time_interval = f"{entry.start_time}-{entry.end_time}"
            teacher_name = entry.teacher.name if entry.teacher is not None else "Не назначен"
            room_name = entry.room.name if entry.room is not None else "Не назначена"
            group_name = entry.group if entry.group is not None else "Не указана"
            ws.append([entry.period, time_interval, entry.subject, teacher_name, room_name, group_name])
    wb.save(filename)
    print(f"Расписание экспортировано в файл {filename}.")

def generate_and_validate_schedule(teachers, rooms, groups):
    time_slots = get_time_slots()
    schedule = generate_schedule(teachers, rooms, groups, time_slots)
    errors = validate_schedule(schedule)
    return schedule, errors
