"""
Функции калибровки изображений
"""

import ccdproc
import astropy.units as u
import numpy as np
import os
from astropy.io import fits
from astropy.nddata import CCDData

# Импортируем модуль проверки целостности
try:
    from .integrity_checker import IntegrityChecker
    INTEGRITY_CHECKER_AVAILABLE = True
except ImportError:
    # Если модуль не найден, работаем без проверки целостности
    INTEGRITY_CHECKER_AVAILABLE = False
    print("Предупреждение: модуль integrity_checker не найден. Проверка целостности отключена.")

class CalibrationProcessor:
    def __init__(self, app):
        self.app = app  # Сохраняем ссылку на приложение
        
    def calibrate_lights(self, lights, master_bias, master_dark, master_flat):
        """Калибровка light кадров (только вычитание мастер-кадров)"""
        calibrated_lights = []
        
        # Логируем в интерфейс
        self.app.log_command(f"Начало калибровки: {len(lights)} кадров")
        if INTEGRITY_CHECKER_AVAILABLE:
            self.app.log_command("Проверка целостности: включена")
        else:
            self.app.log_command("Проверка целостности: отключена (модуль не найден)")
        self.app.log_command("")
        
        for i, light_path in enumerate(lights):
            try:
                filename = os.path.basename(light_path)
                self.app.log_command(f"Калибровка [{i+1}/{len(lights)}]: {filename}")
                
                # 1. Загружаем light
                light = self.app.read_fits_with_unit(light_path)
                calibrated = light.copy()
                
                # 2. Вычитаем bias (если есть)
                if master_bias is not None:
                    calibrated = ccdproc.subtract_bias(calibrated, master_bias)
                    self.app.log_command(f"  - Вычтен Master Bias")
                else:
                    self.app.log_command(f"  - Master Bias: нет")
                
                # 3. Вычитаем dark (если есть) - ВАЖНО: с масштабированием по экспозиции
                if master_dark is not None:
                    calibrated = ccdproc.subtract_dark(
                        calibrated, 
                        master_dark,
                        exposure_time='exposure',  # Ищет ключ 'exposure' в header
                        exposure_unit=u.second,
                        scale=True  # МАСШТАБИРУЕМ по времени экспозиции!
                    )
                    self.app.log_command(f"  - Вычтен Master Dark")
                else:
                    self.app.log_command(f"  - Master Dark: нет")
                
                # 4. Делим на flat (если есть)
                if master_flat is not None:
                    # Проверяем что flat не содержит нулей
                    if np.any(master_flat.data <= 0):
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
                    
                    self.app.log_command(f"  - Применен Master Flat")
                else:
                    self.app.log_command(f"  - Master Flat: нет")
                
                # 5. Убираем отрицательные значения (после вычитаний могут появиться)
                calibrated.data = np.clip(calibrated.data, 0, None)
                
                # 6. Создаем чистый CCDData без маски и неопределенности
                clean_data = calibrated.data
                
                # Создаем новый CCDData только с данными и заголовком
                clean_ccd = CCDData(
                    data=clean_data,
                    unit=calibrated.unit,
                    header=calibrated.header.copy()  # Копируем заголовок
                )
                
                # 7. Добавляем информацию о калибровке
                self._add_calibration_metadata(clean_ccd, master_bias, master_dark, master_flat)
                
                # 8. Добавляем проверку целостности (если модуль доступен)
                if INTEGRITY_CHECKER_AVAILABLE:
                    try:
                        IntegrityChecker.add_integrity_info(
                            clean_ccd.header,
                            clean_ccd.data,
                            software_name="AstroCalibratorCH",
                            proc_version="1.0"
                        )
                        # Логируем короткую версию хэша
                        if 'DATACHECK' in clean_ccd.header:
                            short_hash = clean_ccd.header['DATACHECK'][:16]
                            self.app.log_command(f"  - Хэш данных: {short_hash}...")
                    except Exception as e:
                        self.app.log_command(f"  - Предупреждение: ошибка при добавлении хэша: {str(e)}")
                else:
                    # Добавляем базовую информацию о создании
                    import datetime
                    creation_time = datetime.datetime.utcnow().isoformat(timespec='seconds')
                    clean_ccd.header['CREATED'] = (creation_time, 'UTC time of file creation')
                    clean_ccd.header['SOFTWARE'] = ('AstroCalibratorCH', 'Software used for calibration')
                
                calibrated_lights.append(clean_ccd)
                self.app.log_command(f"  Успешно калиброван")
                self.app.log_command("")
                
            except Exception as e:
                error_msg = f"Ошибка калибровки {os.path.basename(light_path)}: {str(e)}"
                self.app.log_command(f"  ОШИБКА: {error_msg}")
                raise Exception(error_msg)
        
        self.app.log_command(f"Калибровка завершена: {len(calibrated_lights)} из {len(lights)} кадров")
                
        return calibrated_lights
    
    def _add_calibration_metadata(self, ccd_data, master_bias, master_dark, master_flat):
        """Добавляет метаданные о калибровке в заголовок"""
        # Добавляем ASCII-совместимые комментарии в заголовок
        ccd_data.header['HISTORY'] = 'Calibration: bias, dark, flat correction'
        if master_bias is not None:
            bias_count = len(self.app.bias) if hasattr(self.app, 'bias') else '?'
            ccd_data.header['HISTORY'] = f'Master Bias: {bias_count} frames'
        if master_dark is not None:
            dark_count = len(self.app.darks) if hasattr(self.app, 'darks') else '?'
            ccd_data.header['HISTORY'] = f'Master Dark: {dark_count} frames'
        if master_flat is not None:
            flat_count = len(self.app.flats) if hasattr(self.app, 'flats') else '?'
            ccd_data.header['HISTORY'] = f'Master Flat: {flat_count} frames'
        
        # Добавляем информацию о калибровке в ASCII-формате
        cal_status = ""
        if master_bias is not None:
            cal_status += "B"
        if master_dark is not None:
            cal_status += "D"
        if master_flat is not None:
            cal_status += "F"
        ccd_data.header['CALSTAT'] = (cal_status, 'Calibration applied')
    
    def verify_calibrated_image(self, filepath):
        """Проверяет целостность калиброванного изображения"""
        if not INTEGRITY_CHECKER_AVAILABLE:
            self.app.log_command(f"Ошибка: модуль проверки целостности не доступен")
            return None
        
        try:
            result = IntegrityChecker.verify_file_integrity(filepath, verbose=False)
            
            if result['error']:
                self.app.log_command(f"Ошибка проверки: {result['error']}")
                return None
            
            filename = os.path.basename(filepath)
            
            if result['is_valid'] is None:
                self.app.log_command(f"Файл {filename}: проверка целостности невозможна (нет хэша)")
                return None
            elif result['is_valid']:
                self.app.log_command(f"Файл {filename}: целостность данных сохранена ✓")
                return True
            else:
                self.app.log_command(f"Файл {filename}: целостность данных НАРУШЕНА! ✗")
                self.app.log_command(f"  Ожидался хэш: {result['stored_hash']}")
                self.app.log_command(f"  Получен хэш: {result['current_hash']}")
                return False
                
        except Exception as e:
            self.app.log_command(f"Ошибка при проверке файла {filepath}: {str(e)}")
            return None
    
    def calibrate_without_flat(self, lights, master_bias, master_dark):
        """Калибровка БЕЗ flat (для тестирования)"""
        self.app.log_command(f"Тестовая калибровка БЕЗ Flat")
        self.app.log_command("")
        
        return self.calibrate_lights(lights, master_bias, master_dark, None)