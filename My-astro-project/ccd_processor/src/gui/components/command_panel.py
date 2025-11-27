"""
Панель команд
"""

import tkinter as tk
from tkinter import ttk
from ..widgets.readonly_text import ReadonlyText

class CommandPanel:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.setup_ui()
        
    def setup_ui(self):
        """Создание панели команд"""
        self.frame = ttk.LabelFrame(self.parent, text="Команды")
        self.frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
        
        self._create_command_text()
        self._create_clear_button()
        
    def _create_command_text(self):
        """Создание текстового поля для команд"""
        self.command_text = ReadonlyText(
            self.frame, 
            width=40, 
            height=30,
            font=('Consolas', 10),
            bg='black',
            fg='white'
        )
        self.command_text.pack(fill=tk.BOTH, expand=True)
        
    def _create_clear_button(self):
        """Создание кнопки очистки"""
        clear_button = ttk.Button(self.frame, text="Очистить", command=self.clear_commands)
        clear_button.pack(fill=tk.X, pady=5)
        
    def log_command(self, message):
        """Добавление сообщения в лог"""
        self.command_text.config(state=tk.NORMAL)
        self.command_text.insert(tk.END, f"> {message}\n")
        self.command_text.see(tk.END)
        self.command_text.config(state=tk.DISABLED)
        
    def clear_commands(self):
        """Очистка командной панели"""
        self.command_text.config(state=tk.NORMAL)
        self.command_text.delete(1.0, tk.END)
        self.command_text.config(state=tk.DISABLED)
        self.log_command("Командная панель очищена")