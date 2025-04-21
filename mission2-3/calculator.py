import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iPhone Style Calculator")
        self.setFixedSize(320, 480)
        self.initUI()
        self.expression = ""

    def initUI(self):
        main_layout = QVBoxLayout()
        self.display = QLabel("0")
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display.setStyleSheet("font-size: 40px; padding: 20px; background: black; color: white;")
        main_layout.addWidget(self.display)

        button_layout = QGridLayout()
        buttons = [
            ["AC", "+/-", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["0", ".", "="]
        ]

        # 상단 4줄 (AC ~ +) 버튼 처리
        for row_idx, row in enumerate(buttons[:-1]):
            for col_idx, btn_text in enumerate(row):
                btn = QPushButton(btn_text)
                btn.setFixedSize(70, 60)
                btn.setStyleSheet("font-size: 24px;")
                button_layout.addWidget(btn, row_idx + 1, col_idx)
                btn.clicked.connect(self.button_clicked)

        # 마지막 줄 (0, ., =) 수동 처리
        row_idx = len(buttons)
        for btn_text, col_info in zip(buttons[-1], [(0, 2), (2, 1), (3, 1)]):  # (column, colspan)
            col, colspan = col_info
            btn = QPushButton(btn_text)
            if btn_text == "0":
                btn.setFixedHeight(60)
            else:
                btn.setFixedSize(70, 60)
            btn.setStyleSheet("font-size: 24px;")
            button_layout.addWidget(btn, row_idx, col, 1, colspan)
            btn.clicked.connect(self.button_clicked)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def button_clicked(self):
        text = self.sender().text()

        if text == "AC":
            self.expression = ""
            self.display.setText("0")
        elif text == "+/-":
            if self.expression.startswith("-"):
                self.expression = self.expression[1:]
            elif self.expression:
                self.expression = "-" + self.expression
            self.display.setText(self.expression)
        elif text == "%":
            try:
                result = str(eval(self.expression) / 100)
                self.expression = result
                self.display.setText(result)
            except:
                self.display.setText("Error")
        elif text == "=":
            try:
                expr = self.expression.replace("×", "*").replace("÷", "/")
                result = str(eval(expr))
                self.display.setText(result)
                self.expression = result
            except:
                self.display.setText("Error")
                self.expression = ""
        else:
            self.expression += text
            self.display.setText(self.expression)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())
