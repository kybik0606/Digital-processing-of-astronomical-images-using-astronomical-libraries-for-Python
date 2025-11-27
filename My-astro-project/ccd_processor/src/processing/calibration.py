"""
Функции калибровки изображений
"""

import ccdproc
import astropy.units as u
import os
import re

class CalibrationProcessor:
    def __init__(self, config):
        self.config = config
        
    def calibrate_lights(self, lights, master_bias, master_dark, master_flat):
        """Калибровка light кадров"""
        calibrated_lights = []
        
        for light_path in lights:
            try:
                light = self.config.read_fits_with_unit(light_path)
                calibrated = light.copy()
                
                # Применение калибровки
                if master_bias:
                    calibrated = ccdproc.subtract_bias(calibrated, master_bias)
                    
                if master_dark:
                    light_exposure = self.get_exposure_time(light)
                    dark_exposure = self.get_exposure_time(master_dark)
                    
                    calibrated = ccdproc.subtract_dark(
                        calibrated, master_dark,
                        dark_exposure=dark_exposure,
                        data_exposure=light_exposure,
                        exposure_time=None,
                        exposure_unit=u.second,
                        scale=False
                    )
                    
                if master_flat:
                    calibrated = ccdproc.flat_correct(calibrated, master_flat)
                    
                calibrated_lights.append(calibrated)
                
            except Exception as e:
                raise Exception(f"Ошибка калибровки {os.path.basename(light_path)}: {str(e)}")
                
        return calibrated_lights
        
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
                    
            # Анализ имени файла
            if hasattr(ccd_data, 'file_path'):
                filename = os.path.basename(ccd_data.file_path)
                match = re.search(r'(\d+\.?\d*)[sS]', filename)
                if match:
                    return float(match.group(1)) * u.second
                    
            return 1.0 * u.second
            
        except Exception:
            return 1.0 * u.second