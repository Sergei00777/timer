import customtkinter as ctk
import threading
import time


class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Таймеры обратного отсчета")
        self.root.geometry("800x850")

        # Стиль интерфейса
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.timers = {
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
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        for name, seconds in self.timers.items():
            timer_frame = ctk.CTkFrame(self.main_frame)
            timer_frame.pack(pady=10, padx=10, fill="x")

            label = ctk.CTkLabel(timer_frame, text=name, font=("Arial", 14, "bold"))
            label.pack(pady=5)

            time_label = ctk.CTkLabel(timer_frame, text=self.format_time(seconds), font=("Arial", 18))
            time_label.pack(pady=5)

            button_frame = ctk.CTkFrame(timer_frame)
            button_frame.pack(pady=5)

            start_btn = ctk.CTkButton(
                button_frame,
                text="Старт",
                command=lambda s=seconds, tl=time_label, n=name: self.start_timer(s, tl, n)
            )
            start_btn.pack(side="left", padx=5)

            stop_btn = ctk.CTkButton(
                button_frame,
                text="Стоп",
                command=lambda n=name: self.stop_timer(n)
            )
            stop_btn.pack(side="left", padx=5)

            reset_btn = ctk.CTkButton(
                button_frame,
                text="Сброс",
                command=lambda s=seconds, tl=time_label, n=name: self.reset_timer(s, tl, n)
            )
            reset_btn.pack(side="left", padx=5)

            # Сохраняем ссылки на элементы
            self.active_timers[name] = {
                "time_left": seconds,
                "label": time_label,
                "running": False,
                "thread": None
            }

    def format_time(self, seconds):
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"

    def start_timer(self, seconds, label, name):
        if self.active_timers[name]["running"]:
            return

        self.active_timers[name]["running"] = True
        self.active_timers[name]["time_left"] = seconds

        def timer_thread():
            while self.active_timers[name]["time_left"] > 0 and self.active_timers[name]["running"]:
                time.sleep(1)
                self.active_timers[name]["time_left"] -= 1
                self.root.after(0,
                                lambda: label.configure(text=self.format_time(self.active_timers[name]["time_left"])))

            self.active_timers[name]["running"] = False

        thread = threading.Thread(target=timer_thread, daemon=True)
        thread.start()
        self.active_timers[name]["thread"] = thread

    def stop_timer(self, name):
        self.active_timers[name]["running"] = False

    def reset_timer(self, seconds, label, name):
        self.stop_timer(name)
        self.active_timers[name]["time_left"] = seconds
        label.configure(text=self.format_time(seconds))


if __name__ == "__main__":
    root = ctk.CTk()
    app = TimerApp(root)
    root.mainloop()