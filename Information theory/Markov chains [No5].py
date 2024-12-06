import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout,
                             QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QLineEdit, QTextEdit, QSpinBox, QMessageBox)
import numpy as np
from fractions import Fraction


class MarkovAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Марковский источник')
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Левая панель
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        size_widget = QWidget()
        size_layout = QHBoxLayout(size_widget)
        size_layout.addWidget(QLabel('Размер матрицы:'))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(2, 10)
        self.size_spin.setValue(3)
        self.size_spin.valueChanged.connect(self.create_matrix)
        size_layout.addWidget(self.size_spin)
        left_layout.addWidget(size_widget)

        # Матрица ввода
        self.matrix_widget = QWidget()
        self.matrix_layout = QGridLayout(self.matrix_widget)
        left_layout.addWidget(self.matrix_widget)

        # Кнопки
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        self.calc_button = QPushButton('Рассчитать')
        self.calc_button.clicked.connect(self.calculate)
        self.clear_button = QPushButton('Очистить')
        self.clear_button.clicked.connect(self.clear)
        button_layout.addWidget(self.calc_button)
        button_layout.addWidget(self.clear_button)
        left_layout.addWidget(button_widget)
        left_layout.addStretch()

        # Вывод
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(self.output, 2)

        self.matrix_entries = []
        self.create_matrix()

    def create_matrix(self):
        for row in self.matrix_entries:
            for entry in row:
                entry.deleteLater()

        size = self.size_spin.value()
        self.matrix_entries = []

        while self.matrix_layout.count():
            item = self.matrix_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for j in range(size):
            self.matrix_layout.addWidget(QLabel(f'a{j + 1}'), 0, j + 1)

        for i in range(size):
            self.matrix_layout.addWidget(QLabel(f'a{i + 1}'), i + 1, 0)
            row_entries = []
            for j in range(size):
                entry = QLineEdit('0')
                entry.setFixedWidth(80)
                self.matrix_layout.addWidget(entry, i + 1, j + 1)
                row_entries.append(entry)
            self.matrix_entries.append(row_entries)

    def get_matrix(self):
        size = len(self.matrix_entries)
        matrix = np.zeros((size, size))
        for i in range(size):
            for j in range(size):
                try:
                    matrix[i][j] = float(self.matrix_entries[i][j].text().replace(',', '.'))
                except ValueError:
                    QMessageBox.warning(self, 'Ошибка', f'Неверное число в ячейке [{i + 1},{j + 1}]')
                    return None
        return matrix

    def clear(self):
        for row in self.matrix_entries:
            for entry in row:
                entry.setText('0')
        self.output.clear()

    def calculate(self):
        matrix = self.get_matrix()
        if matrix is None:
            return

        if not np.allclose(matrix.sum(), 1.0, rtol=1e-5):
            QMessageBox.warning(self, 'Ошибка', 'Сумма вероятностей должна быть равна 1')
            return

        self.output.clear()
        scheme_A = np.sum(matrix, axis=1)

        # Вывод начальных данных
        self.output.append("1) Объединённая схема (A,A):")
        self.print_simple_matrix(matrix)

        self.output.append("\n2) Вероятностная схема A:")
        for i, val in enumerate(scheme_A):
            self.output.append(f"a{i + 1} = {val:.12f}")

        transition_matrix = np.zeros_like(matrix)
        for i in range(len(scheme_A)):
            if scheme_A[i] != 0:
                transition_matrix[i] = matrix[i] / scheme_A[i]

        self.output.append("\n3) Матрица переходных вероятностей P(s):")
        self.print_simple_matrix(transition_matrix, use_fractions=True)

        # Распределения
        k_gram_probs = self.calculate_k_gram_probabilities(scheme_A, transition_matrix, 5)
        for k, probs in k_gram_probs.items():
            self.output.append(f"\nРаспределение для {k}-грамм:")
            for seq, prob in sorted(probs.items()):
                self.output.append(f"P({seq}) = {prob:.12f}")

        # Энтропия
        self.output.append("\nЗначения энтропии H(k):")
        for k in range(1, 6):
            h_k = self.calculate_H_k(scheme_A, transition_matrix, k)
            self.output.append(f"H({k}) = {h_k:.12f} бит")

        h_inf = self.calculate_H_k(scheme_A, transition_matrix, 2)
        self.output.append(f"\nПредельное значение H(∞) = {h_inf:.12f} бит")

    def print_simple_matrix(self, matrix, use_fractions=False):
        size = len(matrix)
        for i in range(size):
            row = []
            for j in range(size):
                if use_fractions:
                    frac = Fraction(matrix[i, j]).limit_denominator(100)
                    val = f"{frac.numerator}/{frac.denominator}" if frac.denominator != 1 else str(frac.numerator)
                    row.append(f"{val:>5}")
                else:
                    row.append(f"{matrix[i, j]:.12f}")
            self.output.append(" ".join(row))

    def calculate_k_gram_probabilities(self, scheme_A, transition_matrix, k):
        sequences = {1: {f"a{i + 1}": p for i, p in enumerate(scheme_A)}}

        for length in range(2, k + 1):
            new_sequences = {}
            for prev_seq, prev_prob in sequences[length - 1].items():
                last_symbol = int(prev_seq[-1]) - 1
                for next_symbol in range(len(scheme_A)):
                    prob = prev_prob * transition_matrix[last_symbol][next_symbol]
                    if prob > 1e-10:
                        new_seq = f"{prev_seq}a{next_symbol + 1}"
                        new_sequences[new_seq] = prob
            sequences[length] = new_sequences

        return sequences

    def calculate_H_k(self, scheme_A, transition_matrix, k):
        if k == 1:
            return self.calculate_entropy(scheme_A)
        elif k == 2:
            conditional_entropy = 0
            for i in range(len(scheme_A)):
                if scheme_A[i] > 0:
                    conditional_entropy += scheme_A[i] * self.calculate_entropy(transition_matrix[i])
            return conditional_entropy
        else:
            return self.calculate_H_k(scheme_A, transition_matrix, 2)

    def calculate_entropy(self, probs):
        nonzero_probs = probs[probs > 0]
        return -np.sum(nonzero_probs * np.log2(nonzero_probs))


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MarkovAnalyzer()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()