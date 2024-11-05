import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# Позиции для кода Хэмминга
ECC_POS = ([0, 1, 3, 4, 6, 8, 10, 11, 13, 15], [0, 2, 3, 5, 6, 9, 10, 12, 13],
           [1, 2, 3, 7, 8, 9, 10, 14, 15], [4, 5, 6, 7, 8, 9, 10], [11, 12, 13, 14, 15])
POSITION16_5 = (11, 4, 1, 0, 0)
ECC_POS21 = ([2, 4, 6, 8, 10, 12, 14, 16, 18, 20], [2, 5, 6, 9, 10, 13, 14, 17, 18],
             [4, 5, 6, 12, 13, 14, 19, 20], [8, 9, 10, 11, 12, 13, 14], [16, 17, 18, 19, 20])
POSITION21 = (0, 1, 3, 7, 15)


def is_bool(variable):
    new_bool = [x for x in variable if x in ["0", "1"]]
    return len(variable) == len(new_bool)


def counter(position, variable):
    list_bool = list(str(variable))
    ecc_value = []
    for item_on_place in position:
        y = sum(1 for x in item_on_place if list_bool[x] == "1")
        ecc_value.append(y % 2)
    return ecc_value


def to_hamming(value, position=POSITION16_5):
    bit16 = str(value)
    if len(bit16) != 16:
        raise ValueError("Число разрядов не равно 16")
    elif not is_bool(bit16):
        raise ValueError("Число не двоичное")

    ecc_date = counter(ECC_POS, bit16)
    bit16 = list(bit16)
    for x in position:
        bit16.insert(int(x), str(ecc_date.pop()))
    return ''.join(bit16)


def checker(variable, ecc21_date):
    list_21 = list(str(variable))
    ecc_old = [int(list_21[x]) for x in POSITION21]
    error_list = [i for i, x in enumerate(ecc_old) if ecc21_date[i] != x]
    return error_list


def to_16bit(variable):
    if len(variable) != 21:
        raise ValueError("Число разрядов не равно 21")
    elif not is_bool(variable):
        raise ValueError("Число не двоичное")

    ecc21_date = counter(ECC_POS21, variable)
    err_list = checker(variable, ecc21_date)
    bit21ecc = list(str(variable))
    result = ""

    # Рассчёт синдрома ошибки для проверки типа ошибки
    syndrome = sum((1 << i) for i in err_list) if err_list else 0

    if syndrome == 0:
        # Нет ошибок
        result = ""
    elif len(err_list) == 1:
        # Одиночная ошибка
        err_pos = syndrome - 1
        bit21ecc[err_pos] = '1' if bit21ecc[err_pos] == '0' else '0'
        result = f"Исправлена одиночная ошибка в бите {err_pos + 1}\n"
    else:
        # Двойная ошибка
        result = f"Обнаружена двойная ошибка (биты {err_list}), не исправляется\n"

    # Удаление контрольных битов
    for x in [15, 7, 3, 1, 0]:
        del bit21ecc[x]

    return ''.join(bit21ecc), result


def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        input_text.delete('1.0', tk.END)
        input_text.insert(tk.END, text)


def encode_text():
    text = input_text.get("1.0", tk.END).strip()
    encoded_lines = []
    for char in text:
        binary_char = f"{ord(char):016b}"
        hamming_code = to_hamming(binary_char)
        encoded_lines.append(hamming_code)
    encoded_text.delete('1.0', tk.END)
    encoded_text.insert(tk.END, '\n'.join(encoded_lines))


def decode_text():
    encoded_content = encoded_text.get("1.0", tk.END).strip().splitlines()
    decoded_chars = []
    error_report = ""

    # Счётчик для блоков
    block_number = 1

    for line in encoded_content:
        binary_16bit, error_info = to_16bit(line.strip())

        # Добавление информации о блоке в отчёт об ошибках
        if error_info:
            error_info = f"Блок {block_number}: " + error_info
        error_report += error_info

        decoded_chars.append(chr(int(binary_16bit, 2)))
        block_number += 1  # Переход к следующему блоку

    # Запись в интерфейс
    decoded_text.delete('1.0', tk.END)
    decoded_text.insert(tk.END, ''.join(decoded_chars))
    error_log.delete('1.0', tk.END)
    error_log.insert(tk.END, error_report)
    messagebox.showinfo("Декодирование завершено", "Процесс декодирования завершен.")


# GUI приложение
root = tk.Tk()
root.title("Код Хэмминга (16,5) для текстовых файлов")

# Верхняя рамка для загрузки и кодирования
frame_top = tk.Frame(root)
frame_top.pack(pady=10)

# Кнопки загрузки и кодирования
btn_load = tk.Button(frame_top, text="Загрузить файл", command=load_file)
btn_load.grid(row=0, column=0, padx=5)

btn_encode = tk.Button(frame_top, text="Кодировать", command=encode_text)
btn_encode.grid(row=0, column=1, padx=5)

btn_decode = tk.Button(frame_top, text="Декодировать и исправить ошибки", command=decode_text)
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
lbl_encoded = tk.Label(frame_texts, text="Закодированный текст (можно редактировать)")
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
