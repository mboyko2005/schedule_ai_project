import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from src.data.teacher import Teacher
from src.data.room import Room
from src.data.group import Group
from src.data.storage import load_teachers, save_teachers, load_rooms, save_rooms, load_groups, save_groups
from src.logic.scheduler import generate_and_validate_schedule, export_schedule_to_excel
from src.ui.assignment_window import AssignmentWindow

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор расписания колледжа")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 10))
        self.style.configure("TButton", font=("Helvetica", 10), padding=5)
        self.style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"), foreground="#333")
        self.style.configure("Treeview", font=("Helvetica", 10), rowheight=25)

        self.teachers = load_teachers()
        self.rooms = load_rooms()
        self.groups = load_groups()

        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        btn_add_teacher = ttk.Button(control_frame, text="Добавить преподавателя", command=self.add_teacher)
        btn_add_teacher.grid(row=0, column=0, padx=5, pady=5)

        btn_add_room = ttk.Button(control_frame, text="Добавить аудиторию", command=self.add_room)
        btn_add_room.grid(row=0, column=1, padx=5, pady=5)

        btn_add_group = ttk.Button(control_frame, text="Добавить группу", command=self.add_group)
        btn_add_group.grid(row=0, column=2, padx=5, pady=5)

        btn_generate = ttk.Button(control_frame, text="Сгенерировать расписание", command=self.generate_schedule)
        btn_generate.grid(row=0, column=3, padx=5, pady=5)

        btn_export = ttk.Button(control_frame, text="Экспортировать в Excel", command=self.export_to_excel)
        btn_export.grid(row=0, column=4, padx=5, pady=5)

        btn_assignments = ttk.Button(control_frame, text="Управление назначениями", command=self.open_assignment_window)
        btn_assignments.grid(row=0, column=5, padx=5, pady=5)

        btn_absence = ttk.Button(control_frame, text="Указать отсутствие преподавателя", command=self.set_teacher_absence)
        btn_absence.grid(row=0, column=6, padx=5, pady=5)

        btn_show_absences = ttk.Button(control_frame, text="Просмотр отсутствий", command=self.show_teacher_absences)
        btn_show_absences.grid(row=0, column=7, padx=5, pady=5)

        btn_delete_teacher = ttk.Button(control_frame, text="Удалить преподавателя", command=self.delete_teacher)
        btn_delete_teacher.grid(row=1, column=0, padx=5, pady=5)

        btn_delete_group = ttk.Button(control_frame, text="Удалить группу", command=self.delete_group)
        btn_delete_group.grid(row=1, column=1, padx=5, pady=5)

        btn_delete_room = ttk.Button(control_frame, text="Удалить аудиторию", command=self.delete_room)
        btn_delete_room.grid(row=1, column=2, padx=5, pady=5)

        btn_show_rooms = ttk.Button(control_frame, text="Показать все кабинеты", command=self.show_all_rooms)
        btn_show_rooms.grid(row=1, column=3, padx=5, pady=5)

        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(tree_frame,
                                 columns=("Day", "Period", "Time", "Subject", "Teacher", "Room", "Group"),
                                 show="headings")
        self.tree.heading("Day", text="День")
        self.tree.heading("Period", text="Пара")
        self.tree.heading("Time", text="Время")
        self.tree.heading("Subject", text="Предмет")
        self.tree.heading("Teacher", text="Преподаватель")
        self.tree.heading("Room", text="Аудитория")
        self.tree.heading("Group", text="Группа")
        self.tree.column("Day", width=100, anchor="center")
        self.tree.column("Period", width=50, anchor="center")
        self.tree.column("Time", width=120, anchor="center")
        self.tree.column("Subject", width=350, anchor="w")
        self.tree.column("Teacher", width=150, anchor="center")
        self.tree.column("Room", width=150, anchor="center")
        self.tree.column("Group", width=150, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.current_schedule = None

    def add_teacher(self):
        name = simpledialog.askstring("Новый преподаватель", "Введите имя преподавателя:")
        if name:
            teacher = Teacher(name)
            self.teachers.append(teacher)
            save_teachers(self.teachers)
            messagebox.showinfo("Информация", f"Добавлен: {teacher}")

    def add_room(self):
        name = simpledialog.askstring("Новая аудитория", "Введите название/номер аудитории:")
        if not name:
            return
        try:
            capacity = int(simpledialog.askstring("Вместимость", "Введите вместимость аудитории:"))
        except (TypeError, ValueError):
            messagebox.showerror("Ошибка", "Некорректное значение вместимости!")
            return
        room = Room(name, capacity)
        self.rooms.append(room)
        save_rooms(self.rooms)
        messagebox.showinfo("Информация", f"Добавлена: {room}")

    def add_group(self):
        name = simpledialog.askstring("Новая группа", "Введите название группы:")
        if name:
            group = Group(name)
            self.groups.append(group)
            save_groups(self.groups)
            messagebox.showinfo("Информация", f"Добавлена: {group}")

    def generate_schedule(self):
        if not self.teachers or not self.rooms:
            messagebox.showerror("Ошибка", "Сначала добавьте преподавателей и аудитории!")
            return
        schedule, errors = generate_and_validate_schedule(self.teachers, self.rooms, self.groups)
        self.current_schedule = schedule
        self.show_schedule(schedule)
        if errors:
            messagebox.showwarning("Предупреждение", f"В расписании обнаружены ошибки:\n" + "\n".join(errors))
        else:
            messagebox.showinfo("Успех", "Расписание сгенерировано без ошибок.")

    def show_schedule(self, schedule):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for day, entries in schedule.items():
            for entry in entries:
                time_interval = f"{entry.start_time}-{entry.end_time}"
                teacher_name = entry.teacher.name if entry.teacher is not None else "Не назначен"
                room_name = entry.room.name if entry.room is not None else "Не назначена"
                self.tree.insert("", tk.END, values=(day, entry.period, time_interval,
                                                     entry.subject, teacher_name, room_name, entry.group))

    def export_to_excel(self):
        if not self.current_schedule:
            messagebox.showerror("Ошибка", "Нет сгенерированного расписания для экспорта!")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if filename:
            export_schedule_to_excel(self.current_schedule, self.groups, filename)
            messagebox.showinfo("Успех", f"Расписание сохранено в {filename}")

    def open_assignment_window(self):
        AssignmentWindow(self.root, self.teachers, self.groups)

    def set_teacher_absence(self):
        # Окно выбора преподавателя из списка.
        win = tk.Toplevel(self.root)
        win.title("Выбор преподавателя для отсутствия")
        tk.Label(win, text="Выберите преподавателя:").pack(padx=10, pady=5)
        lb = tk.Listbox(win, width=50, font=("Helvetica", 10))
        for t in self.teachers:
            lb.insert(tk.END, f"{t.id}: {t.name}")
        lb.pack(padx=10, pady=5)
        def select_teacher():
            selection = lb.curselection()
            if not selection:
                messagebox.showerror("Ошибка", "Выберите преподавателя!")
                return
            index = selection[0]
            selected_teacher = self.teachers[index]
            win.destroy()
            # Открываем окно для задания отсутствия.
            absence_win = tk.Toplevel(self.root)
            absence_win.title("Задание отсутствия")
            tk.Label(absence_win, text=f"Преподаватель: {selected_teacher.name}").grid(row=0, column=0, columnspan=2, padx=10, pady=5)
            tk.Label(absence_win, text="Тип отсутствия:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
            absence_type_var = tk.StringVar(value="1")
            absence_type_menu = ttk.Combobox(absence_win, textvariable=absence_type_var, state="readonly",
                                             values=["1 - один день", "2 - неделя"])
            absence_type_menu.grid(row=1, column=1, padx=10, pady=5)
            tk.Label(absence_win, text="Если один день, укажите день:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
            day_entry = ttk.Entry(absence_win)
            day_entry.grid(row=2, column=1, padx=10, pady=5)
            tk.Label(absence_win, text="Введите номера пар через запятую:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
            pairs_entry = ttk.Entry(absence_win)
            pairs_entry.grid(row=3, column=1, padx=10, pady=5)
            def save_absence():
                atype = absence_type_var.get()[0]  # "1" или "2"
                pairs_str = pairs_entry.get().strip()
                if not pairs_str:
                    messagebox.showerror("Ошибка", "Введите номера пар!")
                    return
                try:
                    pairs = [int(p.strip()) for p in pairs_str.split(",")]
                except ValueError:
                    messagebox.showerror("Ошибка", "Неверный формат номеров пар!")
                    return
                if atype == "1":
                    day = day_entry.get().strip()
                    if not day:
                        messagebox.showerror("Ошибка", "Введите день!")
                        return
                    selected_teacher.absences[day] = pairs
                    save_teachers(self.teachers)
                    messagebox.showinfo("Информация", f"Для преподавателя {selected_teacher.name} установлено отсутствие в день {day} на пары: {pairs}")
                else:
                    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
                    for d in days:
                        selected_teacher.absences[d] = pairs
                    save_teachers(self.teachers)
                    messagebox.showinfo("Информация", f"Для преподавателя {selected_teacher.name} установлено отсутствие на всю неделю на пары: {pairs}")
                absence_win.destroy()
            btn_save = ttk.Button(absence_win, text="Сохранить отсутствие", command=save_absence)
            btn_save.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
        btn_select = ttk.Button(win, text="Выбрать", command=select_teacher)
        btn_select.pack(padx=10, pady=10)
    def show_teacher_absences(self):
        # Открываем окно, где отображаются записи об отсутствиях преподавателей.
        win = tk.Toplevel(self.root)
        win.title("Отсутствия преподавателей")
        tree = ttk.Treeview(win, columns=("Teacher", "День", "Пары"), show="headings")
        tree.heading("Teacher", text="Преподаватель")
        tree.heading("День", text="День")
        tree.heading("Пары", text="Пары")
        tree.column("Teacher", width=150, anchor="center")
        tree.column("День", width=100, anchor="center")
        tree.column("Пары", width=150, anchor="center")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for teacher in self.teachers:
            if teacher.absences:
                for day, pairs in teacher.absences.items():
                    tree.insert("", tk.END, values=(teacher.name, day, ", ".join(map(str, pairs))))
        def delete_absence():
            selected = tree.selection()
            if not selected:
                messagebox.showerror("Ошибка", "Выберите запись для удаления!")
                return
            item = selected[0]
            values = tree.item(item, "values")
            teacher_name, day, _ = values
            for teacher in self.teachers:
                if teacher.name == teacher_name:
                    if day in teacher.absences:
                        del teacher.absences[day]
                        save_teachers(self.teachers)
                        tree.delete(item)
                        messagebox.showinfo("Информация", f"Запись об отсутствии для {teacher_name} в день {day} удалена.")
                    break
        btn_del = ttk.Button(win, text="Удалить выбранную запись", command=delete_absence)
        btn_del.pack(padx=10, pady=10)
    def delete_teacher(self):
        win = tk.Toplevel(self.root)
        win.title("Удалить преподавателя")
        lb = tk.Listbox(win, width=60, font=("Helvetica", 10))
        for t in self.teachers:
            lb.insert(tk.END, str(t))
        lb.pack(padx=10, pady=10)
        def do_delete():
            selection = lb.curselection()
            if not selection:
                messagebox.showerror("Ошибка", "Выберите преподавателя для удаления!")
                return
            index = selection[0]
            teacher = self.teachers.pop(index)
            save_teachers(self.teachers)
            lb.delete(index)
            messagebox.showinfo("Информация", f"Удалён: {teacher}")
        btn = ttk.Button(win, text="Удалить выбранного", command=do_delete)
        btn.pack(padx=10, pady=10)
    def delete_group(self):
        win = tk.Toplevel(self.root)
        win.title("Удалить группу")
        lb = tk.Listbox(win, width=60, font=("Helvetica", 10))
        for g in self.groups:
            lb.insert(tk.END, str(g))
        lb.pack(padx=10, pady=10)
        def do_delete():
            selection = lb.curselection()
            if not selection:
                messagebox.showerror("Ошибка", "Выберите группу для удаления!")
                return
            index = selection[0]
            group = self.groups.pop(index)
            save_groups(self.groups)
            lb.delete(index)
            messagebox.showinfo("Информация", f"Удалена: {group}")
        btn = ttk.Button(win, text="Удалить выбранную", command=do_delete)
        btn.pack(padx=10, pady=10)
    def delete_room(self):
        win = tk.Toplevel(self.root)
        win.title("Удалить аудиторию")
        lb = tk.Listbox(win, width=60, font=("Helvetica", 10))
        for r in self.rooms:
            lb.insert(tk.END, f"ID {r.id} - {r.name} (Вместимость: {r.capacity})")
        lb.pack(padx=10, pady=10)
        def do_delete():
            selection = lb.curselection()
            if not selection:
                messagebox.showerror("Ошибка", "Выберите аудиторию для удаления!")
                return
            index = selection[0]
            room = self.rooms.pop(index)
            save_rooms(self.rooms)
            lb.delete(index)
            messagebox.showinfo("Информация", f"Удалена: {room}")
        btn = ttk.Button(win, text="Удалить выбранную", command=do_delete)
        btn.pack(padx=10, pady=10)
    def show_all_rooms(self):
        win = tk.Toplevel(self.root)
        win.title("Список аудиторий")
        tree = ttk.Treeview(win, columns=("ID", "Название", "Вместимость"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Название", text="Название")
        tree.heading("Вместимость", text="Вместимость")
        tree.column("ID", width=50, anchor="center")
        tree.column("Название", width=150, anchor="center")
        tree.column("Вместимость", width=100, anchor="center")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for r in self.rooms:
            tree.insert("", tk.END, values=(r.id, r.name, r.capacity))

if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
