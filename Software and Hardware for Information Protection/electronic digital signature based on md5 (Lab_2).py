import tkinter as tk
from tkinter import filedialog
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
import hashlib

def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem, public_pem

def generate_signature_md5(file_path, private_key_path, output_text_file_path):
    # Загрузка приватного ключа
    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    # Чтение содержимого файла
    with open(file_path, "rb") as file:
        file_data = file.read()

    # Создание хеша MD5
    md5_hash = hashlib.md5(file_data).hexdigest()

    # Создание подписи
    signature = private_key.sign(
        md5_hash.encode(),
        padding.PKCS1v15(),
        hashes.MD5()
    )

    # Сохранение хеша MD5 и подписи в текстовый файл
    with open(output_text_file_path, "w") as text_file:
        text_file.write(f"MD5 Hash: {md5_hash}\n")
        text_file.write(f"Signature: {signature.hex()}\n")

    print(f"Подпись успешно создана и сохранена в {output_text_file_path}")

def verify_signature_md5(file_path, public_key_path, signature_path):
    # Загрузка открытого ключа
    with open(public_key_path, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )

    # Чтение содержимого файла
    with open(file_path, "rb") as file:
        file_data = file.read()

    # Чтение подписи
    with open(signature_path, "r") as signature_file:
        signature_data = signature_file.read()
        signature = bytes.fromhex(signature_data.split("Signature: ")[1].strip())

    # Создание хеша MD5
    md5_hash = hashlib.md5(file_data).hexdigest()

    # Проверка подписи
    try:
        public_key.verify(
            signature,
            md5_hash.encode(),
            padding.PKCS1v15(),
            hashes.MD5()
        )
        return True
    except InvalidSignature:
        return False

def select_file():
    file_path = filedialog.askopenfilename(title="Выберите файл для подписи")
    file_entry.delete(0, tk.END)
    file_entry.insert(0, file_path)

def select_private_key():
    key_path = filedialog.askopenfilename(title="Выберите приватный ключ")
    key_entry.delete(0, tk.END)
    key_entry.insert(0, key_path)

def select_output_file():
    output_path = filedialog.asksaveasfilename(title="Сохранить результат как", defaultextension=".txt")
    output_entry.delete(0, tk.END)
    output_entry.insert(0, output_path)

def generate_signature():
    file_path = file_entry.get()
    private_key_path = key_entry.get()
    output_text_file_path = output_entry.get()

    if file_path and private_key_path and output_text_file_path:
        generate_signature_md5(file_path, private_key_path, output_text_file_path)
        result_label.config(text="Подпись успешно создана и сохранена.")
    else:
        result_label.config(text="Пожалуйста, выберите все необходимые файлы.")

def generate_and_save_keys():
    private_pem, public_pem = generate_keys()

    private_key_path = filedialog.asksaveasfilename(title="Сохранить приватный ключ как", defaultextension=".pem")
    public_key_path = filedialog.asksaveasfilename(title="Сохранить открытый ключ как", defaultextension=".pem")

    if private_key_path and public_key_path:
        with open(private_key_path, "wb") as private_file:
            private_file.write(private_pem)

        with open(public_key_path, "wb") as public_file:
            public_file.write(public_pem)

        result_label.config(text="Ключи успешно сгенерированы и сохранены.")
    else:
        result_label.config(text="Пожалуйста, выберите пути для сохранения ключей.")

def select_verify_file():
    file_path = filedialog.askopenfilename(title="Выберите файл для проверки")
    verify_file_entry.delete(0, tk.END)
    verify_file_entry.insert(0, file_path)

def select_verify_public_key():
    key_path = filedialog.askopenfilename(title="Выберите открытый ключ")
    verify_key_entry.delete(0, tk.END)
    verify_key_entry.insert(0, key_path)

def select_verify_signature_file():
    signature_path = filedialog.askopenfilename(title="Выберите файл с подписью")
    verify_signature_entry.delete(0, tk.END)
    verify_signature_entry.insert(0, signature_path)

def verify_signature():
    file_path = verify_file_entry.get()
    public_key_path = verify_key_entry.get()
    signature_path = verify_signature_entry.get()

    if file_path and public_key_path and signature_path:
        is_valid = verify_signature_md5(file_path, public_key_path, signature_path)
        if is_valid:
            result_label.config(text="Подпись действительна.")
        else:
            result_label.config(text="Подпись недействительна.")
    else:
        result_label.config(text="Пожалуйста, выберите все необходимые файлы.")

# Создание главного окна
root = tk.Tk()
root.title("Генератор и проверка ЭЦП на основе MD5")

# Создание элементов интерфейса для генерации подписи
file_label = tk.Label(root, text="Файл для подписи:")
file_label.grid(row=0, column=0, padx=10, pady=10)

file_entry = tk.Entry(root, width=50)
file_entry.grid(row=0, column=1, padx=10, pady=10)

file_button = tk.Button(root, text="Выбрать файл", command=select_file)
file_button.grid(row=0, column=2, padx=10, pady=10)

key_label = tk.Label(root, text="Приватный ключ:")
key_label.grid(row=1, column=0, padx=10, pady=10)

key_entry = tk.Entry(root, width=50)
key_entry.grid(row=1, column=1, padx=10, pady=10)

key_button = tk.Button(root, text="Выбрать ключ", command=select_private_key)
key_button.grid(row=1, column=2, padx=10, pady=10)

output_label = tk.Label(root, text="Сохранить результат как:")
output_label.grid(row=2, column=0, padx=10, pady=10)

output_entry = tk.Entry(root, width=50)
output_entry.grid(row=2, column=1, padx=10, pady=10)

output_button = tk.Button(root, text="Выбрать путь", command=select_output_file)
output_button.grid(row=2, column=2, padx=10, pady=10)

generate_button = tk.Button(root, text="Создать подпись", command=generate_signature)
generate_button.grid(row=3, column=1, padx=10, pady=20)

generate_keys_button = tk.Button(root, text="Сгенерировать ключи", command=generate_and_save_keys)
generate_keys_button.grid(row=4, column=1, padx=10, pady=20)

# Создание элементов интерфейса для проверки подписи
verify_file_label = tk.Label(root, text="Файл для проверки:")
verify_file_label.grid(row=5, column=0, padx=10, pady=10)

verify_file_entry = tk.Entry(root, width=50)
verify_file_entry.grid(row=5, column=1, padx=10, pady=10)

verify_file_button = tk.Button(root, text="Выбрать файл", command=select_verify_file)
verify_file_button.grid(row=5, column=2, padx=10, pady=10)

verify_key_label = tk.Label(root, text="Открытый ключ:")
verify_key_label.grid(row=6, column=0, padx=10, pady=10)

verify_key_entry = tk.Entry(root, width=50)
verify_key_entry.grid(row=6, column=1, padx=10, pady=10)

verify_key_button = tk.Button(root, text="Выбрать ключ", command=select_verify_public_key)
verify_key_button.grid(row=6, column=2, padx=10, pady=10)

verify_signature_label = tk.Label(root, text="Файл с подписью:")
verify_signature_label.grid(row=7, column=0, padx=10, pady=10)

verify_signature_entry = tk.Entry(root, width=50)
verify_signature_entry.grid(row=7, column=1, padx=10, pady=10)

verify_signature_button = tk.Button(root, text="Выбрать подпись", command=select_verify_signature_file)
verify_signature_button.grid(row=7, column=2, padx=10, pady=10)

verify_button = tk.Button(root, text="Проверить подпись", command=verify_signature)
verify_button.grid(row=8, column=1, padx=10, pady=20)

result_label = tk.Label(root, text="")
result_label.grid(row=9, column=1, padx=10, pady=10)

# Запуск главного цикла
root.mainloop()
