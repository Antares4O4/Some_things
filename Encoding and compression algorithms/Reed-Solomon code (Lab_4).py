import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import reedsolo  # Библиотека для кодирования/декодирования по коду Рида-Соломона

# Инициализация кодера Рида-Соломона с 10 контрольными символами
rs = reedsolo.RSCodec(10)

def load_file():
    """Загрузка текстового файла и отображение его содержимого."""
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        input_text.delete('1.0', tk.END)
        input_text.insert(tk.END, text)

def encode_text():
    """Кодирование введенного текста с использованием кода Рида-Соломона."""
    text = input_text.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Внимание", "Пожалуйста, введите текст для кодирования.")
        return

    try:
        # Кодируем текст в байты
        encoded_bytes = rs.encode(text.encode('utf-8'))
        # Преобразуем закодированные байты в двоичный формат
        encoded_binary = ''.join(format(byte, '08b') for byte in encoded_bytes)
        encoded_text.delete('1.0', tk.END)
        encoded_text.insert(tk.END, encoded_binary)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка кодирования: {e}")

def decode_text():
    """Декодирование закодированного текста и исправление ошибок."""
    encoded_content = encoded_text.get("1.0", tk.END).strip()
    if not encoded_content:
        messagebox.showwarning("Внимание", "Пожалуйста, введите закодированный текст.")
        return

    # Проверяем длину закодированного текста, чтобы избежать ошибок
    if len(encoded_content) % 8 != 0:
        messagebox.showerror("Ошибка", "Некорректный закодированный текст.")
        return

    # Преобразуем строку из двоичного формата в байты
    encoded_bytes = bytes(int(encoded_content[i:i + 8], 2) for i in range(0, len(encoded_content), 8))

    try:
        # Декодируем с исправлением ошибок
        decoded_bytes, decoded_msgecc, errata_pos = rs.decode(encoded_bytes)  # Извлекаем исправленные данные и позиции ошибок
        decoded_text.delete('1.0', tk.END)
        decoded_text.insert(tk.END, decoded_bytes.decode('utf-8'))  # Декодируем байты в строку

        # Отображение отчёта об исправленных ошибках
        error_log.delete('1.0', tk.END)
        if errata_pos:
            for pos in errata_pos:
                block_number = pos // 255  # Номер блока
                bit_number = pos % 255  # Номер бита
                error_log.insert(tk.END, f"Исправлена ошибка в блоке {block_number}, бит {bit_number}\n")
        else:
            error_log.insert(tk.END, "Ошибок не обнаружено.")

    except reedsolo.ReedSolomonError as e:
        messagebox.showerror("Ошибка декодирования", f"Не удалось исправить ошибки: {e}")

# GUI интерфейс
root = tk.Tk()
root.title("Код Рида-Соломона для текстовых файлов")

# Верхняя рамка для загрузки и кодирования
frame_top = tk.Frame(root)
frame_top.pack(pady=10)

# Кнопки загрузки и кодирования
btn_load = tk.Button(frame_top, text="Загрузить файл", command=load_file)
btn_load.grid(row=0, column=0, padx=5)

btn_encode = tk.Button(frame_top, text="Кодировать", command=encode_text)
btn_encode.grid(row=0, column=1, padx=5)

btn_decode = tk.Button(frame_top, text="Декодировать", command=decode_text)
btn_decode.grid(row=0, column=2, padx=5)

# Поля для отображения текстов
frame_texts = tk.Frame(root)
frame_texts.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Вводный текст
lbl_input = tk.Label(frame_texts, text="Исходный текст")
lbl_input.grid(row=0, column=0, sticky="w")
input_text = scrolledtext.ScrolledText(frame_texts, width=40, height=10)
input_text.grid(row=1, column=0, padx=5, pady=5)

# Закодированный текст
lbl_encoded = tk.Label(frame_texts, text="Закодированный текст")
lbl_encoded.grid(row=0, column=1, sticky="w")
encoded_text = scrolledtext.ScrolledText(frame_texts, width=40, height=10)
encoded_text.grid(row=1, column=1, padx=5, pady=5)

# Декодированный текст
lbl_decoded = tk.Label(frame_texts, text="Декодированный текст")
lbl_decoded.grid(row=0, column=2, sticky="w")
decoded_text = scrolledtext.ScrolledText(frame_texts, width=40, height=10)
decoded_text.grid(row=1, column=2, padx=5, pady=5)

# Поле для вывода ошибок
frame_errors = tk.Frame(root)
frame_errors.pack(padx=10, pady=5, fill=tk.BOTH)

lbl_errors = tk.Label(frame_errors, text="Отчёт об ошибках")
lbl_errors.pack(anchor="w")
error_log = scrolledtext.ScrolledText(frame_errors, width=100, height=5)
error_log.pack(padx=5, pady=5)

root.mainloop()
