import customtkinter as ctk
import threading
import time
from pygame import mixer
import os


class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Таймер с прокруткой")
        self.root.geometry("600x700")

        # Инициализация звука
        mixer.init()
        self.sound_file = "alarm.wav"  # Нужен файл alarm.wav в той же папке
        if not os.path.exists(self.sound_file):
            self.sound_file = None

        # Настройки темы
        self.theme_mode = "dark"
        ctk.set_appearance_mode(self.theme_mode)
        ctk.set_default_color_theme("blue")

        # Основные таймеры
        self.default_timers = {
            "10 минут": 600,
            "15 минут": 900,
            "20 минут": 1200,
            "30 минут": 1800,
            "40 минут": 2400,
            "50 минут": 3000
        }

        self.active_timers = {}  # Для хранения активных таймеров

        self.create_widgets()

    def create_widgets(self):
        # Главный контейнер с прокруткой
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Canvas + Scrollbar
        self.canvas = ctk.CTkCanvas(self.main_container, highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(self.main_container, orientation="vertical", command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas)

        # Настройка прокрутки
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Переключатель темы
        self.theme_switch = ctk.CTkSwitch(
            self.scrollable_frame,
            text="Темная тема",
            command=self.toggle_theme
        )
        self.theme_switch.pack(pady=5)
        self.theme_switch.select() if self.theme_mode == "dark" else self.theme_switch.deselect()

        # Поле для добавления своего таймера
        self.custom_timer_frame = ctk.CTkFrame(self.scrollable_frame)
        self.custom_timer_frame.pack(pady=10, fill="x")

        self.custom_minutes = ctk.CTkEntry(self.custom_timer_frame, placeholder_text="Минуты")
        self.custom_minutes.pack(side="left", padx=5)

        self.add_custom_btn = ctk.CTkButton(
            self.custom_timer_frame,
            text="Добавить таймер",
            command=self.add_custom_timer
        )
        self.add_custom_btn.pack(side="left", padx=5)

        # Создание стандартных таймеров
        for name, seconds in self.default_timers.items():
            self.create_timer_ui(name, seconds)

    def create_timer_ui(self, name, seconds):
        timer_frame = ctk.CTkFrame(self.scrollable_frame)
        timer_frame.pack(pady=10, padx=10, fill="x")

        label = ctk.CTkLabel(timer_frame, text=name, font=("Arial", 14, "bold"))
        label.pack(pady=5)

        time_label = ctk.CTkLabel(timer_frame, text=self.format_time(seconds), font=("Arial", 18))
        time_label.pack(pady=5)

        # Прогресс-бар
        progress = ctk.CTkProgressBar(timer_frame, height=10)
        progress.pack(fill="x", padx=10, pady=5)
        progress.set(1)  # Полный прогресс

        button_frame = ctk.CTkFrame(timer_frame)
        button_frame.pack(pady=5)

        start_btn = ctk.CTkButton(
            button_frame,
            text="Старт",
            command=lambda n=name: self.start_timer(n)
        )
        start_btn.pack(side="left", padx=5)

        pause_btn = ctk.CTkButton(
            button_frame,
            text="Пауза",
            command=lambda n=name: self.pause_timer(n)
        )
        pause_btn.pack(side="left", padx=5)

        reset_btn = ctk.CTkButton(
            button_frame,
            text="Сброс",
            command=lambda n=name, s=seconds: self.reset_timer(n, s)
        )
        reset_btn.pack(side="left", padx=5)

        # Сохраняем ссылки на элементы
        self.active_timers[name] = {
            "initial_seconds": seconds,
            "time_left": seconds,
            "label": time_label,
            "progress": progress,
            "running": False,
            "paused": False,
            "thread": None
        }

    def format_time(self, seconds):
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"

    def start_timer(self, name):
        if self.active_timers[name]["running"]:
            return

        self.active_timers[name]["running"] = True
        self.active_timers[name]["paused"] = False

        def timer_thread():
            while (
                    self.active_timers[name]["time_left"] > 0
                    and self.active_timers[name]["running"]
            ):
                if not self.active_timers[name]["paused"]:
                    time.sleep(1)
                    self.active_timers[name]["time_left"] -= 1

                    # Обновляем интерфейс
                    self.root.after(0, lambda: (
                        self.active_timers[name]["label"].configure(
                            text=self.format_time(self.active_timers[name]["time_left"])
                        ),
                        self.active_timers[name]["progress"].set(
                            self.active_timers[name]["time_left"] / self.active_timers[name]["initial_seconds"]
                        )
                    ))

            # Таймер завершился
            if self.active_timers[name]["time_left"] == 0:
                self.root.after(0, lambda: self.play_alarm())

            self.active_timers[name]["running"] = False

        thread = threading.Thread(target=timer_thread, daemon=True)
        thread.start()
        self.active_timers[name]["thread"] = thread

    def pause_timer(self, name):
        if self.active_timers[name]["running"]:
            self.active_timers[name]["paused"] = not self.active_timers[name]["paused"]

    def reset_timer(self, name, seconds):
        self.active_timers[name]["running"] = False
        self.active_timers[name]["time_left"] = seconds
        self.active_timers[name]["label"].configure(text=self.format_time(seconds))
        self.active_timers[name]["progress"].set(1)

    def play_alarm(self):
        if self.sound_file:
            mixer.music.load(self.sound_file)
            mixer.music.play()

    def toggle_theme(self):
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        ctk.set_appearance_mode(self.theme_mode)
        self.theme_switch.configure(text="Темная тема" if self.theme_mode == "dark" else "Светлая тема")

    def add_custom_timer(self):
        try:
            minutes = int(self.custom_minutes.get())
            if minutes <= 0:
                raise ValueError
            name = f"{minutes} минут"
            seconds = minutes * 60

            if name not in self.active_timers:
                self.create_timer_ui(name, seconds)
            else:
                print("Таймер уже существует!")
        except ValueError:
            print("Введите корректное число минут!")


if __name__ == "__main__":
    root = ctk.CTk()
    app = TimerApp(root)
    root.mainloop()