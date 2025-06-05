import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel
import json
from datetime import datetime, time
import threading
import time as time_module
import os
from PIL import Image, ImageTk


class WaterTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Трекер приема воды")
        self.root.geometry("400x600")
        self.root.configure(bg='white')

        if not os.path.exists('water_data.json'):
            self.first_run()
        else:
            self.load_data()

        self.setup_ui()
        self.start_notifications()
        self.show_initial_reminder()

    def show_initial_reminder(self):
        """Показывает напоминание при запуске приложения"""
        if self.data['current_intake'] < self.data['daily_goal']:
            remaining = self.data['daily_goal'] - self.data['current_intake']
            messagebox.showinfo(
                "Напоминание",
                f"Сегодня вам осталось выпить {remaining} мл воды"
            )

    def first_run(self):
        """Первая настройка программы"""
        weight = simpledialog.askinteger("Начало работы", "Введите ваш вес (кг):",
                                         parent=self.root, minvalue=30, maxvalue=200)
        if weight is None:
            exit()

        plant = simpledialog.askstring("Выбор растения",
                                       "Выберите растение (flower/cactus/monstera):",
                                       parent=self.root)
        if plant not in ['flower', 'cactus', 'monstera']:
            plant = 'flower'

        self.data = {
            'weight': weight,
            'daily_goal': weight * 30,
            'current_intake': 0,
            'plant': plant,
            'last_update': datetime.now().strftime("%Y-%m-%d"),
            'days_completed': 0
        }
        self.save_data()

    def load_data(self):
        """Загрузка данных из файла"""
        try:
            with open('water_data.json', 'r') as f:
                self.data = json.load(f)

            today = datetime.now().strftime("%Y-%m-%d")
            if self.data['last_update'] != today:
                self.new_day(today)
        except:
            os.remove('water_data.json')
            self.first_run()

    def new_day(self, today):
        """Обработка нового дня"""
        if self.data['current_intake'] >= self.data['daily_goal']:
            self.data['days_completed'] += 1

        self.data['current_intake'] = 0
        self.data['last_update'] = today
        self.save_data()

    def save_data(self):
        """Сохранение данных в файл"""
        with open('water_data.json', 'w') as f:
            json.dump(self.data, f, indent=4)

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Заголовок
        tk.Label(self.root, text="Трекер приема воды", font=('Arial', 20), bg='white').pack(pady=10)

        # Кнопка настроек
        tk.Button(self.root, text="⚙", font=('Arial', 12), command=self.show_settings,
                  bg='white', relief='flat', bd=0).place(x=350, y=10, width=40, height=40)

        # Изображение растения
        self.img_label = tk.Label(self.root, bg='white')
        self.img_label.pack(pady=10)
        self.update_image()

        # Прогресс
        self.progress_label = tk.Label(self.root,
                                       text=f"{self.data['current_intake']} / {self.data['daily_goal']} мл",
                                       font=('Arial', 14), bg='white')
        self.progress_label.pack(pady=5)

        # Прогресс бар
        self.canvas = tk.Canvas(self.root, width=300, height=20, bg='white', highlightthickness=0)
        self.canvas.pack()
        self.progress_bg = self.canvas.create_rectangle(0, 0, 300, 20, fill='#e0e0e0')
        self.progress = self.canvas.create_rectangle(0, 0, 0, 20, fill='green')
        self.update_progress()

        # Кнопки добавления воды
        button_frame = tk.Frame(self.root, bg='white')
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="+100 мл", command=lambda: self.add_water(100),
                  bg='#4CAF50', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="+250 мл", command=lambda: self.add_water(250),
                  bg='#4CAF50', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="+500 мл", command=lambda: self.add_water(500),
                  bg='#4CAF50', fg='white').pack(side=tk.LEFT, padx=5)

        # Кнопка сброса прогресса
        tk.Button(self.root, text="Сбросить дневной прогресс", command=self.reset_daily_progress,
                  bg='#f44336', fg='white', font=('Arial', 12)).pack(pady=15)

        # Информация о прогрессе
        tk.Label(self.root,
                 text=f"Успешных дней: {self.data['days_completed']}",
                 font=('Arial', 12), bg='white').pack()

    def update_image(self):
        """Обновление изображения растения"""
        try:
            progress = min(self.data['current_intake'] / self.data['daily_goal'], 1.0)
            stage = min(int(progress * 5), 4)  # stage от 0 до 4

            # Получаем путь к директории со скриптом
            script_dir = os.path.dirname(os.path.abspath(__file__))
            img_name = f"{self.data['plant']}_stage_{stage}.png"
            img_path = os.path.join(script_dir, img_name)

            # Проверяем существование файла
            if not os.path.exists(img_path):
                # Если файл не найден, попробуем альтернативный вариант именования
                alt_img_name = f"{self.data['plant']}_stage_{stage + 1}.png"
                alt_img_path = os.path.join(script_dir, alt_img_name)
                if os.path.exists(alt_img_path):
                    img_path = alt_img_path
                else:
                    raise FileNotFoundError(f"Не найдены файлы {img_name} или {alt_img_name}")

            img = Image.open(img_path)
            img = img.resize((200, 200), Image.LANCZOS)
            self.img = ImageTk.PhotoImage(img)
            self.img_label.configure(image=self.img)
            self.img_label.image = self.img
        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")
            # Отображаем текстовую информацию вместо изображения
            self.img_label.configure(text=f"Растение: {self.data['plant']}\nСтадия: {stage + 1}/5",
                                   font=('Arial', 12), compound='top')

    def update_progress(self):
        """Обновление прогресс бара"""
        progress = min(self.data['current_intake'] / self.data['daily_goal'], 1.0)
        width = 300 * progress
        self.canvas.coords(self.progress, 0, 0, width, 20)
        self.progress_label.config(text=f"{self.data['current_intake']} / {self.data['daily_goal']} мл")

    def add_water(self, amount):
        """Добавление выпитой воды"""
        self.data['current_intake'] += amount
        self.save_data()
        self.update_progress()
        self.update_image()

        if self.data['current_intake'] >= self.data['daily_goal']:
            messagebox.showinfo("Ура!", "Вы достигли дневной нормы!")

    def reset_daily_progress(self):
        """Сброс дневного прогресса"""
        if messagebox.askyesno("Сброс", "Вы уверены, что хотите сбросить дневной прогресс?"):
            self.data['current_intake'] = 0
            self.save_data()
            self.update_progress()
            self.update_image()
            messagebox.showinfo("Сброс", "Дневной прогресс сброшен!")

    def show_settings(self):
        """Окно настроек"""
        settings = Toplevel(self.root)
        settings.title("Настройки")
        settings.geometry("300x250")
        settings.configure(bg='white')
        settings.grab_set()

        tk.Label(settings, text="Настройки трекера", font=('Arial', 16), bg='white').pack(pady=10)

        # Выбор растения
        tk.Label(settings, text="Выберите растение:", bg='white').pack()
        plant_var = tk.StringVar(value=self.data['plant'])

        plants_frame = tk.Frame(settings, bg='white')
        plants_frame.pack()

        tk.Radiobutton(plants_frame, text="Цветок", variable=plant_var,
                       value="flower", bg='white').pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(plants_frame, text="Кактус", variable=plant_var,
                       value="cactus", bg='white').pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(plants_frame, text="Монстера", variable=plant_var,
                       value="monstera", bg='white').pack(side=tk.LEFT, padx=5)

        # Изменение веса
        tk.Label(settings, text="Ваш вес (кг):", bg='white').pack(pady=(10, 0))
        self.weight_entry = tk.Entry(settings, justify='center')
        self.weight_entry.insert(0, str(self.data['weight']))
        self.weight_entry.pack()

        # Кнопки сохранения/отмены
        buttons_frame = tk.Frame(settings, bg='white')
        buttons_frame.pack(pady=15)

        tk.Button(buttons_frame, text="Отмена", command=settings.destroy,
                  bg='#f44336', fg='white').pack(side=tk.LEFT, padx=10)
        tk.Button(buttons_frame, text="Сохранить", command=lambda: self.save_settings(plant_var.get(), settings),
                  bg='#4CAF50', fg='white').pack(side=tk.LEFT, padx=10)

    def save_settings(self, plant, settings_window):
        """Сохранение настроек"""
        try:
            new_weight = int(self.weight_entry.get())
            if 30 <= new_weight <= 200:
                self.data['weight'] = new_weight
                self.data['daily_goal'] = new_weight * 30
                self.data['plant'] = plant
                self.save_data()
                self.update_progress()
                self.update_image()
                settings_window.destroy()
                messagebox.showinfo("Сохранено", "Настройки успешно сохранены!")
            else:
                messagebox.showerror("Ошибка", "Вес должен быть от 30 до 200 кг")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректный вес (число)")

    def start_notifications(self):
        """Метод для запуска системы уведомлений"""

        def notification_loop():
            while True:
                try:
                    now = datetime.now().time()
                    today = datetime.now().strftime("%Y-%m-%d")

                    if today != self.data['last_update']:
                        self.new_day(today)
                        self.root.after(0, self.update_progress)
                        self.root.after(0, self.update_image)

                    # Уведомления каждые 2 часа с 8:00 до 22:00
                    if (time(8, 0) <= now <= time(22, 0)) and now.minute == 0 and now.hour % 2 == 0:
                        if self.data['current_intake'] < self.data['daily_goal']:
                            remaining = self.data['daily_goal'] - self.data['current_intake']
                            self.root.after(0, lambda: messagebox.showinfo(
                                "Напоминание",
                                f"Осталось выпить {remaining} мл воды"
                            ))

                    time_module.sleep(60)

                except Exception as e:
                    print(f"Ошибка в потоке уведомлений: {e}")
                    time_module.sleep(60)

        notification_thread = threading.Thread(target=notification_loop, daemon=True)
        notification_thread.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = WaterTracker(root)
    root.mainloop()