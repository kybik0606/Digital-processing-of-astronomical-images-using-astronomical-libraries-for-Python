"""
Конфигурация приложения
"""

import os
import json
from pathlib import Path

class Config:
    def __init__(self, config_file=None):
        self.working_directory = os.getcwd()
        self.lights = []
        self.darks = []
        self.bias = []
        self.flats = []
        
        # Мастер-кадры
        self.master_bias = None
        self.master_dark = None  
        self.master_flat = None
        
        # Текущее состояние
        self.current_image_index = 0
        self.current_image_type = "lights"
        
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
            
    def set_working_directory(self, directory):
        """Установка рабочей директории"""
        self.working_directory = directory
        
    def add_files(self, file_type, files):
        """Добавление файлов"""
        if file_type == "lights":
            self.lights.extend(files)
        elif file_type == "darks":
            self.darks.extend(files)
        elif file_type == "bias":
            self.bias.extend(files)
        elif file_type == "flats":
            self.flats.extend(files)
            
    def get_file_counts(self):
        """Получение количества файлов"""
        return {
            "lights_count": len(self.lights),
            "darks_count": len(self.darks),
            "bias_count": len(self.bias),
            "flats_count": len(self.flats)
        }
        
    def save_config(self, filepath):
        """Сохранение конфигурации"""
        config_data = {
            "working_directory": self.working_directory,
            "lights": self.lights,
            "darks": self.darks,
            "bias": self.bias,
            "flats": self.flats
        }
        
        with open(filepath, 'w') as f:
            json.dump(config_data, f, indent=2)
            
    def load_config(self, filepath):
        """Загрузка конфигурации"""
        with open(filepath, 'r') as f:
            config_data = json.load(f)
            
        self.working_directory = config_data.get("working_directory", os.getcwd())
        self.lights = config_data.get("lights", [])
        self.darks = config_data.get("darks", [])
        self.bias = config_data.get("bias", [])
        self.flats = config_data.get("flats", [])