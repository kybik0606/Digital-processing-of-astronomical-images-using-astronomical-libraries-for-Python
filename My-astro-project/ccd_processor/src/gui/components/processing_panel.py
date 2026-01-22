"""
Панель обработки
"""

import tkinter as tk
from tkinter import ttk

class ProcessingPanel:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.setup_ui()
        
    def setup_ui(self):
        """Создание панели обработки"""
        processing_frame = ttk.LabelFrame(self.parent, text="Обработка")
        processing_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Кнопки создания мастер-кадров
        master_frame = ttk.Frame(processing_frame)
        master_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(master_frame, text="Создать мастер-кадры:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(master_frame, text="Master Bias", 
                  command=self.app.create_master_bias).pack(side=tk.LEFT, padx=5)
        ttk.Button(master_frame, text="Master Dark", 
                  command=self.app.create_master_dark).pack(side=tk.LEFT, padx=5)
        ttk.Button(master_frame, text="Master Flat", 
                  command=self.app.create_master_flat).pack(side=tk.LEFT, padx=5)
        
        # Кнопка калибровки
        ttk.Button(master_frame, text="Калибровать Lights", 
                  command=self.app.calibrate_lights).pack(side=tk.LEFT, padx=5)