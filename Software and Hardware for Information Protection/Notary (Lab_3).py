import os
import tkinter as tk
from tkinter import filedialog, messagebox
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import hashlib
from cryptography.exceptions import InvalidSignature

# Папки для пользователей
SENDER_FOLDER = "sender_files"
NOTARY_FOLDER = "notary_files"
RECEIVER_FOLDER = "receiver_files"

# Инициализация папок
os.makedirs(SENDER_FOLDER, exist_ok=True)
os.makedirs(NOTARY_FOLDER, exist_ok=True)
os.makedirs(RECEIVER_FOLDER, exist_ok=True)


# Генерация хэша файла
def generate_hash(file_path):
    with open(file_path, "rb") as f:
        file_data = f.read()
    hash_value = hashlib.sha256(file_data).digest()
    return hash_value


# Генерация ключей Нотариусом
def generate_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Сохраняем ключи Нотариуса
    with open(os.path.join(NOTARY_FOLDER, "private_key.pem"), "wb") as f:
        f.write(private_pem)
    with open(os.path.join(NOTARY_FOLDER, "public_key.pem"), "wb") as f:
        f.write(public_pem)

    messagebox.showinfo("Нотариус", "Ключи успешно сгенерированы!")


# Подписывание файла Нотариусом
def sign_file():
    file_path = filedialog.askopenfilename(initialdir=NOTARY_FOLDER, title="Выберите файл для подписания")
    if not file_path:
        return

    # Генерация хэша файла
    hash_value = generate_hash(file_path)

    # Чтение приватного ключа
    with open(os.path.join(NOTARY_FOLDER, "private_key.pem"), "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    # Подписание хэша файла
    signature = private_key.sign(
        hash_value,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # Сохраняем подпись в отдельный файл
    signature_path = os.path.join(NOTARY_FOLDER, "signature_" + os.path.basename(file_path) + ".sig")
    with open(signature_path, "wb") as f:
        f.write(signature)

    # Переименование файла в подписанный
    signed_file_path = os.path.join(NOTARY_FOLDER, "signed_" + os.path.basename(file_path))
    os.rename(file_path, signed_file_path)

    # Перемещение открытого ключа в папку получателя
    with open(os.path.join(NOTARY_FOLDER, "public_key.pem"), "rb") as f:
        public_key = f.read()

    public_key_path = os.path.join(RECEIVER_FOLDER, "public_key.pem")
    with open(public_key_path, "wb") as f:
        f.write(public_key)

    # Сохраняем пути к файлам для отправки получателю
    send_file_to_receiver.signed_file_path = signed_file_path
    send_file_to_receiver.signature_path = signature_path
    send_file_to_receiver.public_key_path = public_key_path

    messagebox.showinfo("Нотариус", "Файл подписан! Подпись и открытый ключ отправлены получателю.")


# Проверка подписи Получателем
def verify_signature():
    signed_file_path = filedialog.askopenfilename(initialdir=RECEIVER_FOLDER, title="Выберите подписанный файл")
    signature_path = filedialog.askopenfilename(initialdir=RECEIVER_FOLDER, title="Выберите файл подписи")
    public_key_path = filedialog.askopenfilename(initialdir=RECEIVER_FOLDER, title="Выберите публичный ключ")

    if not signed_file_path or not signature_path or not public_key_path:
        return

    # Генерация хэша исходного файла
    hash_value = generate_hash(signed_file_path)

    # Чтение подписи
    with open(signature_path, "rb") as f:
        signature = f.read()

    # Чтение публичного ключа
    with open(public_key_path, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    # Проверка подписи
    try:
        public_key.verify(
            signature,
            hash_value,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        messagebox.showinfo("Получатель", "Подпись верна! Файл не изменён.")
    except InvalidSignature:
        messagebox.showwarning("Получатель", "Подпись неверна! Файл был изменён.")


# Отправка файла от Отправителя к Нотариусу
def send_file_to_notary():
    file_path = filedialog.askopenfilename(initialdir=SENDER_FOLDER, title="Выберите файл для отправки нотариусу")
    if not file_path:
        return

    new_file_path = os.path.join(NOTARY_FOLDER, os.path.basename(file_path))
    os.rename(file_path, new_file_path)

    messagebox.showinfo("Отправитель", "Файл успешно отправлен Нотариусу!")


# Отправка файла от Нотариуса к Получателю
def send_file_to_receiver():
    signed_file_path = send_file_to_receiver.signed_file_path
    signature_path = send_file_to_receiver.signature_path
    public_key_path = send_file_to_receiver.public_key_path

    new_signed_file_path = os.path.join(RECEIVER_FOLDER, os.path.basename(signed_file_path))
    new_signature_path = os.path.join(RECEIVER_FOLDER, os.path.basename(signature_path))
    new_public_key_path = os.path.join(RECEIVER_FOLDER, os.path.basename(public_key_path))

    os.rename(signed_file_path, new_signed_file_path)
    os.rename(signature_path, new_signature_path)
    os.rename(public_key_path, new_public_key_path)

    messagebox.showinfo("Нотариус", "Файл и подпись успешно отправлены Получателю!")


# Окно для отправителя
def sender_window():
    window = tk.Toplevel()
    window.title("Отправитель")
    window.geometry("300x200")

    label = tk.Label(window, text="Отправить файл Нотариусу")
    label.pack(pady=10)

    send_button = tk.Button(window, text="Отправить файл", command=send_file_to_notary)
    send_button.pack(pady=5)

    window.mainloop()


# Окно для Нотариуса
def notary_window():
    window = tk.Toplevel()
    window.title("Нотариус")
    window.geometry("300x200")

    label = tk.Label(window, text="Генерация ключей и подписание файла")
    label.pack(pady=10)

    gen_keys_button = tk.Button(window, text="Сгенерировать ключи", command=generate_keys)
    gen_keys_button.pack(pady=5)

    sign_button = tk.Button(window, text="Подписать файл", command=sign_file)
    sign_button.pack(pady=5)

    send_button = tk.Button(window, text="Отправить файл получателю", command=send_file_to_receiver)
    send_button.pack(pady=5)

    window.mainloop()


# Окно для Получателя
def receiver_window():
    window = tk.Toplevel()
    window.title("Получатель")
    window.geometry("300x200")

    label = tk.Label(window, text="Проверить подпись файла")
    label.pack(pady=10)

    verify_button = tk.Button(window, text="Проверить подпись", command=verify_signature)
    verify_button.pack(pady=5)

    window.mainloop()


# Главное окно программы
root = tk.Tk()
root.title("Система ЭЦП")
root.geometry("300x200")

label = tk.Label(root, text="Выберите роль")
label.pack(pady=10)

sender_button = tk.Button(root, text="Отправитель", command=sender_window)
sender_button.pack(pady=5)

notary_button = tk.Button(root, text="Нотариус", command=notary_window)
notary_button.pack(pady=5)

receiver_button = tk.Button(root, text="Получатель", command=receiver_window)
receiver_button.pack(pady=5)

root.mainloop()
