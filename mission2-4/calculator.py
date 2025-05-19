import sys  # 시스템 관련 기능을 위한 표준 라이브러리
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QVBoxLayout, QLabel  # PyQt5 위젯 구성
from PyQt5.QtCore import Qt  # 정렬과 관련된 상수 제공


class CalculatorCore:
    def __init__(self):  # 계산기 로직을 담당하는 클래스 초기화
        self.reset()

    def reset(self):  # 식 초기화 메서드
        self.expression = ''  # 입력된 계산식 문자열
        self.result = ''  # 결과 저장용 (사용은 안 하고 있음)
        self.has_dot = False  # 소수점 입력 여부 추적

    def add(self, a, b):  # 덧셈 메서드
        return a + b

    def subtract(self, a, b):  # 뺄셈 메서드
        return a - b

    def multiply(self, a, b):  # 곱셈 메서드
        return a * b

    def divide(self, a, b):  # 나눗셈 메서드 (0 나누기 예외 처리)
        if b == 0:
            raise ZeroDivisionError('0으로 나눌 수 없습니다.')
        return a / b

    def negative_positive(self):  # 부호 전환 메서드
        if self.expression.startswith('-'):
            self.expression = self.expression[1:]  # 음수 → 양수
        elif self.expression:
            self.expression = '-' + self.expression  # 양수 → 음수

    def percent(self):  # 퍼센트 처리 (÷ 100)
        try:
            self.expression = str(float(self.expression) / 100)
        except:
            self.expression = 'Error'

    def equal(self):  # 수식 계산 및 결과 처리
        try:
            expr = self.expression.replace('×', '*').replace('÷', '/')  # 연산자 변환
            result = eval(expr)  # 문자열 수식 계산 / 문자열로된 파이썬 수식이나 코드를 실제로 실행하게 만드는 함수. / 다만 문자열이 들어갈수있기 때문에 조심해야 함. / 다만 학교에서 사용하는것이니 패스.
            if isinstance(result, float):
                result = '{:.6f}'.format(result).rstrip('0').rstrip('.')  # 소수점 6자리 반올림 + 깔끔한 출력
            self.expression = str(result)
        except ZeroDivisionError:
            self.expression = '0으로 나눌 수 없습니다.'
        except:
            self.expression = 'Error'


class Calculator(QWidget):  # PyQt5를 이용한 UI 클래스
    def __init__(self):
        super().__init__()
        self.setWindowTitle('iPhone Style Calculator')  # 창 제목 설정
        self.setFixedSize(320, 480)  # 창 크기 고정
        self.core = CalculatorCore()  # 계산 로직 객체 생성
        self.initUI()  # UI 구성 호출

    def initUI(self):  # UI 초기 구성
        main_layout = QVBoxLayout()  # 전체 세로 레이아웃

        self.display = QLabel('0')  # 결과 표시용 라벨
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # 오른쪽 수직직 정렬
        self.display.setStyleSheet('font-size: 40px; padding: 20px; background: black; color: white;')  # 스타일 지정
        main_layout.addWidget(self.display)  # 메인 레이아웃에 디스플레이 추가

        button_layout = QGridLayout()  # 버튼 그리드 레이아웃
        buttons = [  # 버튼 텍스트 배열
            ['AC', '+/-', '%', '÷'],
            ['7', '8', '9', '×'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['0', '.', '=']
        ]

        for row_idx, row in enumerate(buttons[:-1]):  # 마지막 줄 제외 버튼 생성
            for col_idx, btn_text in enumerate(row):
                btn = QPushButton(btn_text)  # 버튼 생성
                btn.setFixedSize(70, 60)  # 크기 설정
                btn.setStyleSheet('font-size: 24px;')  # 글씨 크기
                button_layout.addWidget(btn, row_idx + 1, col_idx)  # 버튼 위치 배치
                btn.clicked.connect(self.button_clicked)  # 클릭 이벤트 연결

        row_idx = len(buttons)  # 마지막 줄 인덱스
        for btn_text, col_info in zip(buttons[-1], [(0, 2), (2, 1), (3, 1)]):  # 마지막 줄 처리 (0 버튼은 2칸 병합)
            col, colspan = col_info  # 위치 정보 분리
            btn = QPushButton(btn_text)  # 버튼 생성
            btn.setFixedHeight(60)  # 높이 고정
            btn.setStyleSheet('font-size: 24px;')  # 글자 크기 설정
            button_layout.addWidget(btn, row_idx, col, 1, colspan)  # 그리드 위치 + 병합 크기 설정
            btn.clicked.connect(self.button_clicked)  # 클릭 이벤트 연결

        main_layout.addLayout(button_layout)  # 버튼 레이아웃 추가
        self.setLayout(main_layout)  # 최종 레이아웃 적용

    def button_clicked(self):  # 버튼 클릭 시 동작
        text = self.sender().text()  # 어떤 버튼 눌렀는지 확인

        if text == 'AC':
            self.core.reset()  # 초기화
        elif text == '+/-':
            self.core.negative_positive()  # 부호 변경
        elif text == '%':
            self.core.percent()  # 퍼센트 계산
        elif text == '=':
            self.core.equal()  # 결과 계산
        elif text == '.':
            if '.' not in self.core.expression:
                self.core.expression += '.'  # 소수점 중복 방지
        else:
            self.core.expression += text  # 숫자 및 연산자 입력

        self.update_display()  # 화면 갱신

    def update_display(self):  # 화면 출력 갱신
        output = self.core.expression or '0'  # 공백이면 0 표시
        if len(output) > 10:
            size = max(12, 40 - (len(output) - 10))  # 폰트 크기 자동 조정
        else:
            size = 40
        self.display.setStyleSheet(f'font-size: {size}px; padding: 20px; background: black; color: white;')
        self.display.setText(output)


if __name__ == '__main__':  # 프로그램 진입점
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())
