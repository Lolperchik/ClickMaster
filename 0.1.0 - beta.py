import tkinter as tk
from tkinter import ttk, messagebox
from pynput.mouse import Button, Controller
from pynput import keyboard
import threading
import time
import os

mouse = Controller()

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        root.title("ClickMaster")
        root.geometry("700x600")
        root.resizable(False, False)
        root.configure(bg="#2c3e50")

        # Установка иконки (если файл доступен)
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
            root.iconbitmap(icon_path)
        except:
            pass

        # Установка темы и стилей
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 12, "bold"), foreground="white", background="#2c3e50")
        style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=10, foreground="white")
        style.configure("TFrame", background="#2c3e50")
        style.configure("TLabelframe", background="#34495e", foreground="white", font=("Segoe UI", 12, "bold"))
        style.configure("TLabelframe.Label", background="#34495e", foreground="white")
        style.map("TCombobox", fieldbackground=[("readonly", "#ecf0f1")], foreground=[("readonly", "black")])
        style.configure("TCombobox", padding=5, font=("Segoe UI", 11))
        style.configure("TEntry", fieldbackground="#ecf0f1", foreground="black", font=("Segoe UI", 11))

        # Цвета для кнопок
        style.configure("Accent.TButton", background="#27ae60")  # Зеленый для "Старт"
        style.map("Accent.TButton", background=[("active", "#219653")])
        style.configure("Stop.TButton", background="#e74c3c")  # Красный для "Стоп"
        style.map("Stop.TButton", background=[("active", "#c0392b")])

        self.clicking = False
        self.running = True
        self.click_thread = None

        # Интервал клика
        interval_frame = ttk.LabelFrame(root, text="Интервал кликов")
        interval_frame.pack(fill="x", padx=20, pady=15)
        ttk.Label(interval_frame, text="часы").grid(row=0, column=1, padx=10)
        ttk.Label(interval_frame, text="минуты").grid(row=0, column=3, padx=10)
        ttk.Label(interval_frame, text="секунды").grid(row=0, column=5, padx=10)
        ttk.Label(interval_frame, text="миллисекунды").grid(row=0, column=7, padx=10)
        self.hours_var = tk.IntVar(value=0)
        self.minutes_var = tk.IntVar(value=0)
        self.seconds_var = tk.IntVar(value=0)
        self.milliseconds_var = tk.IntVar(value=0)
        self.hours_entry = ttk.Entry(interval_frame, width=5, textvariable=self.hours_var)
        self.hours_entry.grid(row=0, column=0, padx=10, pady=10)
        self.minutes_entry = ttk.Entry(interval_frame, width=5, textvariable=self.minutes_var)
        self.minutes_entry.grid(row=0, column=2, padx=10, pady=10)
        self.seconds_entry = ttk.Entry(interval_frame, width=5, textvariable=self.seconds_var)
        self.seconds_entry.grid(row=0, column=4, padx=10, pady=10)
        self.milliseconds_entry = ttk.Entry(interval_frame, width=7, textvariable=self.milliseconds_var)
        self.milliseconds_entry.grid(row=0, column=6, padx=10, pady=10)

        # Повтор клика
        repeat_frame = ttk.LabelFrame(root, text="Повтор кликов")
        repeat_frame.pack(fill="x", padx=20, pady=15)
        self.repeat_var = tk.IntVar(value=0)
        self.infinite_repeat_var = tk.BooleanVar(value=True)
        self.rb_infinite = ttk.Radiobutton(repeat_frame, text="Бесконечно (до остановки)", variable=self.infinite_repeat_var, value=True, command=self.repeat_toggle)
        self.rb_infinite.grid(row=0, column=0, sticky="w", padx=15, pady=10, columnspan=2)
        self.rb_times = ttk.Radiobutton(repeat_frame, text="Количество", variable=self.infinite_repeat_var, value=False, command=self.repeat_toggle)
        self.rb_times.grid(row=1, column=0, sticky="w", padx=15, pady=10)
        self.times_entry = ttk.Entry(repeat_frame, width=10, textvariable=self.repeat_var)
        self.times_entry.grid(row=1, column=1, padx=10, pady=10)
        self.times_entry.config(state="disabled")

        # Опции клика
        options_frame = ttk.LabelFrame(root, text="Параметры клика")
        options_frame.pack(fill="x", padx=20, pady=15)
        ttk.Label(options_frame, text="Кнопка мыши").grid(row=0, column=0, sticky="w", padx=15, pady=10)
        self.mouse_button_var = tk.StringVar(value="Левая")
        self.mouse_button_combo = ttk.Combobox(options_frame, values=["Левая", "Правая"], state="readonly", textvariable=self.mouse_button_var, width=12)
        self.mouse_button_combo.grid(row=0, column=1, sticky="w", padx=10, pady=10)
        ttk.Label(options_frame, text="Тип клика").grid(row=0, column=2, sticky="w", padx=15, pady=10)
        self.click_type_var = tk.StringVar(value="Одинарный")
        self.click_type_combo = ttk.Combobox(options_frame, values=["Одинарный", "Двойной"], state="readonly", textvariable=self.click_type_var, width=12)
        self.click_type_combo.grid(row=0, column=3, sticky="w", padx=10, pady=10)

        # Позиция клика
        position_frame = ttk.LabelFrame(root, text="Позиция клика")
        position_frame.pack(fill="x", padx=20, pady=15)
        self.position_var = tk.StringVar(value="current")
        self.rb_current_pos = ttk.Radiobutton(position_frame, text="Текущая позиция курсора", variable=self.position_var, value="current", command=self.position_toggle)
        self.rb_current_pos.grid(row=0, column=0, sticky="w", padx=15, pady=10, columnspan=4)
        self.rb_fixed_pos = ttk.Radiobutton(position_frame, text="Фиксированная позиция: X", variable=self.position_var, value="fixed", command=self.position_toggle)
        self.rb_fixed_pos.grid(row=1, column=0, sticky="w", padx=15, pady=10)
        self.x_var = tk.IntVar(value=0)
        self.y_var = tk.IntVar(value=0)
        self.x_entry = ttk.Entry(position_frame, width=7, textvariable=self.x_var)
        self.x_entry.grid(row=1, column=1, padx=10, pady=10)
        ttk.Label(position_frame, text="Y").grid(row=1, column=2, padx=10, pady=10)
        self.y_entry = ttk.Entry(position_frame, width=7, textvariable=self.y_var)
        self.y_entry.grid(row=1, column=3, padx=10, pady=10)
        self.pick_button = ttk.Button(position_frame, text="Выбрать позицию", command=self.pick_location)
        self.pick_button.grid(row=1, column=4, padx=15, pady=10)

        # Кнопки управления
        buttons_frame = ttk.Frame(root, style="TFrame")
        buttons_frame.pack(fill="x", padx=20, pady=15)
        self.start_button = ttk.Button(buttons_frame, text="Старт (F6)", command=self.start_clicking, style="Accent.TButton")
        self.start_button.grid(row=0, column=0, padx=10, pady=10)
        self.stop_button = ttk.Button(buttons_frame, text="Стоп (F7)", command=self.stop_clicking, style="Stop.TButton")
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)
        self.toggle_button = ttk.Button(buttons_frame, text="Переключить (F8)", command=self.toggle_clicking)
        self.toggle_button.grid(row=0, column=2, padx=10, pady=10)

        # Нижние кнопки
        bottom_frame = ttk.Frame(root, style="TFrame")
        bottom_frame.pack(fill="x", padx=20, pady=15)
        ttk.Button(bottom_frame, text="Сохранить настройки", command=self.save_settings).grid(row=0, column=0, padx=10, pady=10)
        ttk.Button(bottom_frame, text="Сбросить настройки", command=self.reset_settings).grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(bottom_frame, text="Горячие клавиши", command=self.show_hotkeys).grid(row=0, column=2, padx=10, pady=10)

        self.position_toggle()

        # Горячие клавиши
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

    def repeat_toggle(self):
        if self.infinite_repeat_var.get():
            self.times_entry.config(state="disabled")
        else:
            self.times_entry.config(state="normal")

    def position_toggle(self):
        if self.position_var.get() == "current":
            self.x_entry.config(state="disabled")
            self.y_entry.config(state="disabled")
            self.pick_button.config(state="disabled")
        else:
            self.x_entry.config(state="normal")
            self.y_entry.config(state="normal")
            self.pick_button.config(state="normal")

    def pick_location(self):
        messagebox.showinfo("Выбор позиции", "Переместите курсор в нужную позицию и нажмите F9")
        self.picking = True
        def on_press(key):
            if key == keyboard.Key.f9:
                pos = mouse.position
                self.x_var.set(pos[0])
                self.y_var.set(pos[1])
                self.picking = False
                return False
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

    def start_clicking(self):
        if self.clicking:
            return
        interval = self.get_interval()
        if interval is None:
            messagebox.showerror("Ошибка", "Неверный интервал кликов")
            return
        times = None
        if not self.infinite_repeat_var.get():
            times = self.repeat_var.get()
            if times <= 0:
                messagebox.showerror("Ошибка", "Количество повторов должно быть больше 0")
                return
        self.clicking = True
        self.click_thread = threading.Thread(target=self.click_loop, args=(interval, times), daemon=True)
        self.click_thread.start()

    def stop_clicking(self):
        self.clicking = False

    def toggle_clicking(self):
        if self.clicking:
            self.stop_clicking()
        else:
            self.start_clicking()

    def get_interval(self):
        try:
            h = self.hours_var.get()
            m = self.minutes_var.get()
            s = self.seconds_var.get()
            ms = self.milliseconds_var.get()
            total = h*3600 + m*60 + s + ms/1000
            if total <= 0:
                return None
            return total
        except Exception:
            return None

    def click_loop(self, interval, times):
        btn = Button.left if self.mouse_button_var.get() == "Левая" else Button.right
        click_type = self.click_type_var.get()
        count = 0
        while self.clicking and self.running:
            if self.position_var.get() == "current":
                x, y = mouse.position
            else:
                x = self.x_var.get()
                y = self.y_var.get()
            mouse.position = (x, y)
            if click_type == "Одинарный":
                mouse.click(btn)
            else:  # Двойной
                mouse.click(btn)
                time.sleep(0.05)
                mouse.click(btn)
            count += 1
            if times is not None and count >= times:
                self.clicking = False
                break
            time.sleep(interval)

    def save_settings(self):
        messagebox.showinfo("Сохранение настроек", "Функция сохранения пока не реализована")

    def reset_settings(self):
        self.hours_var.set(0)
        self.minutes_var.set(0)
        self.seconds_var.set(0)
        self.milliseconds_var.set(0)
        self.infinite_repeat_var.set(True)
        self.repeat_var.set(0)
        self.mouse_button_var.set("Левая")
        self.click_type_var.set("Одинарный")
        self.position_var.set("current")
        self.position_toggle()

    def show_hotkeys(self):
        messagebox.showinfo("Горячие клавиши", "F6 - Старт\nF7 - Стоп\nF8 - Переключить\nF9 - Выбрать позицию (при выборе позиции)")

    def on_key_press(self, key):
        if key == keyboard.Key.f6:
            self.start_clicking()
        elif key == keyboard.Key.f7:
            self.stop_clicking()
        elif key == keyboard.Key.f8:
            self.toggle_clicking()

    def close(self):
        self.running = False
        self.clicking = False
        self.listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()
