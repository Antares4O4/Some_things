import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTextEdit, QMessageBox)
from PyQt5.QtGui import QFont

# Вероятности английских букв из таблицы
ENGLISH_FREQ = {
    'a': 0.0575, 'b': 0.0128, 'c': 0.0263, 'd': 0.0285, 'e': 0.0913,
    'f': 0.0173, 'g': 0.0133, 'h': 0.0313, 'i': 0.0599, 'j': 0.0006,
    'k': 0.0084, 'l': 0.0335, 'm': 0.0235, 'n': 0.0596, 'o': 0.0689,
    'p': 0.0192, 'q': 0.0008, 'r': 0.0508, 's': 0.0567, 't': 0.0706,
    'u': 0.0334, 'v': 0.0069, 'w': 0.0119, 'x': 0.0073, 'y': 0.0164,
    'z': 0.0007, ' ': 0.1928
}


def create_ascii_table(data):
    """Создает красивую ASCII таблицу из данных о вероятностях"""
    # Определяем ширину колонок
    symbol_width = 10
    probability_width = 12

    # Символы для отрисовки таблицы
    top_left = '╔'
    top_right = '╗'
    bottom_left = '╚'
    bottom_right = '╝'
    horizontal = '═'
    vertical = '║'
    t_down = '╦'
    t_up = '╩'
    t_right = '╠'
    t_left = '╣'
    cross = '╬'

    # Создаем заголовок таблицы
    header = (f"{top_left}{horizontal * symbol_width}{t_down}"
              f"{horizontal * probability_width}{top_right}\n")
    header += (f"{vertical}{'Символ':^{symbol_width}}{vertical}"
               f"{'Вероятность':^{probability_width}}{vertical}\n")
    header += (f"{t_right}{horizontal * symbol_width}{cross}"
               f"{horizontal * probability_width}{t_left}\n")

    # Создаем строки таблицы
    rows = []
    for symbol, prob in sorted(data.items()):
        if symbol == ' ':
            symbol_display = 'пробел'
        else:
            symbol_display = symbol
        row = (f"{vertical}{symbol_display:^{symbol_width}}{vertical}"
               f"{prob:^{probability_width}.4f}{vertical}")
        rows.append(row)

    # Создаем подвал таблицы
    footer = (f"{bottom_left}{horizontal * symbol_width}{t_up}"
              f"{horizontal * probability_width}{bottom_right}")

    # Собираем таблицу
    return header + '\n'.join(rows) + '\n' + footer


class ArithmeticCoding:
    def __init__(self):
        self.precision = 32

    def get_probability_ranges(self):
        prob_table = {}
        current = 0.0
        for symbol, freq in sorted(ENGLISH_FREQ.items()):
            prob_table[symbol] = (current, current + freq)
            current += freq
        return prob_table

    def encode(self, data):
        if not data:
            return 0.0, None

        prob_table = self.get_probability_ranges()
        low, high = 0.0, 1.0

        for symbol in data.lower():
            if symbol not in prob_table:
                continue
            symbol_low, symbol_high = prob_table[symbol]
            range_size = high - low
            high = low + range_size * symbol_high
            low = low + range_size * symbol_low

        return (low + high) / 2, prob_table

    def decode(self, encoded_value, prob_table, message_length):
        result = []
        current_value = encoded_value

        for _ in range(message_length):
            for symbol, (low, high) in sorted(prob_table.items()):
                if low <= current_value < high:
                    result.append(symbol)
                    range_size = high - low
                    current_value = (current_value - low) / range_size
                    break

        return ''.join(result)


class ArithmeticCodingGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.coder = ArithmeticCoding()
        self.words = []
        self.MAX_WORDS = 15
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Арифметическое кодирование')
        self.setGeometry(100, 100, 900, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Панель ввода
        input_panel = QWidget()
        input_layout = QHBoxLayout(input_panel)

        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText('Введите слово (только английские буквы)')
        add_button = QPushButton('Добавить слово')
        add_button.clicked.connect(self.add_word)

        input_layout.addWidget(self.word_input)
        input_layout.addWidget(add_button)

        main_layout.addWidget(input_panel)

        # Список слов
        words_label = QLabel('Список слов:')
        main_layout.addWidget(words_label)

        self.words_display = QTextEdit()
        self.words_display.setReadOnly(True)
        self.words_display.setMaximumHeight(100)
        main_layout.addWidget(self.words_display)

        # Кнопки управления
        button_panel = QWidget()
        button_layout = QHBoxLayout(button_panel)

        encode_button = QPushButton('Закодировать')
        encode_button.clicked.connect(self.encode_words)
        clear_button = QPushButton('Очистить всё')
        clear_button.clicked.connect(self.clear_all)

        button_layout.addWidget(encode_button)
        button_layout.addWidget(clear_button)

        main_layout.addWidget(button_panel)

        # Область результатов
        results_label = QLabel('Результаты:')
        main_layout.addWidget(results_label)

        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setMaximumHeight(200)
        main_layout.addWidget(self.results_display)

        # Область для таблицы вероятностей
        prob_label = QLabel('Таблица вероятностей символов:')
        main_layout.addWidget(prob_label)

        # Создаем таблицу вероятностей с помощью ASCII
        prob_table = create_ascii_table(ENGLISH_FREQ)

        prob_display = QTextEdit()
        prob_display.setReadOnly(True)
        # Устанавливаем моноширинный шрифт для правильного отображения ASCII таблицы
        font = QFont("Courier New")
        font.setPointSize(10)
        prob_display.setFont(font)
        prob_display.setText(prob_table)
        prob_display.setMaximumHeight(800)
        main_layout.addWidget(prob_display)

    def add_word(self):
        word = self.word_input.text().strip()
        if not word:
            QMessageBox.warning(self, 'Предупреждение', 'Пожалуйста, введите слово')
            return

        if not all(c.isalpha() or c.isspace() for c in word):
            QMessageBox.warning(self, 'Предупреждение',
                                'Пожалуйста, используйте только английские буквы и пробелы')
            return

        if len(self.words) >= self.MAX_WORDS:
            QMessageBox.warning(self, 'Предупреждение',
                                f'Достигнуто максимальное количество слов ({self.MAX_WORDS})')
            return

        self.words.append(word)
        self.update_words_display()
        self.word_input.clear()

    def update_words_display(self):
        self.words_display.setText('\n'.join(f'{i + 1}. {word}'
                                             for i, word in enumerate(self.words)))

    def encode_words(self):
        if not self.words:
            QMessageBox.warning(self, 'Предупреждение', 'Добавьте хотя бы одно слово')
            return

        results = []
        for word in self.words:
            encoded_value, prob_table = self.coder.encode(word)
            decoded_word = self.coder.decode(encoded_value, prob_table, len(word))

            original_bits = len(word) * 8
            encoded_bits = 32
            compression_ratio = original_bits / encoded_bits

            results.append(
                f'Слово: {word}\n'
                f'Закодированное значение: {encoded_value:.10f}\n'
                f'Декодированное слово: {decoded_word}\n'
                f'Исходный размер: {original_bits} бит\n'
                f'Размер после кодирования: {encoded_bits} бит\n'
                f'Степень сжатия: {compression_ratio:.2f}\n'
                f'{"-" * 144}'
            )

        self.results_display.setText('\n'.join(results))

    def clear_all(self):
        self.words = []
        self.words_display.clear()
        self.results_display.clear()
        self.word_input.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ArithmeticCodingGUI()
    gui.show()
    sys.exit(app.exec_())