import tkinter as tk
from src.ui.main_window import MainWindow

def main():
    root = tk.Tk()
    root.title("Генератор расписания колледжа")
    # Устанавливаем иконку с помощью PhotoImage (убедитесь, что файл "myicon.png" существует)
    icon = tk.PhotoImage(file="myicon.png")
    root.iconphoto(False, icon)
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
