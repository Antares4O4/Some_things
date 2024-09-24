import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox


# Функция для вычисления MD5 хэша файла
def calculate_md5(file_path):
    md5_hash = hashlib.md5()


    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            md5_hash.update(chunk)

    return md5_hash.hexdigest()



def choose_file():
    file_path = filedialog.askopenfilename()  # Открытие окна выбора файла
    if file_path:
        hash_value = calculate_md5(file_path)  # Вычисляем хэш
        messagebox.showinfo("MD5 хэш", f"MD5 хэш файла:\n{hash_value}")  # Показ хэша в новом окне


# GUI
def main():
    root = tk.Tk()  # Создаем основное окно
    root.title("MD5 Хэш Файла")  # Заголовок окна
    root.geometry("300x100")  # Размеры окна

    # Кнопка для выбора файла
    btn_choose_file = tk.Button(root, text="Выбрать файл", command=choose_file)
    btn_choose_file.pack(pady=20)  # Размещение кнопки

    root.mainloop()  # Запуск основного цикла приложения


# Запуск программы
if __name__ == "__main__":
    main()
