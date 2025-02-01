import re

def validate_schedule(schedule):
    errors = []
    for day, entries in schedule.items():
        group_periods = {}
        for entry in entries:
            # Сгруппируем по группе (используем наименование группы)
            group_name = entry.group
            if group_name:
                group_periods.setdefault(group_name, []).append(entry.period)
        for group_name, periods in group_periods.items():
            periods_sorted = sorted(periods)
            if len(periods_sorted) > 4:
                errors.append(f"В день {day}: Группа {group_name} имеет больше 4 пар ({len(periods_sorted)}).")
            # Если более одного занятия, они должны идти подряд
            if len(periods_sorted) > 1:
                for i in range(1, len(periods_sorted)):
                    if periods_sorted[i] != periods_sorted[i-1] + 1:
                        errors.append(f"В день {day}: Расписание для группы {group_name} имеет разрыв между парами.")
    return errors
