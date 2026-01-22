"""
Создание мастер-кадров
"""

import ccdproc
import numpy as np
from astropy.nddata import CCDData
from astropy.stats import mad_std

class MastersProcessor:
    def __init__(self, app):
        self.app = app
        
    def create_master_bias(self, bias_files):
        """Создание мастер bias"""
        if not bias_files:
            raise ValueError("Нет bias кадров для обработки")
            
        bias_list = [self.app.read_fits_with_unit(f) for f in bias_files]

        master_bias = ccdproc.combine(bias_list,
            method='average',
            sigma_clip=True, 
            sigma_clip_low_thresh=5, 
            sigma_clip_high_thresh=5,
            sigma_clip_func=np.ma.median, 
            sigma_clip_dev_func=mad_std,
            mem_limit=360e6,
            unit='adu'
        )
        
        return master_bias
        
    def create_master_dark(self, dark_files, master_bias=None):
        """Создание мастер dark"""
        if not dark_files:
            raise ValueError("Нет dark кадров для обработки")
            
        dark_list = [self.app.read_fits_with_unit(f) for f in dark_files]
        
        # Вычитание bias если есть
        if master_bias:
            dark_list = [ccdproc.subtract_bias(dark, master_bias) for dark in dark_list]
            
        master_dark = ccdproc.combine(dark_list,
            method='average',
            sigma_clip=True, 
            sigma_clip_low_thresh=5, 
            sigma_clip_high_thresh=5,
            sigma_clip_func=np.ma.median, 
            sigma_clip_dev_func=mad_std,
            mem_limit=360e6,
            unit='adu'
        )
        
        return master_dark
        
    def create_master_flat(self, flat_files, master_bias=None):
        """Создание мастер flat"""
        if not flat_files:
            raise ValueError("Нет flat кадров для обработки")
            
        flat_list = [self.app.read_fits_with_unit(f) for f in flat_files]
        
        # Вычитание bias если есть
        if master_bias:
            flat_list = [ccdproc.subtract_bias(flat, master_bias) for flat in flat_list]
            
        # Нормализация
        normalized_flats = []
        for flat in flat_list:
            # Простая нормализация по медиане
            normalized_data = flat.data / np.median(flat.data)
            # Создаем новый CCDData с тем же unit
            normalized_flat = CCDData(normalized_data, unit=flat.unit)
            normalized_flats.append(normalized_flat)
            
        master_flat = ccdproc.combine(
            normalized_flats,
            method='median',
            sigma_clip=True,
            sigma_clip_low_thresh=3,
            sigma_clip_high_thresh=3
        )
        
        return master_flat