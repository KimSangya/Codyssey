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
        # 전체 레이아웃 설정정
        main_layout = QVBoxLayout()
        self.display = QLabel("0")
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display.setStyleSheet("font-size: 40px; padding: 20px; background: black; color: white;")
        main_layout.addWidget(self.display)

        # 버튼 레이아웃
        button_layout = QGridLayout()
        buttons = [
            ["AC", "+/-", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["0", ".", "="]
        ]

        for row_idx, row in enumerate(buttons):
            for col_idx, btn_text in enumerate(row):
                if btn_text == "0":
                    btn = QPushButton(btn_text)
                    btn.setFixedHeight(60)
                    btn.setStyleSheet("font-size: 24px;")
                    button_layout.addWidget(btn, row_idx + 1, 0, 1, 2)
                    btn.clicked.connect(self.button_clicked)
                    continue
                elif btn_text == "." and len(row) < 4:
                    col = 2
                else:
                    col = col_idx if btn_text != "." else 2
                btn = QPushButton(btn_text)
                btn.setFixedSize(70, 60)
                btn.setStyleSheet("font-size: 24px;")
                button_layout.addWidget(btn, row_idx + 1, col)
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
    # 1. App 객체 생성
    app = QApplication(sys.argv)
    calc = Calculator()
    # 창 띄우기
    calc.show()
    # 이벤트 루프 실행행
    sys.exit(app.exec_())