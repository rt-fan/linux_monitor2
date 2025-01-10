import tkinter as tk
import psutil
import sqlite3
import time


class SystemMonitorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Тестовое задание")
        self.master.geometry("300x320+100+100")

        self.label = tk.Label(master, text="Уровень загруженности:")
        self.label.place(x=20, y=20)
        
        self.cpu_label = tk.Label(master, text="Загрузка ЦП: 0%")
        self.cpu_label.place(x=20, y=60)
        
        self.ram_label = tk.Label(master, text="Использование ОЗУ: 0")
        self.ram_label.place(x=20, y=90)
        
        self.disk_label = tk.Label(master, text="Использование ПЗУ: %")
        self.disk_label.place(x=20, y=120)

        self.set_time = tk.Entry(master, width=3)
        self.set_time.insert(0, "1")
        self.set_time_label_1 = tk.Label(master, text="Обновлять каждые")
        self.set_time_label_2 = tk.Label(master, text="сек.")
        self.set_time_label_1.place(x=50, y=200)
        self.set_time.place(x=180, y=200)
        self.set_time_label_2.place(x=210, y=200)
        
        self.start_button = tk.Button(master, text="Начать запись", width=20,
                                      command=self.start_recording)
        self.start_button.place(x=50, y=230)
        
        self.stop_button = tk.Button(master, text="Остановить запись", width=20, 
                                     command=self.stop_recording)
        self.stop_button.place(x=50, y=230)
        self.stop_button.place_forget()

        self.elapsed_time = tk.Label(master, text="00:00")
        self.elapsed_time.place(x=130, y=270)
        
        self.recording = False
        self.start_time = None
        
        self.db_connection = sqlite3.connect('system_monitor.db')
        self.create_table()

        self.total_memory = psutil.virtual_memory().total / (1024 ** 3)
        self.total_disk = psutil.disk_usage('/').total / (1024 ** 3)
        
        self.update_system_info()

    def create_table(self):
        '''Создание БД'''
        cursor = self.db_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_usage (
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_usage REAL,
                ram_usage REAL,
                disk_usage REAL
            )
        ''')
        self.db_connection.commit()

    def update_system_info(self):
        '''Обновление окна'''
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().free / (1024 ** 3)
        disk_usage = psutil.disk_usage('/').free / (1024 ** 3)

        self.update_interval = int(self.set_time.get())
        
        self.cpu_label.config(text=f"Загрузка ЦП: {cpu_usage}%")
        self.ram_label.config(text=f"ОЗУ: Свободно {ram_usage:.1f} из {self.total_memory:.1f} Gb")
        self.disk_label.config(text=f"ПЗУ: Свободно {disk_usage:.1f} из {self.total_disk:.1f} Gb")
        
        if self.recording:
            self.record_usage(cpu_usage, ram_usage, disk_usage)
        
        self.master.after(self.update_interval * 1000, self.update_system_info)

    def record_usage(self, cpu, ram, disk):
        '''Запись данных в БД'''
        cursor = self.db_connection.cursor()
        cursor.execute('''
            INSERT INTO system_usage (timestamp, cpu_usage, ram_usage, disk_usage)
            VALUES (DATETIME('now', '+3 hours'), ?, ?, ?)
        ''', (cpu, ram, disk))
        self.db_connection.commit()

    def start_recording(self):
        '''Начинаем запись'''
        self.recording = True
        self.start_time = time.time()
        self.start_button.place_forget()
        self.stop_button.place(x=50, y=230)
        self.update_timer()

    def stop_recording(self):
        '''Останавливаем запись'''
        self.recording = False
        self.stop_button.place_forget()
        self.start_button.place(x=50, y=230)
        self.start_time = None
        self.elapsed_time.config(text=f"00:00")
    
    @staticmethod
    def seconds_to_mm_ss(seconds):
        '''Форматируем секунды в вид mm:ss'''
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def update_timer(self):
        ''''''
        if self.recording:
            elapsed_time = int(time.time() - self.start_time)
            formatted_time = self.seconds_to_mm_ss(elapsed_time)
            self.elapsed_time.config(text=f"{formatted_time}")
            self.master.after(1000, self.update_timer)

    def on_closing(self):
        self.db_connection.close()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SystemMonitorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
