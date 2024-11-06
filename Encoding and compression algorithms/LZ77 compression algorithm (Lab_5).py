import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
from bitarray import bitarray

class LZ77Compressor:
    """
    Класс, реализующий алгоритм сжатия и распаковки LZ77.
    """
    MAX_WINDOW_SIZE = 400  # Максимальный размер окна для алгоритма

    def __init__(self, window_size=20):
        # Инициализируем размер окна, ограничиваем его максимальным значением
        self.window_size = min(window_size, self.MAX_WINDOW_SIZE)
        self.lookahead_buffer_size = 15  # Размер буфера предварительного просмотра

    def compress(self, input_file_path, output_file_path=None):
        """
        Метод сжатия файла с помощью алгоритма LZ77.
        """
        data = None  # Хранит прочитанные данные из файла
        i = 0  # Указатель на текущую позицию в файле
        output_buffer = bitarray(endian='big')  # Битовый массив для хранения сжатых данных

        # Чтение данных из входного файла
        try:
            with open(input_file_path, 'rb') as input_file:
                data = input_file.read()
        except IOError:
            raise IOError("Не удалось открыть файл для чтения.")

        # Основной цикл обработки данных
        while i < len(data):
            # Поиск наилучшего совпадения в окне
            match = self.find_longest_match(data, i)

            # Если найдено совпадение
            if match:
                (best_match_distance, best_match_length) = match
                output_buffer.append(True)  # Добавляем флаг наличия совпадения (1)

                # Кодируем расстояние и длину совпадения
                output_buffer.frombytes(bytes([best_match_distance >> 4]))
                output_buffer.frombytes(bytes([((best_match_distance & 0xf) << 4) | best_match_length]))
                i += best_match_length  # Перемещаем указатель вперед на длину совпадения
            else:
                # Если совпадение не найдено, добавляем символ как есть
                output_buffer.append(False)  # Добавляем флаг отсутствия совпадения (0)
                output_buffer.frombytes(bytes([data[i]]))  # Записываем байт символа
                i += 1  # Переходим к следующему символу

        output_buffer.fill()  # Заполняем оставшееся пространство нулями

        # Запись сжатых данных в файл, если указан путь
        if output_file_path:
            try:
                with open(output_file_path, 'wb') as output_file:
                    output_file.write(output_buffer.tobytes())
            except IOError:
                raise IOError("Не удалось записать файл для сохранения сжатых данных.")

    def decompress(self, input_file_path, output_file_path=None):
        """
        Метод для распаковки файла, сжатого с помощью LZ77.
        """
        data = bitarray(endian='big')  # Битовый массив для хранения входных данных
        output_buffer = []  # Буфер для распакованных данных

        # Чтение сжатых данных из файла
        try:
            with open(input_file_path, 'rb') as input_file:
                data.fromfile(input_file)
        except IOError:
            raise IOError("Не удалось открыть файл для чтения.")

        # Основной цикл обработки данных
        while len(data) >= 9:  # Минимум 9 бит для обработки (1 бит флага и 8 бит данных)

            flag = data.pop(0)  # Извлекаем флаг

            if not flag:
                # Если флаг равен 0, читаем 8 бит символа
                byte = data[:8].tobytes()  # Извлекаем байт данных
                output_buffer.append(byte)  # Добавляем в буфер вывода
                del data[:8]  # Удаляем обработанные биты
            else:
                # Если флаг равен 1, читаем расстояние и длину
                byte1 = ord(data[:8].tobytes())  # Первые 8 бит для расстояния
                byte2 = ord(data[8:16].tobytes())  # Вторые 8 бит для длины

                del data[:16]  # Удаляем обработанные биты
                distance = (byte1 << 4) | (byte2 >> 4)  # Восстанавливаем расстояние
                length = (byte2 & 0xf)  # Восстанавливаем длину

                # Добавляем в выходной буфер данные, используя найденное расстояние и длину
                for i in range(length):
                    output_buffer.append(output_buffer[-distance])

        out_data = b''.join(output_buffer)  # Собираем распакованные данные

        # Записываем распакованные данные в файл
        if output_file_path:
            try:
                with open(output_file_path, 'wb') as output_file:
                    output_file.write(out_data)
            except IOError:
                raise IOError("Не удалось записать файл для сохранения распакованных данных.")

    def find_longest_match(self, data, current_position):
        """
        Поиск самой длинной подстроки в буфере для сжатия.
        """
        end_of_buffer = min(current_position + self.lookahead_buffer_size, len(data) + 1)
        best_match_distance = -1
        best_match_length = -1

        # Перебираем возможные подстроки
        for j in range(current_position + 2, end_of_buffer):
            start_index = max(0, current_position - self.window_size)
            substring = data[current_position:j]

            # Проверяем каждое совпадение подстроки с окном
            for i in range(start_index, current_position):
                repetitions = len(substring) // (current_position - i)
                last = len(substring) % (current_position - i)
                matched_string = data[i:current_position] * repetitions + data[i:i + last]

                if matched_string == substring and len(substring) > best_match_length:
                    best_match_distance = current_position - i
                    best_match_length = len(substring)

        if best_match_distance > 0 and best_match_length > 0:
            return best_match_distance, best_match_length
        return None

class LZ77GUI:
    """
    Класс для создания графического интерфейса с использованием Tkinter.
    """
    def __init__(self, master):
        # Настройка окна
        self.master = master
        self.master.title("LZ77 Компрессия и Декомпрессия")
        self.master.geometry("400x400")
        self.master.configure(bg="#f0f0f0")

        # Заголовок
        self.title_label = tk.Label(self.master, text="Алгоритм LZ77", font=("Arial", 18, "bold"), bg="#f0f0f0")
        self.title_label.pack(pady=20)

        # Поле для ввода размера окна
        self.instruction_label = tk.Label(self.master, text="Введите размер окна (макс 400):", bg="#f0f0f0")
        self.instruction_label.pack(pady=5)
        self.window_size_entry = tk.Entry(self.master, font=("Arial", 14), justify="center")
        self.window_size_entry.pack(pady=5)

        # Кнопки для сжатия и распаковки
        self.compress_button = tk.Button(self.master, text="Сжать файл", command=self.compress_file,
                                         font=("Arial", 12), bg="#4CAF50", fg="white", padx=10, pady=5)
        self.compress_button.pack(pady=10)

        self.decompress_button = tk.Button(self.master, text="Распаковать файл", command=self.decompress_file,
                                           font=("Arial", 12), bg="#2196F3", fg="white", padx=10, pady=5)
        self.decompress_button.pack(pady=10)

        # Прогресс-бар для индикации выполнения операции
        self.progress = Progressbar(self.master, orient="horizontal", length=200, mode="determinate")
        self.progress.pack(pady=10)

        # Поле для вывода статуса выполнения операции
        self.status_label = tk.Label(self.master, text="", bg="#f0f0f0", font=("Arial", 10))
        self.status_label.pack(pady=10)

    def get_window_size(self):
        """
        Получает и проверяет введенное значение размера окна.
        """
        try:
            size = int(self.window_size_entry.get())
            if size < 1 or size > 400:
                raise ValueError("Размер окна должен быть от 1 до 400.")
            return size
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
            return None

    def compress_file(self):
        """
        Обработка сжатия файла.
        """
        window_size = self.get_window_size()
        if window_size is None:
            return

        input_file_path = filedialog.askopenfilename(title="Выберите файл для сжатия")
        if input_file_path:
            output_file_path = filedialog.asksaveasfilename(defaultextension=".lz77", title="Сохраните сжатый файл")
            if output_file_path:
                compressor = LZ77Compressor(window_size=window_size)
                try:
                    compressor.compress(input_file_path, output_file_path)
                    self.status_label.config(text="Файл успешно сжат!", fg="green")
                except Exception as e:
                    messagebox.showerror("Ошибка", str(e))

    def decompress_file(self):
        """
        Обработка распаковки файла.
        """
        input_file_path = filedialog.askopenfilename(title="Выберите файл для распаковки")
        if input_file_path:
            output_file_path = filedialog.asksaveasfilename(defaultextension=".txt", title="Сохраните распакованный файл")
            if output_file_path:
                compressor = LZ77Compressor()
                try:
                    compressor.decompress(input_file_path, output_file_path)
                    self.status_label.config(text="Файл успешно распакован!", fg="green")
                except Exception as e:
                    messagebox.showerror("Ошибка", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = LZ77GUI(root)
    root.mainloop()
