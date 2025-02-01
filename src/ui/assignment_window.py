import tkinter as tk
from tkinter import ttk, messagebox
from src.data.storage import save_teachers

class AssignmentWindow(tk.Toplevel):
    def __init__(self, parent, teachers, groups):
        super().__init__(parent)
        self.title("Управление назначениями преподавателей")
        self.teachers = teachers
        self.groups = groups

        tk.Label(self, text="Выберите преподавателя:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.teacher_var = tk.StringVar()
        self.teacher_combo = ttk.Combobox(self, textvariable=self.teacher_var, state="readonly")
        self.teacher_combo['values'] = [f"{t.id}: {t.name}" for t in self.teachers]
        self.teacher_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.teacher_combo.bind("<<ComboboxSelected>>", self.on_teacher_selected)

        self.assignment_tree = ttk.Treeview(self, columns=("Group", "Subject", "Time"), show="headings", height=10)
        self.assignment_tree.heading("Group", text="Группа")
        self.assignment_tree.heading("Subject", text="Предмет")
        self.assignment_tree.heading("Time", text="Время")
        self.assignment_tree.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)

        tk.Label(self, text="Группа:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.group_var = tk.StringVar()
        self.group_combo = ttk.Combobox(self, textvariable=self.group_var, state="readonly")
        self.group_combo['values'] = [f"{g.id}: {g.name}" for g in self.groups]
        self.group_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(self, text="Предмет:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.subject_entry = ttk.Entry(self)
        self.subject_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(self, text="Время:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.time_entry = ttk.Entry(self)
        self.time_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5)

        self.add_button = ttk.Button(self, text="Добавить назначение", command=self.add_assignment)
        self.add_button.grid(row=5, column=0, padx=5, pady=5)

        self.delete_button = ttk.Button(self, text="Удалить выбранное назначение", command=self.delete_assignment)
        self.delete_button.grid(row=5, column=1, padx=5, pady=5)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self.current_teacher = None

    def on_teacher_selected(self, event):
        teacher_str = self.teacher_var.get()
        teacher_id = int(teacher_str.split(":")[0])
        for teacher in self.teachers:
            if teacher.id == teacher_id:
                self.current_teacher = teacher
                break
        self.refresh_assignments()

    def refresh_assignments(self):
        for item in self.assignment_tree.get_children():
            self.assignment_tree.delete(item)
        if not self.current_teacher:
            return
        for idx, assignment in enumerate(self.current_teacher.assignments):
            group_name = self.get_group_name(assignment.get("group_id"))
            subject = assignment.get("subject", "")
            time_val = assignment.get("time", "")
            self.assignment_tree.insert("", "end", iid=idx, values=(group_name, subject, time_val))

    def get_group_name(self, group_id):
        for g in self.groups:
            if g.id == group_id:
                return g.name
        return f"Группа {group_id}"

    def add_assignment(self):
        if not self.current_teacher:
            messagebox.showerror("Ошибка", "Выберите преподавателя!")
            return
        group_str = self.group_combo.get()
        if not group_str:
            messagebox.showerror("Ошибка", "Выберите группу!")
            return
        group_id = int(group_str.split(":")[0])
        subject = self.subject_entry.get().strip()
        time_val = self.time_entry.get().strip()
        if not subject or not time_val:
            messagebox.showerror("Ошибка", "Введите предмет и время!")
            return
        assignment = {"group_id": group_id, "subject": subject, "time": time_val}
        self.current_teacher.assignments.append(assignment)
        self.refresh_assignments()
        save_teachers(self.teachers)
        self.group_combo.set("")
        self.subject_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)

    def delete_assignment(self):
        selected_item = self.assignment_tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите назначение для удаления!")
            return
        index = int(selected_item[0])
        if self.current_teacher and index < len(self.current_teacher.assignments):
            del self.current_teacher.assignments[index]
            self.refresh_assignments()
            save_teachers(self.teachers)
