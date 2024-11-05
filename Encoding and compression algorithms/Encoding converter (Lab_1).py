import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QComboBox
)
import chardet
import subprocess

# Поддерживаемые кодировки
SUPPORTED_ENCODINGS = ['cp866', 'cp1251', 'maccyrillic', 'iso-8859-5']

class EncodingConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Конвертер кодировок')
        self.setGeometry(100, 100, 400, 200)

        # Layouts
        main_layout = QVBoxLayout()
        file_layout = QHBoxLayout()
        output_layout = QHBoxLayout()
        encoding_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        # Входной файл
        self.input_label = QLabel('Входной файл:')
        self.input_file = QLineEdit()
        self.input_button = QPushButton('Выбрать')
        self.input_button.clicked.connect(self.select_input_file)

        file_layout.addWidget(self.input_label)
        file_layout.addWidget(self.input_file)
        file_layout.addWidget(self.input_button)

        # Выходной файл
        self.output_label = QLabel('Выходной файл:')
        self.output_file = QLineEdit()
        self.output_button = QPushButton('Сохранить как')
        self.output_button.clicked.connect(self.select_output_file)

        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_file)
        output_layout.addWidget(self.output_button)

        # Целевая кодировка
        self.encoding_label = QLabel('Целевая кодировка:')
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(SUPPORTED_ENCODINGS)

        encoding_layout.addWidget(self.encoding_label)
        encoding_layout.addWidget(self.encoding_combo)

        # Кнопка конвертации
        self.convert_button = QPushButton('Конвертировать')
        self.convert_button.clicked.connect(self.convert_file)
        button_layout.addWidget(self.convert_button)

        # Добавляем все лейауты в главный
        main_layout.addLayout(file_layout)
        main_layout.addLayout(output_layout)
        main_layout.addLayout(encoding_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def select_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Выберите файл')
        if file_path:
            self.input_file.setText(file_path)

    def select_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, 'Сохранить файл как', '', 'Text Files (*.txt);;All Files (*)')
        if file_path:
            self.output_file.setText(file_path)

    def detect_encoding(self, file_path):
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result['encoding']

    def convert_with_iconv(self, input_file, output_file, from_encoding, to_encoding):
        try:
            # Выполняем команду iconv для конвертации кодировки
            result = subprocess.run(
                ['iconv', '-f', from_encoding, '-t', to_encoding, '-o', output_file, input_file],
                check=True,
                capture_output=True
            )
            return f"Файл успешно конвертирован из {from_encoding} в {to_encoding} с использованием iconv."
        except subprocess.CalledProcessError as e:
            return f"Ошибка при конвертации с использованием iconv: {e.stderr.decode()}"

    def convert_file(self):
        input_file = self.input_file.text()
        output_file = self.output_file.text()
        target_encoding = self.encoding_combo.currentText()

        if not input_file or not output_file:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите входной и выходной файл.")
            return

        # Определяем кодировку входного файла
        source_encoding = self.detect_encoding(input_file)

        if not source_encoding:
            QMessageBox.warning(self, "Ошибка", "Не удалось определить кодировку входного файла.")
            return

        # Если выбранная кодировка - CP10007, используем iconv
        if target_encoding == 'cp10007':
            result = self.convert_with_iconv(input_file, output_file, source_encoding, 'CP10007')
        else:
            # Иначе используем стандартную конвертацию с Python
            try:
                with open(input_file, 'r', encoding=source_encoding, errors='replace') as f:
                    content = f.read()

                with open(output_file, 'w', encoding=target_encoding, errors='replace') as f:
                    f.write(content)

                result = f"Файл успешно конвертирован из {source_encoding} в {target_encoding}."
            except Exception as e:
                result = f"Ошибка: {str(e)}"

        QMessageBox.information(self, "Результат", result)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EncodingConverterApp()
    ex.show()
    sys.exit(app.exec_())