import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator - Генератор паролей")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Файл для хранения истории
        self.history_file = "passwords_history.json"
        self.password_history = []
        
        # Загрузка истории из JSON
        self.load_history()
        
        # Параметры генерации
        self.password_length = tk.IntVar(value=12)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_special = tk.BooleanVar(value=False)
        
        # Создание интерфейса
        self.create_widgets()
        
        # Генерация первого пароля
        self.generate_password()
    
    def load_history(self):
        """Загрузка истории паролей из JSON файла"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as file:
                    self.password_history = json.load(file)
            except:
                self.password_history = []
        else:
            # Пример данных для демонстрации
            self.password_history = [
                {"password": "Pass123!", "length": 7, "date": "2026-05-06 14:30:00", 
                 "chars": "digits+letters+special"},
                {"password": "SecurePass99", "length": 11, "date": "2026-05-05 10:15:00", 
                 "chars": "digits+letters"}
            ]
    
    def save_history(self):
        """Сохранение истории паролей в JSON файл"""
        with open(self.history_file, 'w', encoding='utf-8') as file:
            json.dump(self.password_history, file, ensure_ascii=False, indent=4)
    
    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        # Главный контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Рамка настроек
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки пароля", padding="15")
        settings_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        
        # Ползунок длины пароля
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        length_control_frame = ttk.Frame(settings_frame)
        length_control_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        length_control_frame.columnconfigure(1, weight=1)
        
        self.length_scale = ttk.Scale(length_control_frame, from_=4, to=32, 
                                      variable=self.password_length, orient=tk.HORIZONTAL)
        self.length_scale.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.length_label = ttk.Label(length_control_frame, text="12", width=5)
        self.length_label.grid(row=0, column=1)
        
        # Обновление отображения длины
        self.length_scale.configure(command=self.update_length_label)
        
        # Минимальная и максимальная длина
        ttk.Label(settings_frame, text="Диапазон: 4-32 символов", 
                 foreground="gray").grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Чекбоксы
        self.digits_check = ttk.Checkbutton(settings_frame, text="Цифры (0-9)", 
                                            variable=self.use_digits)
        self.digits_check.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.letters_check = ttk.Checkbutton(settings_frame, text="Буквы (a-z, A-Z)", 
                                            variable=self.use_letters)
        self.letters_check.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        self.special_check = ttk.Checkbutton(settings_frame, text="Спецсимволы (!@#$%^&*()_+-=[]{}|;:,.<>?)", 
                                            variable=self.use_special)
        self.special_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Рамка генерации
        generate_frame = ttk.Frame(main_frame)
        generate_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        generate_frame.columnconfigure(0, weight=1)
        
        # Поле для отображения пароля
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(generate_frame, textvariable=self.password_var, 
                                       font=("Courier", 14), state="readonly")
        self.password_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Кнопка генерации
        self.generate_btn = ttk.Button(generate_frame, text="Сгенерировать пароль", 
                                       command=self.generate_password)
        self.generate_btn.grid(row=0, column=1)
        
        # Кнопка копирования
        self.copy_btn = ttk.Button(generate_frame, text="Копировать", 
                                  command=self.copy_to_clipboard)
        self.copy_btn.grid(row=0, column=2, padx=(10, 0))
        
        # Рамка истории
        history_frame = ttk.LabelFrame(main_frame, text="История паролей", padding="10")
        history_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        # Создание таблицы истории (Treeview)
        columns = ("password", "length", "date", "chars")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)
        
        # Настройка заголовков
        self.tree.heading("password", text="Пароль")
        self.tree.heading("length", text="Длина")
        self.tree.heading("date", text="Дата создания")
        self.tree.heading("chars", text="Использованные символы")
        
        # Настройка ширины колонок
        self.tree.column("password", width=200, anchor="center")
        self.tree.column("length", width=70, anchor="center")
        self.tree.column("date", width=150, anchor="center")
        self.tree.column("chars", width=250, anchor="center")
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Кнопки управления историей
        history_buttons_frame = ttk.Frame(history_frame)
        history_buttons_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        self.clear_history_btn = ttk.Button(history_buttons_frame, text="Очистить историю", 
                                           command=self.clear_history)
        self.clear_history_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_btn = ttk.Button(history_buttons_frame, text="Экспорт в JSON", 
                                    command=self.export_history)
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        # Обновление отображения истории
        self.update_history_display()
    
    def update_length_label(self, value):
        """Обновление метки длины пароля"""
        self.length_label.config(text=str(int(float(value))))
    
    def get_character_set(self):
        """Получение набора символов на основе выбранных опций"""
        characters = ""
        
        if self.use_digits.get():
            characters += string.digits
        if self.use_letters.get():
            characters += string.ascii_letters
        if self.use_special.get():
            characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        return characters
    
    def validate_settings(self):
        """Проверка корректности настроек"""
        length = self.password_length.get()
        
        # Проверка длины
        if length < 4 or length > 32:
            messagebox.showerror("Ошибка", "Длина пароля должна быть от 4 до 32 символов!")
            return False
        
        # Проверка выбора символов
        if not (self.use_digits.get() or self.use_letters.get() or self.use_special.get()):
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов!")
            return False
        
        return True
    
    def generate_password(self):
        """Генерация случайного пароля"""
        if not self.validate_settings():
            return
        
        characters = self.get_character_set()
        length = self.password_length.get()
        
        # Генерация пароля
        password = ''.join(random.choice(characters) for _ in range(length))
        
        # Обновление отображения
        self.password_var.set(password)
        
        # Сохранение в историю
        self.add_to_history(password, length)
        
        return password
    
    def add_to_history(self, password, length):
        """Добавление пароля в историю"""
        # Получение информации об использованных символах
        chars_used = []
        if self.use_digits.get():
            chars_used.append("цифры")
        if self.use_letters.get():
            chars_used.append("буквы")
        if self.use_special.get():
            chars_used.append("спецсимволы")
        
        chars_str = "+".join(chars_used)
        
        # Создание записи
        history_entry = {
            "password": password,
            "length": length,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "chars": chars_str
        }
        
        # Добавление в начало списка (новые сверху)
        self.password_history.insert(0, history_entry)
        
        # Ограничение истории (последние 50 паролей)
        if len(self.password_history) > 50:
            self.password_history = self.password_history[:50]
        
        # Сохранение в JSON
        self.save_history()
        
        # Обновление отображения
        self.update_history_display()
    
    def update_history_display(self):
        """Обновление отображения истории"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Заполнение таблицы
        for entry in self.password_history:
            self.tree.insert("", "end", values=(
                entry["password"],
                entry["length"],
                entry["date"],
                entry["chars"]
            ))
    
    def copy_to_clipboard(self):
        """Копирование пароля в буфер обмена"""
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Предупреждение", "Нет пароля для копирования!")
    
    def clear_history(self):
        """Очистка истории паролей"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.password_history = []
            self.save_history()
            self.update_history_display()
            messagebox.showinfo("Успех", "История очищена!")
    
    def export_history(self):
        """Экспорт истории в JSON файл (сохранение текущей копии)"""
        export_file = f"passwords_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(export_file, 'w', encoding='utf-8') as file:
                json.dump(self.password_history, file, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"История экспортирована в файл: {export_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать историю: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()