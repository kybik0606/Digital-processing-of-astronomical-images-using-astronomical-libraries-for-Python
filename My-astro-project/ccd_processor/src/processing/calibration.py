"""
Функции калибровки изображений
"""

import ccdproc
import astropy.units as u
import numpy as np
import os

class CalibrationProcessor:
    def __init__(self, app):
        self.app = app  # Сохраняем ссылку на приложение
        
    def calibrate_lights(self, lights, master_bias, master_dark, master_flat):
        """Калибровка light кадров (только вычитание мастер-кадров)"""
        calibrated_lights = []
        
        # Логируем в интерфейс
        self.app.log_command(f"НАЧАЛО КАЛИБРОВКИ: {len(lights)} light кадров")
        
        for i, light_path in enumerate(lights):
            try:
                self.app.log_command(f"[{i+1}/{len(lights)}] Калибровка: {os.path.basename(light_path)}")
                
                # 1. Загружаем light
                light = self.app.read_fits_with_unit(light_path)
                calibrated = light.copy()
                
                # Логируем исходные данные
                self._log_data_stats("Оригинал", light.data)
                
                # 2. Вычитаем bias (если есть)
                if master_bias is not None:
                    self.app.log_command(f"  └─ Вычитаем Master Bias...")
                    calibrated = ccdproc.subtract_bias(calibrated, master_bias)
                    self._log_data_stats("После Bias", calibrated.data)
                else:
                    self.app.log_command(f"  └─ Master Bias: пропущено")
                
                # 3. Вычитаем dark (если есть) - ВАЖНО: с масштабированием по экспозиции
                if master_dark is not None:
                    self.app.log_command(f"  └─ Вычитаем Master Dark...")
                    
                    calibrated = ccdproc.subtract_dark(
                        calibrated, 
                        master_dark,
                        exposure_time='exposure',  # Ищет ключ 'exposure' в header
                        exposure_unit=u.second,
                        scale=True  # МАСШТАБИРУЕМ по времени экспозиции!
                    )
                    self._log_data_stats("После Dark", calibrated.data)
                else:
                    self.app.log_command(f"  └─ Master Dark: пропущено")
                
                # 4. Делим на flat (если есть)
                if master_flat is not None:
                    self.app.log_command(f"  └─ Делим на Master Flat...")
                    
                    # Проверяем что flat не содержит нулей
                    if np.any(master_flat.data <= 0):
                        self.app.log_command(f"    ⚠️ ВНИМАНИЕ: Master Flat содержит нулевые или отрицательные значения!")
                        # Корректируем чтобы избежать деления на ноль
                        flat_data = master_flat.data.copy()
                        flat_data[flat_data <= 0] = np.median(flat_data) * 0.01
                        master_flat_corrected = ccdproc.CCDData(
                            flat_data, 
                            unit=master_flat.unit,
                            header=master_flat.header
                        )
                        calibrated = ccdproc.flat_correct(calibrated, master_flat_corrected)
                    else:
                        calibrated = ccdproc.flat_correct(calibrated, master_flat)
                    
                    self._log_data_stats("После Flat", calibrated.data)
                else:
                    self.app.log_command(f"  └─ Master Flat: пропущено")
                
                # 5. Убираем отрицательные значения (после вычитаний могут появиться)
                calibrated.data = np.clip(calibrated.data, 0, None)
                
                # 6. НЕ нормализуем! Оставляем как есть после калибровки
                self._log_data_stats("Финальный (без нормализации)", calibrated.data)
                
                calibrated_lights.append(calibrated)
                self.app.log_command(f"  ✓ Успешно калиброван")
                
            except Exception as e:
                error_msg = f"Ошибка калибровки {os.path.basename(light_path)}: {str(e)}"
                self.app.log_command(f"  ✗ {error_msg}")
                raise Exception(error_msg)
        
        self.app.log_command(f"КАЛИБРОВКА ЗАВЕРШЕНА: {len(calibrated_lights)}/{len(lights)} кадров")
                
        return calibrated_lights
    
    def _log_data_stats(self, stage, data):
        """Логировать статистику данных в интерфейс"""
        if data.size == 0:
            self.app.log_command(f"    [{stage}] Пустые данные!")
            return
            
        # Основные статистики
        stats = {
            "Min": f"{np.min(data):.2f}",
            "Max": f"{np.max(data):.2f}",
            "Mean": f"{np.mean(data):.2f}",
            "Std": f"{np.std(data):.2f}",
            "Median": f"{np.median(data):.2f}"
        }
        
        # Считаем яркие пиксели (потенциальные звезды)
        median = np.median(data)
        std = np.std(data)
        
        if std > 0:  # Избегаем деления на ноль
            threshold = median + 3 * std
            bright_pixels = np.sum(data > threshold)
            bright_percent = bright_pixels / data.size * 100
        else:
            bright_pixels = 0
            bright_percent = 0
        
        # Логируем компактно
        stats_str = f"Min:{stats['Min']} Max:{stats['Max']} Mean:{stats['Mean']}"
        self.app.log_command(f"    [{stage}] {stats_str} | Ярких пикс: {bright_pixels} ({bright_percent:.2f}%)")
        
        # Предупреждение если слишком мало ярких пикселей
        if bright_pixels < 100 and stage == "Финальный (без нормализации)":
            self.app.log_command(f"    ⚠️  МАЛО ЯРКИХ ПИКСЕЛЕЙ ({bright_pixels}) - возможны проблемы с регистрацией")
    
    def calibrate_without_flat(self, lights, master_bias, master_dark):
        """Калибровка БЕЗ flat (для тестирования)"""
        self.app.log_command(f"ТЕСТ: Калибровка БЕЗ Flat")
        
        return self.calibrate_lights(lights, master_bias, master_dark, None)