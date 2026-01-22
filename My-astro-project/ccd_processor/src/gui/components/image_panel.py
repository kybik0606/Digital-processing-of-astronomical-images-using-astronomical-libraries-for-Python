"""
Панель изображения
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import rcParams
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
        """Создание холста matplotlib с темной темой"""
        # Настраиваем matplotlib для темной темы
        self._configure_matplotlib_dark_theme()
        
        # Создаем фигуру с темным фоном
        self.fig = plt.Figure(figsize=(8, 6), dpi=100, facecolor='#2b2b2b')
        self.ax = self.fig.add_subplot(111, facecolor='#2b2b2b')
        
        # Настраиваем оси для темной темы
        self.ax.set_title("Загрузите изображение", color='white', fontsize=12)
        
        # Устанавливаем цвет текста и линий
        self.ax.tick_params(colors='white')
        for spine in self.ax.spines.values():
            spine.set_color('white')
        
        # Текст "Нет изображения"
        self.ax.text(0.5, 0.5, "Нет изображения", 
                    ha='center', va='center', 
                    transform=self.ax.transAxes,
                    color='white',
                    fontsize=14)
        
        # Убираем оси
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        
        self.canvas = FigureCanvasTkAgg(self.fig, self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def _configure_matplotlib_dark_theme(self):
        """Настройка темной темы для matplotlib"""
        # Настройки для темной темы matplotlib
        plt.rcParams.update({
            'figure.facecolor': '#2b2b2b',
            'axes.facecolor': '#2b2b2b',
            'axes.edgecolor': 'white',
            'axes.labelcolor': 'white',
            'text.color': 'white',
            'xtick.color': 'white',
            'ytick.color': 'white',
            'grid.color': '#555555',
            'grid.linestyle': '--',
            'grid.alpha': 0.7
        })
        
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
        type_frame.pack(side=tk.RIGHT, padx=5)
        
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
                  command=self.app.toggle_grid).pack(side=tk.LEFT, padx=5)
        
        # Добавляем цветовую карту (БЕЗ ПРИВЯЗКИ К МЕТОДУ)
        self._create_colormap_selector(controls_frame)
        
    def _create_colormap_selector(self, parent_frame):
        """Создание выбора цветовой карты (без привязки)"""
        cmap_frame = ttk.Frame(parent_frame)
        cmap_frame.pack(side=tk.RIGHT, padx=10)
        
    def get_colormap(self):
        """Получить выбранную цветовую карту"""
        return self.cmap_var.get()
        
    def update_display(self, image_data=None, title=None):
        """Обновление отображения изображения"""
        self.ax.clear()
        
        # Настройки для темной темы
        self.ax.set_facecolor('#2b2b2b')
        
        if image_data is None:
            # Отображаем текст "Нет изображения"
            self.ax.text(0.5, 0.5, "Нет изображения", 
                        ha='center', va='center', 
                        transform=self.ax.transAxes,
                        color='white',
                        fontsize=14)
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            display_title = "Загрузите изображение"
        else:
            # Отображаем изображение
            im = self.ax.imshow(image_data, cmap=self.get_colormap(), 
                               aspect='auto', origin='lower')
            
            # Добавляем цветовую шкалу
            if hasattr(self, 'colorbar'):
                self.colorbar.remove()
            self.colorbar = self.fig.colorbar(im, ax=self.ax)
            
            # Настраиваем цветовую шкалу для темной темы
            self.colorbar.ax.yaxis.set_tick_params(color='white')
            plt.setp(self.colorbar.ax.yaxis.get_ticklabels(), color='white')
            self.colorbar.outline.set_edgecolor('white')
            
            display_title = title if title else "Изображение"
        
        # Обновляем заголовок
        self.ax.set_title(display_title, color='white', fontsize=12)
        
        # Настраиваем цвета
        self.ax.tick_params(colors='white')
        for spine in self.ax.spines.values():
            spine.set_color('white')
        
        # Убираем подписи осей если нет изображения
        if image_data is None:
            self.ax.set_xlabel('')
            self.ax.set_ylabel('')
        
        self.canvas.draw()