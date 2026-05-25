import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime


class RandomTaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Файл для сохранения истории
        self.history_file = "task_history.json"
        
        # Предопределённые задачи с типами
        self.predefined_tasks = [
            {"task": "Прочитать статью по Python", "type": "учёба"},
            {"task": "Решить 5 задач на LeetCode", "type": "учёба"},
            {"task": "Прочитать главу технической книги", "type": "учёба"},
            {"task": "Сделать зарядку 15 минут", "type": "спорт"},
            {"task": "Пробежать 3 км", "type": "спорт"},
            {"task": "Сделать 20 отжиманий", "type": "спорт"},
            {"task": "Написать отчёт по проекту", "type": "работа"},
            {"task": "Ответить на рабочие письма", "type": "работа"},
            {"task": "Подготовить презентацию", "type": "работа"},
            {"task": "Сделать 10-минутную медитацию", "type": "спорт"},
            {"task": "Посмотреть обучающее видео", "type": "учёба"},
            {"task": "Провести код-ревью", "type": "работа"},
        ]
        
        # История сгенерированных задач
        self.history = []
        
        # Загружаем историю из файла
        self.load_history()
        
        # Создаём интерфейс
        self.create_widgets()
        self.update_history_list()
    
    def create_widgets(self):
        # === Заголовок ===
        title_label = tk.Label(
            self.root, 
            text="🎲 Random Task Generator", 
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=10)
        
        # === Фрейм генерации задачи ===
        gen_frame = tk.LabelFrame(self.root, text="Генерация задачи", padx=10, pady=10)
        gen_frame.pack(padx=15, pady=5, fill="x")
        
        # Кнопка генерации
        self.generate_btn = tk.Button(
            gen_frame,
            text="🎲 Сгенерировать задачу",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            command=self.generate_task
        )
        self.generate_btn.pack(pady=5, fill="x")
        
        # Отображение текущей задачи
        self.current_task_var = tk.StringVar(value="Нажмите кнопку для генерации...")
        self.current_task_label = tk.Label(
            gen_frame,
            textvariable=self.current_task_var,
            font=("Arial", 11),
            wraplength=500,
            fg="#333"
        )
        self.current_task_label.pack(pady=5)
        
        # Тип задачи
        self.current_type_var = tk.StringVar(value="")
        self.current_type_label = tk.Label(
            gen_frame,
            textvariable=self.current_type_var,
            font=("Arial", 10, "italic"),
            fg="#666"
        )
        self.current_type_label.pack()
        
        # === Фрейм добавления новой задачи ===
        add_frame = tk.LabelFrame(self.root, text="Добавить новую задачу", padx=10, pady=10)
        add_frame.pack(padx=15, pady=5, fill="x")
        
        # Поле ввода задачи
        tk.Label(add_frame, text="Задача:").grid(row=0, column=0, sticky="w")
        self.new_task_entry = tk.Entry(add_frame, width=40)
        self.new_task_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # Выбор типа
        tk.Label(add_frame, text="Тип:").grid(row=1, column=0, sticky="w")
        self.task_type_var = tk.StringVar(value="учёба")
        type_combo = ttk.Combobox(
            add_frame, 
            textvariable=self.task_type_var,
            values=["учёба", "спорт", "работа"],
            state="readonly",
            width=37
        )
        type_combo.grid(row=1, column=1, padx=5, pady=2)
        
        # Кнопка добавления
        add_btn = tk.Button(
            add_frame,
            text="➕ Добавить задачу",
            command=self.add_new_task
        )
        add_btn.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
        
        # === Фрейм фильтрации ===
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация истории", padx=10, pady=10)
        filter_frame.pack(padx=15, pady=5, fill="x")
        
        tk.Label(filter_frame, text="Показать:").pack(side="left")
        
        self.filter_var = tk.StringVar(value="все")
        filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=["все", "учёба", "спорт", "работа"],
            state="readonly",
            width=15
        )
        filter_combo.pack(side="left", padx=5)
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self.update_history_list())
        
        # === Фрейм истории ===
        history_frame = tk.LabelFrame(self.root, text="История задач", padx=10, pady=10)
        history_frame.pack(padx=15, pady=5, fill="both", expand=True)
        
        # Список истории с прокруткой
        scrollbar = tk.Scrollbar(history_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.history_listbox = tk.Listbox(
            history_frame,
            yscrollcommand=scrollbar.set,
            font=("Arial", 10),
            height=12
        )
        self.history_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.history_listbox.yview)
        
        # Кнопки управления историей
        btn_frame = tk.Frame(history_frame)
        btn_frame.pack(fill="x", pady=5)
        
        clear_btn = tk.Button(
            btn_frame,
            text="🗑️ Очистить историю",
            command=self.clear_history
        )
        clear_btn.pack(side="left", padx=2)
        
        save_btn = tk.Button(
            btn_frame,
            text="💾 Сохранить в JSON",
            command=self.save_history
        )
        save_btn.pack(side="left", padx=2)
        
        # Статус бар
        self.status_var = tk.StringVar(value="Готово к работе")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            bd=1,
            relief=tk.SUNKEN,
            anchor="w"
        )
        status_bar.pack(side="bottom", fill="x")
    
    def generate_task(self):
        """Генерирует случайную задачу из списка"""
        if not self.predefined_tasks:
            messagebox.showwarning("Ошибка", "Список задач пуст!")
            return
        
        # Выбираем случайную задачу
        task_data = random.choice(self.predefined_tasks)
        
        # Обновляем отображение
        self.current_task_var.set(f"📋 {task_data['task']}")
        self.current_type_var.set(f"Категория: {task_data['type']}")
        
        # Добавляем в историю
        history_entry = {
            "task": task_data['task'],
            "type": task_data['type'],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(history_entry)
        
        # Автосохранение
        self.save_history()
        self.update_history_list()
        
        self.status_var.set(f"Сгенерирована задача: {task_data['task'][:30]}...")
    
    def add_new_task(self):
        """Добавляет новую задачу в список с проверкой ввода"""
        task_text = self.new_task_entry.get().strip()
        task_type = self.task_type_var.get()
        
        # Проверка на пустую строку
        if not task_text:
            messagebox.showerror(
                "Ошибка ввода", 
                "Название задачи не может быть пустым!\nВведите текст задачи."
            )
            return
        
        # Проверка на дубликат
        for existing in self.predefined_tasks:
            if existing['task'].lower() == task_text.lower():
                messagebox.showwarning(
                    "Дубликат",
                    "Такая задача уже существует в списке!"
                )
                return
        
        # Добавляем задачу
        new_task = {
            "task": task_text,
            "type": task_type
        }
        self.predefined_tasks.append(new_task)
        
        # Очищаем поле ввода
        self.new_task_entry.delete(0, tk.END)
        
        messagebox.showinfo(
            "Успех",
            f"Задача '{task_text}' добавлена в категорию '{task_type}'!"
        )
        self.status_var.set(f"Добавлена новая задача: {task_text[:30]}...")
    
    def update_history_list(self):
        """Обновляет отображение истории с учётом фильтра"""
        self.history_listbox.delete(0, tk.END)
        
        filter_type = self.filter_var.get()
        
        filtered_history = self.history
        if filter_type != "все":
            filtered_history = [
                entry for entry in self.history 
                if entry['type'] == filter_type
            ]
        
        if not filtered_history:
            self.history_listbox.insert(tk.END, "История пуста")
            return
        
        # Отображаем в обратном порядке (новые сверху)
        for entry in reversed(filtered_history):
            display_text = f"[{entry['timestamp']}] [{entry['type']}] {entry['task']}"
            self.history_listbox.insert(tk.END, display_text)
    
    def save_history(self):
        """Сохраняет историю в JSON файл"""
        try:
            data = {
                "history": self.history,
                "predefined_tasks": self.predefined_tasks
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.status_var.set("История сохранена в JSON")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))
    
    def load_history(self):
        """Загружает историю из JSON файла"""
        if not os.path.exists(self.history_file):
            return
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.history = data.get("history", [])
                loaded_tasks = data.get("predefined_tasks", [])
                
                # Объединяем предопределённые и загруженные задачи
                if loaded_tasks:
                    # Избегаем дубликатов
                    existing_tasks = {t['task'] for t in self.predefined_tasks}
                    for task in loaded_tasks:
                        if task['task'] not in existing_tasks:
                            self.predefined_tasks.append(task)
                            
            self.status_var.set("История загружена из JSON")
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", str(e))
    
    def clear_history(self):
        """Очищает историю"""
        if not self.history:
            return
            
        if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
            self.history = []
            self.save_history()
            self.update_history_list()
            self.status_var.set("История очищена")


def main():
    root = tk.Tk()
    app = RandomTaskGenerator(root)
    root.mainloop()


if __name__ == "__main__":
    main()