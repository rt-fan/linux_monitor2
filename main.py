import tkinter as tk
from tkinter import messagebox
import psutil
import sqlite3
import time
import threading

class SystemMonitorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Системный монитор")
        
        self.cpu_label = tk.Label(master, text="Загрузка ЦП: 0%")
        self.cpu_label.pack()
        
        self.ram_label = tk.Label(master, text="Использование ОЗУ: 0%")
        self.ram_label.pack()
        
        self.disk_label = tk.Label(master, text="Использование ПЗУ: 0%")
        self.disk_label.pack()
        
        self.start_button = tk.Button(master, text="Начать запись", command=self.start_recording)
        self.start_button.pack()
        
        self.stop_button = tk.Button(master, text="Остановить", command=self.stop_recording)
        self.stop_button.pack()
        self.stop_button.pack_forget()  # Скрыть кнопку остановки
        
        self.recording = False
        self.start_time = None
        
        self.update_interval = 1  # Интервал обновления в секундах
        self.db_connection = sqlite3.connect('system_monitor.db')
        self.create_table()
        
        self.update_system_info()

    def create_table(self):
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
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        
        self.cpu_label.config(text=f"Загрузка ЦП: {cpu_usage}%")
        self.ram_label.config(text=f"Использование ОЗУ: {ram_usage}%")
        self.disk_label.config(text=f"Использование ПЗУ: {disk_usage}%")
        
        if self.recording:
            self.record_usage(cpu_usage, ram_usage, disk_usage)
        
        self.master.after(self.update_interval * 1000, self.update_system_info)

    def record_usage(self, cpu, ram, disk):
        cursor = self.db_connection.cursor()
        cursor.execute('INSERT INTO system_usage (cpu_usage, ram_usage, disk_usage) VALUES (?, ?, ?)', 
                       (cpu, ram, disk))
        self.db_connection.commit()

    def start_recording(self):
        self.recording = True
        self.start_time = time.time()
        self.start_button.pack_forget()
        self.stop_button.pack()
        self.update_timer()

    def stop_recording(self):
        self.recording = False
        self.stop_button.pack_forget()
        self.start_button.pack()
        self.start_time = None

    def update_timer(self):
        if self.recording:
            elapsed_time = int(time.time() - self.start_time)
            self.stop_button.config(text=f"Остановить (время записи: {elapsed_time} сек)")
            self.master.after(1000, self.update_timer)

    def on_closing(self):
        self.db_connection.close()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemMonitorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()