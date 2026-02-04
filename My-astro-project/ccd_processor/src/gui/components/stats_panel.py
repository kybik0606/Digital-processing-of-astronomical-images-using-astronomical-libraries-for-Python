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
        self.stats_frame.config(width=200)  # Увеличил ширину для кнопок
        
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
        """Создание секции для мастер-кадров с кнопками добавления"""
        master_frame = ttk.Frame(self.stats_frame)
        master_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Заголовок
        ttk.Label(master_frame, text="Мастер-кадры:", 
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        # Master Bias с кнопкой
        bias_frame = ttk.Frame(master_frame)
        bias_frame.pack(fill=tk.X, pady=2)
        
        # Левая часть: метка и статус
        bias_left = ttk.Frame(bias_frame)
        bias_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(bias_left, text="Bias:", font=('Arial', 9, 'bold'), width=8).pack(side=tk.LEFT)
        self.master_bias_label = ttk.Label(bias_left, text="❌ Нет", font=('Arial', 9), foreground='red')
        self.master_bias_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Правая часть: кнопка добавления
        add_bias_btn = ttk.Button(bias_frame, text="+", 
                                 width=3,
                                 command=self.app.load_master_bias,
                                 style="Small.TButton")
        add_bias_btn.pack(side=tk.RIGHT)
        
        # Master Dark с кнопкой
        dark_frame = ttk.Frame(master_frame)
        dark_frame.pack(fill=tk.X, pady=2)
        
        # Левая часть: метка и статус
        dark_left = ttk.Frame(dark_frame)
        dark_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(dark_left, text="Dark:", font=('Arial', 9, 'bold'), width=8).pack(side=tk.LEFT)
        self.master_dark_label = ttk.Label(dark_left, text="❌ Нет", font=('Arial', 9), foreground='red')
        self.master_dark_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Правая часть: кнопка добавления
        add_dark_btn = ttk.Button(dark_frame, text="+", 
                                 width=3,
                                 command=self.app.load_master_dark,
                                 style="Small.TButton")
        add_dark_btn.pack(side=tk.RIGHT)
        
        # Master Flat с кнопкой
        flat_frame = ttk.Frame(master_frame)
        flat_frame.pack(fill=tk.X, pady=2)
        
        # Левая часть: метка и статус
        flat_left = ttk.Frame(flat_frame)
        flat_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(flat_left, text="Flat:", font=('Arial', 9, 'bold'), width=8).pack(side=tk.LEFT)
        self.master_flat_label = ttk.Label(flat_left, text="❌ Нет", font=('Arial', 9), foreground='red')
        self.master_flat_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Правая часть: кнопка добавления
        add_flat_btn = ttk.Button(flat_frame, text="+", 
                                 width=3,
                                 command=self.app.load_master_flat,
                                 style="Small.TButton")
        add_flat_btn.pack(side=tk.RIGHT)
        
        # Кнопка просмотра мастер-кадров
        view_button = ttk.Button(master_frame, text="Просмотр мастер-кадров", 
                               command=self._show_master_frames_dialog)
        view_button.pack(fill=tk.X, pady=(10, 5))
        
        # Стиль для маленьких кнопок
        style = ttk.Style()
        style.configure("Small.TButton", font=('Arial', 8), padding=2)
        
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
        """Показать диалог выбора мастер-кадра с темной темой"""
        # Создаем диалоговое окно
        dialog = tk.Toplevel(self.parent)
        dialog.title("🔍 Просмотр мастер-кадра")
        dialog.geometry("320x200")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Темная тема
        dialog.configure(bg='#2b2b2b')
        
        # Центрирование
        dialog.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        dialog_width = 320
        dialog_height = 200
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Основной контейнер
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Заголовок с иконкой
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Иконка (эмодзи или текст)
        icon_label = ttk.Label(header_frame, 
                              text="🔍",
                              font=('Arial', 14),
                              background='#2b2b2b',
                              foreground='white')
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        title_label = ttk.Label(header_frame,
                               text="Выберите мастер-кадр для просмотра",
                               font=('Arial', 11, 'bold'),
                               background='#2b2b2b',
                               foreground='white',
                               wraplength=250)
        title_label.pack(side=tk.LEFT)
        
        # Combobox с пояснением
        combo_frame = ttk.Frame(main_frame)
        combo_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(combo_frame,
                 text="Тип кадра:",
                 font=('Arial', 9),
                 background='#2b2b2b',
                 foreground='#cccccc').pack(anchor=tk.W)
        
        master_var = tk.StringVar(value="Bias")
        master_combo = ttk.Combobox(combo_frame,
                                   textvariable=master_var,
                                   values=["Bias", "Dark", "Flat"],
                                   state="readonly",
                                   width=15,
                                   font=('Arial', 10))
        master_combo.pack(fill=tk.X, pady=(5, 0))
        
        # Tooltip для combobox
        tooltip_text = {
            "Bias": "Кадры нулевой экспозиции (шум сенсора)",
            "Dark": "Темновые кадры (термический шум)",
            "Flat": "Калибровочные кадры (равномерная засветка)"
        }
        
        def show_tooltip(event):
            master_type = master_var.get()
            if master_type in tooltip_text:
                # Можно добавить всплывающую подсказку
                pass
        
        master_combo.bind('<<ComboboxSelected>>', show_tooltip)
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Кнопка Отмена (слева)
        cancel_btn = ttk.Button(button_frame,
                               text="Отмена",
                               command=dialog.destroy,
                               width=12)
        cancel_btn.pack(side=tk.LEFT)
        
        # Пробел между кнопками
        ttk.Frame(button_frame, width=20).pack(side=tk.LEFT)
        
        # Кнопка Просмотр (справа, акцентная)
        view_btn = ttk.Button(button_frame,
                             text="Ок",
                             command=lambda: self._view_master_frame(master_var.get(), dialog),
                             width=12,
                             style="Accent.TButton")
        view_btn.pack(side=tk.RIGHT)
        
        # Горячие клавиши
        dialog.bind('<Return>', lambda e: self._view_master_frame(master_var.get(), dialog))
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        
        # Фокус и выделение
        master_combo.focus_set()
        master_combo.selection_range(0, tk.END)
        
        # Закрытие при клике вне окна (опционально)
        def close_on_click_out(event):
            if event.widget == dialog:
                dialog.destroy()
        
        dialog.bind('<Button-1>', close_on_click_out)
        
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