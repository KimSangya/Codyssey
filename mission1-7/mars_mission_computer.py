import random  # 난수 생성을 위한 기본 모듈
import time    # 시간 측정 및 sleep 등을 위한 모듈
import threading  # 멀티스레딩을 위한 기본 모듈

# 환경 로그를 저장할 파일 이름
log_file = 'env.log'

# 각 환경 변수와 초기값, 누적값, 단위를 저장하는 딕셔너리
env_values = {
    "mars_base_internal_temperature": [(18, 30.5), 18, 0, '도'],
    "mars_base_external_temperature": [(0, 21), 0, 0, '도'],
    "mars_base_internal_humidity": [(50, 60), 50, 0, '%'],
    "mars_base_external_illuminance": [(500, 715), 500, 0, 'W/m2'],
    "mars_base_internal_co2": [(0.02, 0.1), 0.02, 0, '%'],
    "mars_base_internal_oxygen": [(4, 7), 4, 0, '%']
}

''' 
    class DummySensor 개념은 원래 배웠던 내용을 그대로 사용하는 것임으로,
    자세한 설명은 생략.
'''
# 센서 역할을 하는 DummySensor 클래스 정의
class DummySensor:
    def __init__(self, env_values):
        self.env_values = env_values  # 환경 데이터를 받아 저장

        # 로그 파일이 없으면 헤더 생성
        if not self.__file_exist(log_file):
            with open(log_file, 'a') as log:
                headers = self.env_values.keys()
                log.write('Date | ' + ' | '.join(headers) + '\n') # 헤더가 없을 경우 집어넣어서 제목들을 지어넣음.

    # 로그 파일 존재 여부를 확인하는 메서드 (비공개)
    def __file_exist(self, log_file):
        try:
            with open(log_file, 'r'):
                return True
        except FileNotFoundError:
            return False

    # 현재 환경 데이터를 반환
    def get_env(self):
        return self.env_values #값을 그대로 받고 반환.

    # 환경 데이터를 난수로 갱신하고 로그에 저장
    def set_env(self):
        now_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 현재 시간 문자열
        print('---', now_str)  # 시간 출력

        # 각 항목의 값을 범위 내 난수로 설정
        for key in self.env_values:
            self.env_values[key][1] = random.uniform(*self.env_values[key][0])

        # 로그 파일에 값 저장
        with open(log_file, 'a') as log:
            values = list(map(lambda x: str(f'{x[1]:.2f}'), self.env_values.values()))
            log.write(f'{now_str} | ' + ' | '.join(values) + '\n')

# 미션 컴퓨터 클래스 정의 mission 7의 문제는 여기서 부터 시작.
class MissionComputer:

    def __init__(self, env_values):
        self.env_values = env_values  # 환경 데이터를 저장
        self.stop_flag = False  # 종료 여부 플래그

    # 키 입력을 감지하여 'q' 입력 시 종료
    def key_listener(self):
        while True:
            key = input()
            if key == 'q': #내가 만약 q를 눌렀을 경우.
                print('종료 키 q 눌림')  # 사용자에게 알림
                self.stop_flag = True  # 종료 플래그 활성화
                break

    # 센서 데이터를 주기적으로 가져와 출력하고 평균을 계산
    def get_sensor_data(self, ds, interval=5, ave_interval_min=5): # 인터벌 : 몇초마다 가져오는지, ave : 평균 
        # 키보드 입력을 감지하는 스레드 시작
        listener_thread = threading.Thread(target=self.key_listener, daemon=True) #daemon = 메인 프로그램이 꺼지면, 스레드도 꺼지게 하는 옵션션
        listener_thread.start()

        # 총 루프 횟수 계산 (예: 5분 = 300초 / 5초 간격 = 60번)
        ave_values_sec = ave_interval_min * 60
        loop = ave_values_sec // interval

        while not self.stop_flag:
            print("\n환경 변수 업데이트:")
            ds.set_env()  # 센서로부터 새로운 값을 설정
            self.env_values = ds.get_env()  # 값을 받아옴

            # 환경 변수 출력 (현재값 + 허용 범위)
            for key in self.env_values.keys():
                print(f"{key}: {self.env_values[key][1]:.2f}, 허용범위 ({self.env_values[key][0][0]}~{self.env_values[key][0][1]})")

            # 누적 평균 계산용 로직
            if ave_values_sec > 0:
                ave_values_sec -= interval
                for key in self.env_values.keys():
                    self.env_values[key][2] += self.env_values[key][1]  # 누적합 저장
                    print(f"--- {key}: {self.env_values[key][2]:.2f})")  # 누적값 표시
            else:
                # 평균 출력 후 누적값 초기화
                for key in self.env_values.keys():
                    print(f"{ave_interval_min}분 평균 - {key}: {(self.env_values[key][2] / loop):.2f})")
                    self.env_values[key][2] = 0
                ave_values_sec = ave_interval_min * 60  # 다시 5분 초기화

            time.sleep(interval)  # interval 시간만큼 대기

        print("System stopped...")  # 종료 시 메시지 출력

# DummySensor 인스턴스 생성
ds = DummySensor(env_values)

# MissionComputer 인스턴스 생성
RunComputer = MissionComputer(env_values)

# 센서 데이터 수집 및 출력 시작
RunComputer.get_sensor_data(ds, interval=5)
