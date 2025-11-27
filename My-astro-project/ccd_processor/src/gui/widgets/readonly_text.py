"""
Кастомный текстовый виджет только для чтения с поддержкой копирования
"""

import tkinter as tk
from tkinter import scrolledtext

class ReadonlyText(scrolledtext.ScrolledText):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(state=tk.DISABLED)
        
        # Контекстное меню
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Копировать", command=self.copy_text)
        self.context_menu.add_command(label="Выделить все", command=self.select_all)
        
        # Привязки событий
        self.bind("<Button-3>", self.show_context_menu)
        self.bind("<Control-a>", self.select_all)
        self.bind("<Control-A>", self.select_all)
        
    def show_context_menu(self, event):
        """Показать контекстное меню"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def copy_text(self):
        """Копировать выделенный текст"""
        try:
            self.config(state=tk.NORMAL)
            text = self.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(text)
            self.config(state=tk.DISABLED)
        except tk.TclError:
            pass
    
    def select_all(self, event=None):
        """Выделить весь текст"""
        self.config(state=tk.NORMAL)
        self.tag_add(tk.SEL, "1.0", tk.END)
        self.mark_set(tk.INSERT, "1.0")
        self.see(tk.INSERT)
        self.config(state=tk.DISABLED)
        return "break"