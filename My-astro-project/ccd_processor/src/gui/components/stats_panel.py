"""
Панель статистики
"""

import tkinter as tk
from tkinter import ttk
import os

class StatsPanel:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.setup_ui()
        
    def setup_ui(self):
        """Создание панели статистики"""
        # Основной фрейм панели статистики
        self.stats_frame = ttk.LabelFrame(self.parent, text="Статистика")
        
        # Устанавливаем фиксированную ширину и запрещаем изменение размера
        self.stats_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.stats_frame.pack_propagate(False)  # Запрещаем изменение размера
        self.stats_frame.config(width=200)  # Фиксированная ширина 250 пикселей
        
        # Остальной код без изменений...
        self.counters_frame = ttk.Frame(self.stats_frame)
        self.counters_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self._create_file_counters()
        self._create_master_frames_section()
        self._create_current_file_info()
        
    def _create_file_counters(self):
        """Создание счетчиков файлов"""
        # Lights
        lights_frame = ttk.Frame(self.counters_frame)
        lights_frame.pack(fill=tk.X, pady=2)
        ttk.Label(lights_frame, text="Lights:", font=('Arial', 10, 'bold'), width=8).pack(side=tk.LEFT)
        self.lights_count = ttk.Label(lights_frame, text="0", font=('Arial', 10))
        self.lights_count.pack(side=tk.LEFT)
        
        # Darks
        darks_frame = ttk.Frame(self.counters_frame)
        darks_frame.pack(fill=tk.X, pady=2)
        ttk.Label(darks_frame, text="Darks:", font=('Arial', 10, 'bold'), width=8).pack(side=tk.LEFT)
        self.darks_count = ttk.Label(darks_frame, text="0", font=('Arial', 10))
        self.darks_count.pack(side=tk.LEFT)
        
        # Bias
        bias_frame = ttk.Frame(self.counters_frame)
        bias_frame.pack(fill=tk.X, pady=2)
        ttk.Label(bias_frame, text="Bias:", font=('Arial', 10, 'bold'), width=8).pack(side=tk.LEFT)
        self.bias_count = ttk.Label(bias_frame, text="0", font=('Arial', 10))
        self.bias_count.pack(side=tk.LEFT)
        
        # Flats
        flats_frame = ttk.Frame(self.counters_frame)
        flats_frame.pack(fill=tk.X, pady=2)
        ttk.Label(flats_frame, text="Flats:", font=('Arial', 10, 'bold'), width=8).pack(side=tk.LEFT)
        self.flats_count = ttk.Label(flats_frame, text="0", font=('Arial', 10))
        self.flats_count.pack(side=tk.LEFT)
        
        # Разделитель
        ttk.Separator(self.stats_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=10)
        
    def _create_master_frames_section(self):
        """Создание секции для мастер-кадров"""
        master_frame = ttk.Frame(self.stats_frame)
        master_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(master_frame, text="Мастер-кадры:", 
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        # Master Bias
        bias_frame = ttk.Frame(master_frame)
        bias_frame.pack(fill=tk.X, pady=2)
        ttk.Label(bias_frame, text="Bias:", font=('Arial', 9, 'bold'), width=8).pack(side=tk.LEFT)
        self.master_bias_label = ttk.Label(bias_frame, text="❌ Нет", font=('Arial', 9), foreground='red')
        self.master_bias_label.pack(side=tk.LEFT)
        
        # Master Dark
        dark_frame = ttk.Frame(master_frame)
        dark_frame.pack(fill=tk.X, pady=2)
        ttk.Label(dark_frame, text="Dark:", font=('Arial', 9, 'bold'), width=8).pack(side=tk.LEFT)
        self.master_dark_label = ttk.Label(dark_frame, text="❌ Нет", font=('Arial', 9), foreground='red')
        self.master_dark_label.pack(side=tk.LEFT)
        
        # Master Flat
        flat_frame = ttk.Frame(master_frame)
        flat_frame.pack(fill=tk.X, pady=2)
        ttk.Label(flat_frame, text="Flat:", font=('Arial', 9, 'bold'), width=8).pack(side=tk.LEFT)
        self.master_flat_label = ttk.Label(flat_frame, text="❌ Нет", font=('Arial', 9), foreground='red')
        self.master_flat_label.pack(side=tk.LEFT)
        
        # Кнопка просмотра
        view_button = ttk.Button(master_frame, text="Просмотр мастер-кадров", 
                               command=self._show_master_frames_dialog)
        view_button.pack(fill=tk.X, pady=5)
        
        # Разделитель
        ttk.Separator(self.stats_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=10)
        
    def _create_current_file_info(self):
        """Информация о текущем файле"""
        current_frame = ttk.Frame(self.stats_frame)
        current_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(current_frame, text="Текущее изображение:", 
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        # Файл
        file_frame = ttk.Frame(current_frame)
        file_frame.pack(fill=tk.X, pady=2)
        ttk.Label(file_frame, text="Файл:", font=('Arial', 9, 'bold'), width=8).pack(side=tk.LEFT)
        self.current_file_label = ttk.Label(file_frame, text="Нет", font=('Arial', 9))
        self.current_file_label.pack(side=tk.LEFT)
        
        # Размер
        size_frame = ttk.Frame(current_frame)
        size_frame.pack(fill=tk.X, pady=2)
        ttk.Label(size_frame, text="Размер:", font=('Arial', 9, 'bold'), width=8).pack(side=tk.LEFT)
        self.image_size_label = ttk.Label(size_frame, text="-", font=('Arial', 9))
        self.image_size_label.pack(side=tk.LEFT)
        
    def _show_master_frames_dialog(self):
        """Показать диалог выбора мастер-кадра"""
        # Создаем диалоговое окно
        dialog = tk.Toplevel(self.parent)
        dialog.title("Просмотр мастер-кадра")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Центрируем диалог
        dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (300 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (150 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(dialog, text="Выберите мастер-кадр для просмотра:", 
                 font=('Arial', 10)).pack(pady=15)
        
        master_var = tk.StringVar(value="Bias")
        master_combo = ttk.Combobox(dialog, textvariable=master_var,
                                   values=["Bias", "Dark", "Flat"], 
                                   state="readonly", width=10)
        master_combo.pack(pady=10)
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Просмотр", 
                  command=lambda: self._view_master_frame(master_var.get(), dialog)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def _view_master_frame(self, master_type, dialog):
        """Просмотр выбранного мастер-кадра"""
        dialog.destroy()
        self.app.display_master_frame_dialog(master_type)
        
    def update_stats(self, stats):
        """Обновление статистики"""
        self.lights_count.config(text=str(stats.get("lights_count", 0)))
        self.darks_count.config(text=str(stats.get("darks_count", 0)))
        self.bias_count.config(text=str(stats.get("bias_count", 0)))
        self.flats_count.config(text=str(stats.get("flats_count", 0)))
                
    def update_current_file(self, filename, size):
        """Обновление информации о текущем файле"""
        self.current_file_label.config(text=filename)
        self.image_size_label.config(text=size)
        
    def update_master_frames(self, masters):
        """Обновление статуса мастер-кадров"""
        if masters.get("Bias", False):
            self.master_bias_label.config(text="✅ Создан", foreground='green')
        else:
            self.master_bias_label.config(text="❌ Нет", foreground='red')
            
        if masters.get("Dark", False):
            self.master_dark_label.config(text="✅ Создан", foreground='green')
        else:
            self.master_dark_label.config(text="❌ Нет", foreground='red')
            
        if masters.get("Flat", False):
            self.master_flat_label.config(text="✅ Создан", foreground='green')
        else:
            self.master_flat_label.config(text="❌ Нет", foreground='red')