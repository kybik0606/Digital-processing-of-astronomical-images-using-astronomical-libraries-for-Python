"""
Модуль для проверки целостности FITS изображений
"""

import hashlib
import datetime
import numpy as np
from astropy.io import fits
import os

class IntegrityChecker:
    """Класс для работы с проверкой целостности данных"""
    
    @staticmethod
    def calculate_data_hash(data):
        """
        Вычисляет хэш SHA-256 для данных массива
        
        Parameters:
        -----------
        data : numpy.ndarray
            Массив данных изображения
            
        Returns:
        --------
        str
            SHA-256 хэш в виде шестнадцатеричной строки
        """
        try:
            # Преобразуем данные в байты и вычисляем хэш
            data_bytes = data.tobytes()
            return hashlib.sha256(data_bytes).hexdigest()
        except Exception as e:
            raise ValueError(f"Ошибка вычисления хэша: {str(e)}")
    
    @staticmethod
    def calculate_pixel_sum(data):
        """
        Вычисляет сумму всех пикселей
        
        Parameters:
        -----------
        data : numpy.ndarray
            Массив данных изображения
            
        Returns:
        --------
        float
            Сумма всех значений пикселей
        """
        return float(np.sum(data))
    
    @staticmethod
    def add_integrity_info(header, data, software_name="AstroCalibratorCH", proc_version="1.0"):
        """
        Добавляет информацию о целостности в заголовок FITS
        
        Parameters:
        -----------
        header : astropy.io.fits.Header
            Заголовок FITS файла
        data : numpy.ndarray
            Массив данных изображения
        software_name : str
            Название программного обеспечения
        proc_version : str
            Версия обработки
            
        Returns:
        --------
        astropy.io.fits.Header
            Обновленный заголовок
        """
        try:
            # Вычисляем хэш данных
            data_hash = IntegrityChecker.calculate_data_hash(data)
            
            # Добавляем хэш в заголовок (первые 32 символа для компактности)
            header['DATACHECK'] = (data_hash[:32], 'SHA-256 first 32 chars hash')
            
            # Добавляем полный хэш в комментарий
            header['HISTORY'] = f'Data SHA-256: {data_hash}'
            
            # Добавляем сумму пикселей
            pixel_sum = IntegrityChecker.calculate_pixel_sum(data)
            header['PIXSUM'] = (f"{pixel_sum:.2f}", 'Sum of all pixel values')
            
            # Добавляем информацию о создании
            creation_time = datetime.datetime.utcnow().isoformat(timespec='seconds')
            header['CREATED'] = (creation_time, 'UTC time of file creation')
            
            # Информация о программе
            header['SOFTWARE'] = (software_name, 'Software used for processing')
            header['PROCVERS'] = (proc_version, 'Processing version')
            
            # Статистика данных для быстрой проверки
            header['DATAMIN'] = (f"{np.min(data):.2f}", 'Minimum pixel value')
            header['DATAMAX'] = (f"{np.max(data):.2f}", 'Maximum pixel value')
            header['DATAMEAN'] = (f"{np.mean(data):.2f}", 'Mean pixel value')
            
            return header
            
        except Exception as e:
            raise RuntimeError(f"Ошибка добавления информации о целостности: {str(e)}")
    
    @staticmethod
    def verify_file_integrity(filepath, verbose=True):
        """
        Проверяет целостность FITS файла
        
        Parameters:
        -----------
        filepath : str
            Путь к FITS файлу
        verbose : bool
            Выводить подробную информацию
            
        Returns:
        --------
        dict
            Словарь с результатами проверки:
            - 'is_valid': bool (True если хэш совпадает, None если нет хэша)
            - 'stored_hash': str (сохраненный хэш)
            - 'current_hash': str (вычисленный хэш)
            - 'pixel_sum': float (сумма пикселей)
            - 'creation_time': str (время создания)
            - 'file_info': dict (информация о файле)
        """
        results = {
            'is_valid': None,
            'stored_hash': None,
            'current_hash': None,
            'pixel_sum': None,
            'creation_time': None,
            'file_info': {},
            'error': None
        }
        
        try:
            # Загружаем файл
            with fits.open(filepath) as hdul:
                header = hdul[0].header
                data = hdul[0].data
                
                # Базовая информация о файле
                filename = os.path.basename(filepath)
                results['file_info'] = {
                    'filename': filename,
                    'size': f"{os.path.getsize(filepath) / 1024:.1f} KB",
                    'dimensions': f"{data.shape[1]}x{data.shape[0]}",
                    'data_type': str(data.dtype),
                    'cal_status': header.get('CALSTAT', 'Unknown')
                }
                
                # Время создания
                results['creation_time'] = header.get('CREATED', 'Unknown')
                
                # Сумма пикселей
                if 'PIXSUM' in header:
                    results['pixel_sum'] = float(header['PIXSUM'])
                
                # Проверяем хэш, если он есть
                if 'DATACHECK' in header:
                    stored_hash = header['DATACHECK']
                    results['stored_hash'] = stored_hash
                    
                    # Вычисляем текущий хэш
                    current_hash = IntegrityChecker.calculate_data_hash(data)[:32]
                    results['current_hash'] = current_hash
                    
                    # Сравниваем хэши
                    is_valid = (stored_hash == current_hash)
                    results['is_valid'] = is_valid
                    
                    # Выводим информацию, если нужно
                    if verbose:
                        print(f"\n{'='*50}")
                        print(f"ПРОВЕРКА ЦЕЛОСТНОСТИ: {filename}")
                        print(f"{'='*50}")
                        print(f"Размер: {results['file_info']['dimensions']}")
                        print(f"Тип данных: {results['file_info']['data_type']}")
                        print(f"Статус калибровки: {results['file_info']['cal_status']}")
                        print(f"Дата создания: {results['creation_time']}")
                        print(f"Сумма пикселей: {results['pixel_sum']:.2f}")
                        print(f"\nХэш данных:")
                        print(f"  Сохраненный: {stored_hash}")
                        print(f"  Вычисленный: {current_hash}")
                        
                        if is_valid:
                            print(f"\n✓ ЦЕЛОСТНОСТЬ ДАННЫХ: СОХРАНЕНА")
                        else:
                            print(f"\n✗ ЦЕЛОСТНОСТЬ ДАННЫХ: НАРУШЕНА!")
                            print(f"  Файл был изменен после создания!")
                else:
                    results['error'] = "Хэш данных не найден в заголовке"
                    if verbose:
                        print(f"\n⚠️  Файл {filename} не содержит информации о целостности")
                        print(f"   Невозможно проверить, был ли файл изменен")
                
                return results
                
        except Exception as e:
            results['error'] = str(e)
            if verbose:
                print(f"\n❌ Ошибка при проверке файла {filepath}: {str(e)}")
            return results
    
    @staticmethod
    def verify_multiple_files(filepaths, verbose=True):
        """
        Проверяет целостность нескольких файлов
        
        Parameters:
        -----------
        filepaths : list
            Список путей к FITS файлам
        verbose : bool
            Выводить сводную информацию
            
        Returns:
        --------
        dict
            Сводная статистика по проверке
        """
        results = {
            'total_files': len(filepaths),
            'valid_files': 0,
            'invalid_files': 0,
            'no_hash_files': 0,
            'error_files': 0,
            'details': []
        }
        
        for filepath in filepaths:
            try:
                file_result = IntegrityChecker.verify_file_integrity(filepath, verbose=False)
                results['details'].append({
                    'filepath': filepath,
                    **file_result
                })
                
                if file_result['error']:
                    results['error_files'] += 1
                elif file_result['is_valid'] is None:
                    results['no_hash_files'] += 1
                elif file_result['is_valid']:
                    results['valid_files'] += 1
                else:
                    results['invalid_files'] += 1
                    
            except Exception as e:
                results['error_files'] += 1
                results['details'].append({
                    'filepath': filepath,
                    'error': str(e)
                })
        
        # Выводим сводную информацию
        if verbose:
            print(f"\n{'='*50}")
            print(f"СВОДНАЯ ИНФОРМАЦИЯ О ПРОВЕРКЕ")
            print(f"{'='*50}")
            print(f"Всего файлов: {results['total_files']}")
            print(f"✓ Целостных: {results['valid_files']}")
            print(f"✗ Нарушенных: {results['invalid_files']}")
            print(f"⚠️  Без хэша: {results['no_hash_files']}")
            print(f"❌ С ошибками: {results['error_files']}")
            
            if results['invalid_files'] > 0:
                print(f"\nФайлы с нарушенной целостностью:")
                for detail in results['details']:
                    if detail.get('is_valid') is False:
                        print(f"  - {os.path.basename(detail['filepath'])}")
        
        return results