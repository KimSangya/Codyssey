import sys  # 시스템 관련 기능 사용을 위한 모듈 (예: 프로그램 종료)

# PyQt5의 위젯(버튼, 창, 레이아웃 등) 기능을 가져옴
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt  # 정렬 등 레이아웃 관련 상수 제공

# 계산기 클래스 선언 (QWidget을 상속하여 GUI 창을 만듦)
class Calculator(QWidget):
    def __init__(self):  # 생성자: 객체가 생성될 때 자동 실행됨
        super().__init__()  # 부모 클래스(QWidget)의 초기화 실행
        self.setWindowTitle("iPhone Style Calculator")  # 창 제목 설정
        self.setFixedSize(320, 480)  # 창 크기 고정
        self.initUI()  # 사용자 인터페이스 구성 함수 호출
        self.expression = ""  # 계산식 저장할 문자열 변수

    def initUI(self):  # UI 구성 함수
        main_layout = QVBoxLayout()  # 전체를 세로로 배치할 레이아웃 생성

        self.display = QLabel("0")  # 결과 표시용 라벨 생성, 처음엔 0 표시
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # 오른쪽 정렬 + 수직 중앙 정렬
        self.display.setStyleSheet("font-size: 40px; padding: 20px; background: black; color: white;")  # 스타일 지정
        main_layout.addWidget(self.display)  # 디스플레이를 메인 레이아웃에 추가

        button_layout = QGridLayout()  # 버튼들을 그리드 형식으로 배치할 레이아웃 생성
        buttons = [  # 버튼 텍스트를 행별로 리스트로 정리
            ["AC", "+/-", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["0", ".", "="]
        ]

        # 위 4줄의 버튼들을 반복문으로 추가
        for row_idx, row in enumerate(buttons[:-1]):  # 마지막 줄은 따로 처리함
            for col_idx, btn_text in enumerate(row):  # 각 버튼에 대해
                btn = QPushButton(btn_text)  # 버튼 생성
                btn.setFixedSize(70, 60)  # 버튼 크기 고정
                btn.setStyleSheet("font-size: 24px;")  # 글자 크기 설정
                button_layout.addWidget(btn, row_idx + 1, col_idx)  # 버튼을 해당 위치에 추가
                btn.clicked.connect(self.button_clicked)  # 클릭 시 이벤트 연결

        row_idx = len(buttons)  # 마지막 줄의 행 인덱스 계산
        # 마지막 줄 버튼들: 위치와 병합 정보 포함
        for btn_text, col_info in zip(buttons[-1], [(0, 2), (2, 1), (3, 1)]):  # (열 위치, 병합 칸 수)
            col, colspan = col_info
            btn = QPushButton(btn_text)  # 버튼 생성
            if btn_text == "0":  # 0번 버튼만 넓게 표시
                btn.setFixedHeight(60)  # 높이만 고정
            else:
                btn.setFixedSize(70, 60)  # 나머지는 크기 고정
            btn.setStyleSheet("font-size: 24px;")  # 스타일 설정
            button_layout.addWidget(btn, row_idx, col, 1, colspan)  # 위치 및 병합 반영하여 추가
            btn.clicked.connect(self.button_clicked)  # 클릭 시 이벤트 연결

        main_layout.addLayout(button_layout)  # 버튼 레이아웃을 메인 레이아웃에 추가
        self.setLayout(main_layout)  # 최종 레이아웃을 창에 적용

    def button_clicked(self):  # 버튼이 눌렸을 때 실행될 함수
        text = self.sender().text()  # 누른 버튼의 텍스트 가져오기

        if text == "AC":  # AC 버튼이면
            self.expression = ""  # 계산식 초기화
            self.display.setText("0")  # 디스플레이도 0으로 초기화
        elif text == "+/-":  # +/- 버튼이면 부호 변경
            if self.expression.startswith("-"):  # 이미 음수면
                self.expression = self.expression[1:]  # - 제거
            elif self.expression:  # 값이 있으면
                self.expression = "-" + self.expression  # - 추가
            self.display.setText(self.expression)  # 화면에 표시
        elif text == "%":  # % 버튼이면
            try:
                result = str(eval(self.expression) / 100)  # 백분율 계산
                self.expression = result  # 계산 결과를 식에 저장
                self.display.setText(result)  # 결과 표시
            except:
                self.display.setText("Error")  # 오류 시 Error 표시
        elif text == "=":  # = 버튼이면 계산 수행
            try:
                expr = self.expression.replace("×", "*").replace("÷", "/")  # 연산자 치환
                result = str(eval(expr))  # 문자열 식을 계산
                self.display.setText(result)  # 결과 표시
                self.expression = result  # 결과를 다음 계산식으로 사용
            except:
                self.display.setText("Error")  # 계산 중 오류 발생 시
                self.expression = ""  # 계산식 초기화
        else:  # 숫자 또는 연산자 버튼이면
            self.expression += text  # 계산식에 추가
            self.display.setText(self.expression)  # 디스플레이에 반영

# 프로그램 실행 부분
if __name__ == "__main__":  # 이 파일이 메인으로 실행될 경우
    app = QApplication(sys.argv)  # QApplication 객체 생성 (필수)
    calc = Calculator()  # 계산기 객체 생성
    calc.show()  # 계산기 창 띄우기
    sys.exit(app.exec_())  # 프로그램 종료까지 이벤트 루프 실행
