"""
Панель изображения
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class ImagePanel:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.setup_ui()
        
    def setup_ui(self):
        """Создание панели изображения"""
        self.frame = ttk.LabelFrame(self.parent, text="Изображение")
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self._create_matplotlib_canvas()
        self._create_navigation_panel()
        self._create_image_controls()
        
    def _create_matplotlib_canvas(self):
        """Создание холста matplotlib"""
        self.fig = plt.Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Загрузите изображение")
        self.ax.text(0.5, 0.5, "Нет изображения", 
                    ha='center', va='center', transform=self.ax.transAxes)
        
        self.canvas = FigureCanvasTkAgg(self.fig, self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def _create_navigation_panel(self):
        """Создание панели навигации"""
        self.nav_frame = ttk.Frame(self.frame)
        self.nav_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Кнопки навигации
        ttk.Button(self.nav_frame, text="← Предыдущий", 
                  command=self.app.previous_image).pack(side=tk.LEFT, padx=2)
        
        self.nav_info = ttk.Label(self.nav_frame, text="Нет изображений")
        self.nav_info.pack(side=tk.LEFT, padx=10, expand=True)
        
        ttk.Button(self.nav_frame, text="Следующий →", 
                  command=self.app.next_image).pack(side=tk.RIGHT, padx=2)
        
        # Выбор типа изображений
        self._create_type_selector()
        
    def _create_type_selector(self):
        """Создание селектора типа изображений"""
        type_frame = ttk.Frame(self.nav_frame)
        type_frame.pack(side=tk.RIGHT, padx=10)
        
        ttk.Label(type_frame, text="Тип:").pack(side=tk.LEFT)
        self.image_type_var = tk.StringVar(value="lights")
        type_combo = ttk.Combobox(type_frame, textvariable=self.image_type_var, 
                                 values=["lights", "darks", "bias", "flats"], 
                                 state="readonly", width=8)
        type_combo.pack(side=tk.LEFT, padx=5)
        type_combo.bind('<<ComboboxSelected>>', self.app.on_image_type_changed)
        
    def _create_image_controls(self):
        """Создание элементов управления изображением"""
        controls_frame = ttk.Frame(self.frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Инвертировать", 
                  command=self.app.invert_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="Сетка", 
                  command=self.app.toggle_grid).pack(side=tk.LEFT, padx=2)