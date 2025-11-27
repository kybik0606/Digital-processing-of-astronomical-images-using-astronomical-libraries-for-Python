#!/usr/bin/env python3
"""
Точка входа в приложение CCD Processor
"""

import sys
import os

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import CCDProcessorApp

if __name__ == "__main__":
    app = CCDProcessorApp()
    app.run()