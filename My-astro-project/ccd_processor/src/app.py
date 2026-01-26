"""
Главный класс приложения
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox  # Добавлен ttk здесь
import os
from astropy.nddata import CCDData
import numpy as np
import ccdproc
import astropy.units as u
import re

from gui.main_window import MainWindow
from utils.config import Config
from processing.calibration import CalibrationProcessor
from processing.masters import MastersProcessor

class CCDProcessorApp:
    def __init__(self):
        self.config = Config()
        self.calibration_processor = CalibrationProcessor(self)
        self.masters_processor = MastersProcessor(self)
        self.root = tk.Tk()
        self.main_window = MainWindow(self.root, self)
        
        # Данные приложения
        self.lights = []
        self.darks = []
        self.bias = []
        self.flats = []
        
        # Текущее состояние
        self.current_image_index = 0
        self.current_image_type = "lights"
        self.current_image = None
        
        # Мастер-кадры
        self.master_bias = None
        self.master_dark = None
        self.master_flat = None
        
        # Инициализация статуса мастер-кадров
        self.update_master_frames_status()
        
    def run(self):
        """Запуск приложения"""
        # Создаем стиль для выделенной кнопки
        style = ttk.Style()
        style.configure("Accent.TButton", font=('Arial', 10, 'bold'))
        
        self.root.title("CCD Processor")
        self.root.geometry("1800x900")

        # Минимальный размер окна
        self.root.minsize(1200, 800)
        
        # Привязка клавиш для навигации
        self.root.bind('<Left>', lambda e: self.previous_image())
        self.root.bind('<Right>', lambda e: self.next_image())
        self.root.focus_set()
        
        self.root.mainloop()
    
    # Свойства для доступа к конфигурации
    @property
    def working_directory(self):
        return self.config.working_directory
    
    # Методы для работы с файлами
    def add_lights(self):
        files = self.select_files("Выберите Light кадры")
        if files:
            self.lights.extend(files)
            self.log_command(f"Добавлено {len(files)} light кадров")
            self.update_stats()
            
            if len(self.lights) == len(files):
                self.current_image_type = "lights"
                self.main_window.image_panel.image_type_var.set("lights")
                self.current_image_index = 0
                self.display_image(files[0])
                self.update_navigation_info()
                self.log_command("Автоматическое переключение на light кадры")
    
    def add_darks(self):
        files = self.select_files("Выберите Dark кадры")
        if files:
            self.darks.extend(files)
            self.log_command(f"Добавлено {len(files)} dark кадров")
            self.update_stats()
    
    def add_bias(self):
        files = self.select_files("Выберите Bias кадры")
        if files:
            self.bias.extend(files)
            self.log_command(f"Добавлено {len(files)} bias кадров")
            self.update_stats()
    
    def add_flats(self):
        files = self.select_files("Выберите Flat кадры")
        if files:
            self.flats.extend(files)
            self.log_command(f"Добавлено {len(files)} flat кадров")
            self.update_stats()
    
    def select_files(self, title):
        """Выбор файлов"""
        files = filedialog.askopenfilenames(
            title=title,
            filetypes=[("FITS files", "*.fits *.fit *.fts"), ("All files", "*.*")]
        )
        return files
    
    def set_working_directory(self):
        """Установка рабочей директории"""
        directory = filedialog.askdirectory(title="Выберите рабочую директорию")
        if directory:
            self.config.set_working_directory(directory)
            self.main_window.top_menu.dir_label.config(
                text=f"Директория: {os.path.basename(directory)}"
            )
            self.log_command(f"Установлена рабочая директория: {directory}")
    
    # Методы для навигации
    def get_current_list(self):
        """Получение текущего списка изображений"""
        if self.current_image_type == "lights":
            return self.lights
        elif self.current_image_type == "darks":
            return self.darks
        elif self.current_image_type == "bias":
            return self.bias
        elif self.current_image_type == "flats":
            return self.flats
        return []
    
    def previous_image(self):
        """Переход к предыдущему изображению"""
        current_list = self.get_current_list()
        if not current_list or len(current_list) == 0:
            return
            
        self.current_image_index = (self.current_image_index - 1) % len(current_list)
        self.display_image(current_list[self.current_image_index], colormap="gray")
        self.update_navigation_info()
    
    def next_image(self):
        """Переход к следующему изображению"""
        current_list = self.get_current_list()
        if not current_list or len(current_list) == 0:
            return
            
        self.current_image_index = (self.current_image_index + 1) % len(current_list)
        self.display_image(current_list[self.current_image_index], colormap="gray")
        self.update_navigation_info()
    
    def on_image_type_changed(self, event):
        """Обработчик изменения типа изображения"""
        new_type = self.main_window.image_panel.image_type_var.get()
        
        if new_type != self.current_image_type:
            self.log_command(f"Переключение типа кадров: {self.current_image_type} -> {new_type}")
            self.current_image_type = new_type
        
        current_list = self.get_current_list()
        
        if current_list and len(current_list) > 0:
            self.current_image_index = 0
            self.display_image(current_list[0], colormap="gray")
            self.update_navigation_info()
            self.log_command(f"Отображение {len(current_list)} {self.current_image_type} кадров")
        else:
            # Вызываем метод из ImagePanel
            self.main_window.image_panel.show_empty_message(self.current_image_type)
            
            self.main_window.image_panel.nav_info.config(text="Нет изображений")
            self.main_window.stats_panel.current_file_label.config(text="Нет")
            self.main_window.stats_panel.image_size_label.config(text="-")
            self.log_command(f"Нет {self.current_image_type} кадров для отображения")
    
    # Методы отображения
    def display_image(self, file_path, colormap="gray"):
        """Отображение изображения"""
        try:
            self.current_image = self.read_fits_with_unit(file_path)
            self.main_window.image_panel.ax.clear()
            
            data = self.current_image.data
            vmin = np.percentile(data, 1)
            vmax = np.percentile(data, 99)
            
            # Используем переданную цветовую карту
            self.main_window.image_panel.ax.imshow(
                data, 
                cmap=colormap, 
                vmin=vmin, 
                vmax=vmax, 
                origin='lower', 
                aspect="equal"
            )
            
            self.main_window.image_panel.ax.set_title(f"{os.path.basename(file_path)}")
            self.main_window.image_panel.canvas.draw()
            
            # Обновление информации
            self.main_window.stats_panel.current_file_label.config(text=os.path.basename(file_path))
            self.main_window.stats_panel.image_size_label.config(text=f"{data.shape[1]} x {data.shape[0]}")
            
            self.log_command(f"Отображен {self.current_image_type}: {os.path.basename(file_path)}")
            
        except Exception as e:
            self.log_command(f"Ошибка загрузки: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")
    
    def update_navigation_info(self):
        """Обновление информации о навигации"""
        current_list = self.get_current_list()
        if current_list and len(current_list) > 0:
            total = len(current_list)
            current_idx = self.current_image_index + 1
            filename = os.path.basename(current_list[self.current_image_index])
            self.main_window.image_panel.nav_info.config(text=f"{current_idx}/{total}: {filename}")
        else:
            self.main_window.image_panel.nav_info.config(text="Нет изображений")
    
    def update_stats(self):
        """Обновление статистики"""
        stats = {
            "lights_count": len(self.lights),
            "darks_count": len(self.darks),
            "bias_count": len(self.bias),
            "flats_count": len(self.flats)
        }
        self.main_window.stats_panel.update_stats(stats)
    
    # Методы обработки
    def create_master_bias(self):
        """Создание мастер bias"""
        if not self.bias:
            self.log_command("Ошибка: Нет bias кадров для обработки")
            messagebox.showwarning("Внимание", "Сначала добавьте bias кадры")
            return
        
        try:
            self.master_bias = self.masters_processor.create_master_bias(self.bias)
            bias_path = os.path.join(self.config.working_directory, "master_bias.fits")
            self.master_bias.write(bias_path, overwrite=True)
            
            self.log_command(f"Master Bias создан из {len(self.bias)} кадров")
            self.log_command(f"Master Bias сохранен как: {bias_path}")
            self.display_master_frame(self.master_bias, "Master Bias")
            
            # Обновление статуса мастер-кадров
            self.update_master_frames_status()
            
        except Exception as e:
            self.log_command(f"Ошибка создания Master Bias: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось создать Master Bias: {str(e)}")
    
    def create_master_dark(self):
        """Создание мастер dark"""
        if not self.darks:
            self.log_command("Ошибка: Нет dark кадров для обработки")
            messagebox.showwarning("Внимание", "Сначала добавьте dark кадры")
            return
        
        try:
            self.master_dark = self.masters_processor.create_master_dark(self.darks, self.master_bias)
            dark_path = os.path.join(self.config.working_directory, "master_dark.fits")
            self.master_dark.write(dark_path, overwrite=True)
            
            self.log_command(f"Master Dark создан из {len(self.darks)} кадров")
            self.log_command(f"Master Dark сохранен как: {dark_path}")
            self.display_master_frame(self.master_dark, "Master Dark")
            
            # Обновление статуса мастер-кадров
            self.update_master_frames_status()
            
        except Exception as e:
            self.log_command(f"Ошибка создания Master Dark: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось создать Master Dark: {str(e)}")
    
    def create_master_flat(self):
        """Создание мастер flat"""
        if not self.flats:
            self.log_command("Ошибка: Нет flat кадров для обработки")
            messagebox.showwarning("Внимание", "Сначала добавьте flat кадры")
            return
        
        try:
            self.master_flat = self.masters_processor.create_master_flat(self.flats, self.master_bias)
            flat_path = os.path.join(self.config.working_directory, "master_flat.fits")
            self.master_flat.write(flat_path, overwrite=True)
            
            self.log_command(f"Master Flat создан из {len(self.flats)} кадров")
            self.log_command(f"Master Flat сохранен как: {flat_path}")
            self.display_master_frame(self.master_flat, "Master Flat")
            
            # Обновление статуса мастер-кадров
            self.update_master_frames_status()
            
        except Exception as e:
            self.log_command(f"Ошибка создания Master Flat: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось создать Master Flat: {str(e)}")
    
    def calibrate_lights(self):
        """Калибровка light кадров"""
        if not self.lights:
            self.log_command("Ошибка: Нет light кадров для калибровки")
            messagebox.showwarning("Внимание", "Сначала добавьте light кадры")
            return
        
        try:
            calibrated_lights = self.calibration_processor.calibrate_lights(
                self.lights, self.master_bias, self.master_dark, self.master_flat
            )
            
            # Сохранение калиброванных файлов
            calibrated_dir = os.path.join(self.config.working_directory, "calibrated")
            os.makedirs(calibrated_dir, exist_ok=True)
            
            for i, calibrated in enumerate(calibrated_lights):
                output_filename = f"calibrated_{os.path.basename(self.lights[i])}"
                output_path = os.path.join(calibrated_dir, output_filename)
                calibrated.write(output_path, overwrite=True)
                self.log_command(f"  - Сохранен как: {output_path}")
            
            self.log_command("Калибровка всех light кадров завершена!")
            messagebox.showinfo("Готово", f"Калибровка light кадров завершена! Файлы сохранены в {calibrated_dir}")
            
        except Exception as e:
            self.log_command(f"Ошибка калибровки: {str(e)}")
            messagebox.showerror("Ошибка", f"Ошибка при калибровке: {str(e)}")
    
    def display_master_frame(self, ccd_data, title):
        """Отображение мастер-кадра"""
        self.main_window.image_panel.ax.clear()
        
        data = ccd_data.data
        vmin = np.percentile(data, 5)
        vmax = np.percentile(data, 95)
        
        self.main_window.image_panel.ax.imshow(data, cmap='gray', vmin=vmin, vmax=vmax, origin='lower')
        self.main_window.image_panel.ax.set_title(title)
        self.main_window.image_panel.canvas.draw()
        
        self.main_window.stats_panel.current_file_label.config(text=title)
        self.main_window.stats_panel.image_size_label.config(text=f"{data.shape[1]} x {data.shape[0]}")
        
        self.log_command(f"Отображен: {title}")
    
    def update_master_frames_status(self):
        """Обновление статуса мастер-кадров в статистике"""
        masters_status = {
            "Bias": self.master_bias is not None,
            "Dark": self.master_dark is not None,
            "Flat": self.master_flat is not None
        }
        if hasattr(self, 'main_window') and hasattr(self.main_window, 'stats_panel'):
            self.main_window.stats_panel.update_master_frames(masters_status)

    def display_master_frame_dialog(self, master_type):
        """Отображение выбранного мастер-кадра"""
        master_frame = None
        title = ""
        
        if master_type == "Bias" and self.master_bias is not None:
            master_frame = self.master_bias
            title = "Master Bias"
        elif master_type == "Dark" and self.master_dark is not None:
            master_frame = self.master_dark
            title = "Master Dark"
        elif master_type == "Flat" and self.master_flat is not None:
            master_frame = self.master_flat
            title = "Master Flat"
        
        if master_frame is not None:
            self.display_master_frame(master_frame, title)
            self.log_command(f"Просмотр: {title}")
        else:
            self.log_command(f"Мастер-кадр {master_type} не создан")
            messagebox.showwarning("Внимание", f"Мастер-кадр {master_type} не создан")
    
    # Вспомогательные методы
    def read_fits_with_unit(self, file_path, unit='adu'):
        """Чтение FITS файла"""
        try:
            ccd = CCDData.read(file_path, unit=unit)
            ccd.file_path = file_path
            return ccd
        except Exception as e:
            self.log_command(f"Ошибка при чтении {file_path}: {str(e)}")
            raise
    
    def get_exposure_time(self, ccd_data):
        """Извлечение времени экспозиции"""
        try:
            header = ccd_data.header
            exposure_keys = ['EXPTIME', 'EXPOSURE', 'EXP TIME', 'EXPTIME1']
            
            for key in exposure_keys:
                if key in header:
                    exposure_time = header[key]
                    if isinstance(exposure_time, str):
                        match = re.search(r'(\d+\.?\d*)', exposure_time)
                        if match:
                            exposure_time = float(match.group(1))
                        else:
                            continue
                    return exposure_time * u.second
                    
            if hasattr(ccd_data, 'file_path'):
                filename = os.path.basename(ccd_data.file_path)
                match = re.search(r'(\d+\.?\d*)[sS]', filename)
                if match:
                    return float(match.group(1)) * u.second
                    
            return 1.0 * u.second
            
        except Exception:
            return 1.0 * u.second
    
    def log_command(self, message):
        """Логирование команды"""
        self.main_window.command_panel.log_command(message)

    def show_inverted(self, show):
        """Показать или скрыть инвертированную версию"""
        try:
            ax = self.main_window.image_panel.ax
            if ax.images:  # Если есть изображение
                ax.images[0].set_cmap("gray_r" if show else "gray")
                self.main_window.image_panel.canvas.draw()
        except:
            pass  # Просто игнорируем ошибки
    
    def auto_flats(self):
        """Авто flats (заглушка)"""
        self.log_command("Функция автоматического создания flats в разработке")
        messagebox.showinfo("Авто Flats", "Эта функция находится в разработке")