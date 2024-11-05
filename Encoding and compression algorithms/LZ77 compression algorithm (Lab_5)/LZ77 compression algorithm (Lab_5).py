import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from LZ77 import LZ77Compressor

class LZ77GUI:
    def __init__(self, master):
        self.master = master
        self.master.title("LZ77 Компрессия и Декомпрессия")
        self.master.geometry("400x300")
        self.master.configure(bg="#f0f0f0")

        # Заголовок
        self.title_label = tk.Label(self.master, text="Алгоритм LZ77", font=("Arial", 18, "bold"), bg="#f0f0f0")
        self.title_label.pack(pady=20)

        # Инструкция
        self.instruction_label = tk.Label(self.master, text="Выберите размер окна (макс 400):", bg="#f0f0f0")
        self.instruction_label.pack(pady=5)

        # Размер окна
        self.window_size_entry = tk.Entry(self.master, font=("Arial", 14), justify="center")
        self.window_size_entry.pack(pady=5)

        # Кнопки
        self.compress_button = tk.Button(self.master, text="Сжать файл", command=self.compress_file,
                                          font=("Arial", 12), bg="#4CAF50", fg="white", padx=10, pady=5)
        self.compress_button.pack(pady=10)

        self.decompress_button = tk.Button(self.master, text="Распаковать файл", command=self.decompress_file,
                                            font=("Arial", 12), bg="#2196F3", fg="white", padx=10, pady=5)
        self.decompress_button.pack(pady=10)

        # Строка состояния
        self.status_label = tk.Label(self.master, text="", bg="#f0f0f0", font=("Arial", 10))
        self.status_label.pack(pady=10)

    def get_window_size(self):
        try:
            size = int(self.window_size_entry.get())
            if size < 1 or size > 400:
                raise ValueError("Размер окна должен быть в пределах от 1 до 400.")
            return size
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
            return None

    def compress_file(self):
        window_size = self.get_window_size()
        if window_size is None:
            return  # Ошибка в размере окна, не продолжаем

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
        input_file_path = filedialog.askopenfilename(title="Выберите файл для распаковки")
        if input_file_path:
            output_file_path = filedialog.asksaveasfilename(defaultextension=".txt", title="Сохраните распакованный файл")
            if output_file_path:
                compressor = LZ77Compressor()  # Размер окна не важен для распаковки
                try:
                    compressor.decompress(input_file_path, output_file_path)
                    self.status_label.config(text="Файл успешно распакован!", fg="green")
                except Exception as e:
                    messagebox.showerror("Ошибка", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = LZ77GUI(root)
    root.mainloop()
