"""
Вспомогательные функции
"""

import os
from astropy.nddata import CCDData

def read_fits_with_unit(file_path, unit='adu'):
    """Чтение FITS файла с указанием unit"""
    try:
        ccd = CCDData.read(file_path, unit=unit)
        ccd.file_path = file_path  # Сохраняем путь для извлечения метаданных
        return ccd
    except Exception as e:
        raise Exception(f"Ошибка чтения {file_path}: {str(e)}")

def get_filename_without_extenstion(filepath):
    """Получение имени файла без расширения"""
    return os.path.splitext(os.path.basename(filepath))[0]

def ensure_directory_exists(directory):
    """Создание директории если не существует"""
    os.makedirs(directory, exist_ok=True)