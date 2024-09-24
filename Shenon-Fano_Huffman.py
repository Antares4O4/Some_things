import tkinter as tk
from tkinter import filedialog, messagebox, StringVar, OptionMenu, Entry
from collections import Counter
import heapq
import os
import pickle

# Узел дерева Хаффмана
class Node:
    def __init__(self, char, freq):
        self.char = char  # Символ
        self.freq = freq  # Частота символа
        self.left = None  # Левый дочерний узел
        self.right = None  # Правый дочерний узел

    def __lt__(self, other):
        # Определение порядка для элементов в куче (по частоте)
        return self.freq < other.freq

# Построение дерева Хаффмана
def build_huffman_tree(text):
    frequency = Counter(text)  # Подсчет частоты символов
    # Создание узлов для каждого символа
    heap = [Node(char, freq) for char, freq in frequency.items()]
    heapq.heapify(heap)  # Преобразование списка в кучу

    # Построение дерева
    while len(heap) > 1:
        left = heapq.heappop(heap)  # Извлечение узла с минимальной частотой
        right = heapq.heappop(heap)  # Извлечение следующего узла
        merged = Node(None, left.freq + right.freq)  # Создание нового узла
        merged.left = left  # Присоединение левого узла
        merged.right = right  # Присоединение правого узла
        heapq.heappush(heap, merged)  # Вставка нового узла обратно в кучу

    return heap[0]  # Возврат корня дерева

# Генерация кодов Хаффмана
def generate_huffman_codes(node, current_code="", codes={}):
    if node is None:
        return
    if node.char is not None:
        codes[node.char] = current_code  # Присвоение кода символу
    # Рекурсивный вызов для левого и правого дочерних узлов
    generate_huffman_codes(node.left, current_code + "0", codes)
    generate_huffman_codes(node.right, current_code + "1", codes)
    return codes

# Кодирование Хаффмана
def huffman_encode(text):
    root = build_huffman_tree(text)  # Построение дерева
    huffman_codes = generate_huffman_codes(root)  # Генерация кодов
    # Кодирование текста с использованием сгенерированных кодов
    encoded_text = ''.join([huffman_codes[char] for char in text])
    return encoded_text, root  # Возврат закодированного текста и корня дерева

# Декодирование Хаффмана
def huffman_decode(encoded_text, root):
    decoded_text = []  # Список для хранения декодированных символов
    node = root  # Начало с корня дерева
    for bit in encoded_text:
        # Переход по дереву в зависимости от бита
        node = node.left if bit == '0' else node.right
        if node.char is not None:  # Если достигли символа
            decoded_text.append(node.char)  # Добавление символа в декодированный текст
            node = root  # Возврат к корню
    return ''.join(decoded_text)  # Возврат декодированного текста

# Шеннон-Фано
def shannon_fano_encode(frequency):
    if len(frequency) == 1:
        return {list(frequency.keys())[0]: ""}  # Базовый случай
    # Сортировка частот
    sorted_freq = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
    total = sum(freq for _, freq in sorted_freq)  # Общая частота
    split_idx, running_sum = 0, 0
    # Определение точки разделения
    for i, (_, freq) in enumerate(sorted_freq):
        running_sum += freq
        if running_sum >= total / 2:
            split_idx = i
            break
    left_half = dict(sorted_freq[:split_idx + 1])  # Левая половина
    right_half = dict(sorted_freq[split_idx + 1:])  # Правая половина
    left_codes = shannon_fano_encode(left_half)  # Рекурсивный вызов для левой половины
    right_codes = shannon_fano_encode(right_half)  # Рекурсивный вызов для правой половины
    # Добавление префиксов
    for char in left_codes:
        left_codes[char] = '0' + left_codes[char]
    for char in right_codes:
        right_codes[char] = '1' + right_codes[char]
    left_codes.update(right_codes)  # Объединение кодов
    return left_codes

# Кодирование Шеннон-Фано
def shannon_fano(text):
    frequency = Counter(text)  # Подсчет частоты символов
    codes = shannon_fano_encode(frequency)  # Генерация кодов
    encoded_text = ''.join([codes[char] for char in text])  # Кодирование текста
    return encoded_text, codes  # Возврат закодированного текста и кодов

# Декодирование Шеннон-Фано
def shannon_fano_decode(encoded_text, codes):
    reversed_codes = {v: k for k, v in codes.items()}  # Реверсирование кодов
    current_code = ""
    decoded_text = []  # Список для хранения декодированных символов
    for bit in encoded_text:
        current_code += bit  # Построение текущего кода
        if current_code in reversed_codes:  # Если код найден
            decoded_text.append(reversed_codes[current_code])  # Добавление символа
            current_code = ""  # Сброс текущего кода
    return ''.join(decoded_text)  # Возврат декодированного текста

# GUI приложение
class EncoderApp:
    def __init__(self, root):
        self.root = root  # Основное окно приложения
        self.root.title("Кодировщик файлов")  # Заголовок окна
        self.root.geometry("600x500")  # Размеры окна

        # Переменные для хранения значений
        self.filename_var = StringVar()
        self.tree_filename_var = StringVar()
        self.codes_filename_var = StringVar()
        self.selected_algorithm = StringVar(value="Хаффман")  # Алгоритм по умолчанию
        self.selected_action = StringVar(value="Кодировать")  # Действие по умолчанию

        # Создание элементов интерфейса
        self.create_widgets()

    def create_widgets(self):
        # Поле для ввода пути к файлу и кнопка выбора
        tk.Label(self.root, text="Выберите или введите путь к файлу", anchor='w').pack(pady=(10, 0), anchor='w', padx=10)
        file_entry = Entry(self.root, textvariable=self.filename_var, width=50)
        file_entry.pack(pady=5, anchor='w', padx=10)
        tk.Button(self.root, text="Обзор", command=self.choose_file).pack(pady=(0, 10), anchor='w', padx=10)

        # Поле для ввода пути к файлу дерева и кнопка выбора
        tk.Label(self.root, text="Выберите или введите путь к файлу дерева Хаффмана", anchor='w').pack(pady=(10, 0),
                                                                                                       anchor='w', padx=10)
        tree_entry = Entry(self.root, textvariable=self.tree_filename_var, width=50)
        tree_entry.pack(pady=5, anchor='w', padx=10)
        tk.Button(self.root, text="Обзор", command=self.choose_tree_file).pack(pady=(0, 10), anchor='w', padx=10)

        # Поле для ввода пути к файлу кодов Шеннон-Фано и кнопка выбора
        tk.Label(self.root, text="Выберите или введите путь к файлу кодов Шеннон-Фано", anchor='w').pack(pady=(10, 0),
                                                                                                         anchor='w', padx=10)
        codes_entry = Entry(self.root, textvariable=self.codes_filename_var, width=50)
        codes_entry.pack(pady=5, anchor='w', padx=10)
        tk.Button(self.root, text="Обзор", command=self.choose_codes_file).pack(pady=(0, 10), anchor='w', padx=10)

        # Выбор алгоритма через выпадающий список
        tk.Label(self.root, text="Выберите алгоритм", anchor='w').pack(pady=(10, 0), anchor='w', padx=10)
        algorithm_options = ["Хаффман", "Шеннон-Фано"]
        OptionMenu(self.root, self.selected_algorithm, *algorithm_options).pack(pady=(0, 10), anchor='w', padx=10)

        # Выбор действия через выпадающий список
        tk.Label(self.root, text="Выберите действие", anchor='w').pack(pady=(10, 0), anchor='w', padx=10)
        action_options = ["Кодировать", "Декодировать"]
        OptionMenu(self.root, self.selected_action, *action_options).pack(pady=(0, 10), anchor='w', padx=10)

        # Кнопка выполнения по центру внизу
        tk.Button(self.root, text="Выполнить", command=self.perform_action, borderwidth=2, highlightbackground="blue",
                  highlightcolor="blue").pack(ipadx=270, ipady=20, side='bottom', anchor='center')

    # Метод для выбора файла
    def choose_file(self):
        self.filename_var.set(filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("Encoded files", "*.huffman *.shannon-fano *.encoded")]))  # Открытие диалогового окна для выбора файла

    # Метод для выбора файла дерева Хаффмана
    def choose_tree_file(self):
        self.tree_filename_var.set(filedialog.askopenfilename(filetypes=[("Huffman Tree Files", "*.pkl")]))  # Открытие диалогового окна для выбора файла дерева

    # Метод для выбора файла кодов Шеннон-Фано
    def choose_codes_file(self):
        self.codes_filename_var.set(filedialog.askopenfilename(filetypes=[("Shannon-Fano Code Files", "*.pkl")]))  # Открытие диалогового окна для выбора файла кодов

    # Метод для выполнения действия (кодирование/декодирование)
    def perform_action(self):
        filename = self.filename_var.get()  # Получение пути к файлу
        tree_filename = self.tree_filename_var.get()  # Получение пути к файлу дерева
        codes_filename = self.codes_filename_var.get()  # Получение пути к файлу кодов

        if not filename:
            messagebox.showwarning("Ошибка", "Пожалуйста, выберите или введите путь к файлу")  # Проверка выбора файла
            return

        with open(filename, 'r', encoding='utf-8') as file:
            text = file.read()  # Чтение содержимого файла

        algorithm = self.selected_algorithm.get()  # Получение выбранного алгоритма
        action = self.selected_action.get()  # Получение выбранного действия

        # Получаем путь к файлу и его расширение
        base_name, file_extension = os.path.splitext(filename)  # Разделение имени файла и расширения

        if action == "Кодировать":
            if algorithm == "Хаффман":
                # Кодирование текста с использованием алгоритма Хаффмана
                encoded_text, tree = huffman_encode(text)
                output_file = f"{base_name}_huffman_encoded{file_extension}"  # Формирование имени выходного файла
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(encoded_text)  # Запись закодированного текста в файл
                # Сохранение дерева Хаффмана в файл
                tree_file_name = f"{base_name}_huffman_tree.pkl"
                with open(tree_file_name, 'wb') as tree_file:
                    pickle.dump(tree, tree_file)  # Сериализация дерева в файл
                messagebox.showinfo("Успех",
                                    f"Файл закодирован как {output_file}\nДерево Хаффмана сохранено как {tree_file_name}")

            elif algorithm == "Шеннон-Фано":
                # Кодирование текста с использованием алгоритма Шеннон-Фано
                encoded_text, codes = shannon_fano(text)
                output_file = f"{base_name}_shannon-fano_encoded{file_extension}"  # Формирование имени выходного файла
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(encoded_text)  # Запись закодированного текста в файл
                # Сохранение кодов Шеннон-Фано в файл
                codes_file_name = f"{base_name}_shannon-fano_codes.pkl"
                with open(codes_file_name, 'wb') as codes_file:
                    pickle.dump(codes, codes_file)  # Сериализация кодов в файл
                messagebox.showinfo("Успех",
                                    f"Файл закодирован как {output_file}\nКоды Шеннон-Фано сохранены как {codes_file_name}")

        elif action == "Декодировать":
            if algorithm == "Хаффман":
                if not tree_filename:
                    messagebox.showwarning("Ошибка", "Пожалуйста, выберите файл дерева Хаффмана")  # Проверка выбора файла дерева
                    return
                try:
                    with open(tree_filename, 'rb') as tree_file:
                        tree = pickle.load(tree_file)  # Десериализация дерева из файла
                    decoded_text = huffman_decode(text, tree)  # Декодирование текста
                    output_file = f"{base_name}_huffman_decoded{file_extension}"  # Формирование имени выходного файла
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(decoded_text)  # Запись декодированного текста в файл
                    messagebox.showinfo("Успех", f"Файл декодирован как {output_file}")
                except FileNotFoundError:
                    messagebox.showerror("Ошибка", f"Файл дерева Хаффмана не найден: {tree_filename}")  # Обработка ошибки

            elif algorithm == "Шеннон-Фано":
                if not codes_filename:
                    messagebox.showwarning("Ошибка", "Пожалуйста, выберите файл кодов Шеннон-Фано")  # Проверка выбора файла кодов
                    return
                try:
                    with open(codes_filename, 'rb') as codes_file:
                        codes = pickle.load(codes_file)  # Десериализация кодов из файла
                    decoded_text = shannon_fano_decode(text, codes)  # Декодирование текста
                    output_file = f"{base_name}_shannon-fano_decoded{file_extension}"  # Формирование имени выходного файла
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(decoded_text)  # Запись декодированного текста в файл
                    messagebox.showinfo("Успех", f"Файл декодирован как {output_file}")
                except FileNotFoundError:
                    messagebox.showerror("Ошибка", f"Файл кодов Шеннон-Фано не найден: {codes_filename}")  # Обработка ошибки

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()  # Создание основного окна приложения
    app = EncoderApp(root)  # Инициализация приложения
    root.mainloop()  # Запуск основного цикла обработки событий
