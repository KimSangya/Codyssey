import json  # JSON 형식으로 출력하기 위한 모듈
import platform  # 운영체제 및 CPU 등의 정보 확인을 위한 모듈
import psutil  # 시스템 리소스 정보(CPU, 메모리 등) 수집을 위한 외부 라이브러리


class MissionComputer:  # 미션 컴퓨터 클래스 정의

    def __init__(self, env_values):  # 클래스 초기화 메서드
        self.env_values = env_values  # 센서 환경 값 저장
        self.stop_flag = False  # 'q' 입력 시 루프 종료를 위한 플래그

    def key_listener(self):  # 키보드 입력 감지 메서드
        while True:  # 무한 루프
            key = input()  # 사용자 입력 받기
            if key == 'q':  # 입력이 'q'일 경우
                print('종료 키 q 눌림')  # 종료 알림 출력
                self.stop_flag = True  # 종료 플래그 설정
                break  # 루프 종료

    def get_sensor_data(self, ds, interval=5, ave_interval_min=5):  # 센서 데이터 수집 메서드
        import threading  # 키 입력 감지 스레드를 위한 모듈
        import time  # 주기적 대기를 위한 모듈

        listener_thread = threading.Thread(target=self.key_listener, daemon=True)  # 키 리스너 스레드 생성
        listener_thread.start()  # 스레드 시작

        ave_values_sec = ave_interval_min * 60  # 평균 계산용 총 초
        loop = ave_values_sec // interval  # 몇 번 반복할지 계산

        while not self.stop_flag:  # 종료 플래그가 꺼질 때까지 루프
            print('\n환경 변수 업데이트:')  # 갱신 알림 출력
            ds.set_env()  # 센서 값 설정
            self.env_values = ds.get_env()  # 센서 값 가져오기

            for key in self.env_values.keys():  # 모든 환경 변수에 대해
                print(f"{key}: {self.env_values[key][1]:.2f}, "
                      f"허용범위 ({self.env_values[key][0][0]}~{self.env_values[key][0][1]})")  # 현재값과 허용범위 출력

            if ave_values_sec > 0:  # 평균 계산 중이라면
                ave_values_sec -= interval  # 시간 차감
                for key in self.env_values.keys():  # 모든 변수에 대해
                    self.env_values[key][2] += self.env_values[key][1]  # 누적합 저장
                    print(f"--- {key}: {self.env_values[key][2]:.2f})")  # 누적값 출력
            else:  # 평균 계산이 끝났다면
                for key in self.env_values.keys():  # 변수별 평균 출력
                    print(f"{ave_interval_min}분 평균 - {key}: "
                          f"{(self.env_values[key][2] / loop):.2f})")  # 평균 계산 후 출력
                    self.env_values[key][2] = 0  # 누적 초기화
                ave_values_sec = ave_interval_min * 60  # 평균 시간 초기화

            time.sleep(interval)  # interval 초 대기

        print("System stopped...")  # 종료 메시지 출력

    def get_mission_computer_info(self):  # 시스템 정보 수집 메서드
        info = {}  # 결과 저장용 딕셔너리

        try:  # 예외 처리
            info['os'] = platform.system()  # 운영체제 이름
            info['os_version'] = platform.version()  # 운영체제 버전
            info['cpu_type'] = platform.processor()  # CPU 종류
            info['cpu_count'] = psutil.cpu_count(logical=True)  # 논리 코어 수
            info['memory'] = f"{round(psutil.virtual_memory().total / (1024 ** 2))} MB"  # 전체 메모리(MB)
        except Exception as e:  # 예외 발생 시
            print(f"시스템 정보 수집 중 오류 발생: {e}")  # 오류 출력

        info = self.filter_output(info)  # setting.txt 기준으로 필터링

        print('[미션 컴퓨터 시스템 정보]')  # 헤더 출력
        print(json.dumps(info, indent=4))  # JSON 형식 출력

    def get_mission_computer_load(self):  # 실시간 시스템 부하 수집 메서드
        load = {}  # 결과 저장용 딕셔너리

        try:  # 예외 처리
            load['cpu_usage_percent'] = psutil.cpu_percent(interval=1)  # CPU 사용량(%)
            load['memory_usage_percent'] = psutil.virtual_memory().percent  # 메모리 사용량(%)
        except Exception as e:  # 예외 발생 시
            print(f"부하 정보 수집 중 오류 발생: {e}")  # 오류 출력

        load = self.filter_output(load)  # setting.txt 기준으로 필터링

        print('[미션 컴퓨터 실시간 부하 정보]')  # 헤더 출력
        print(json.dumps(load, indent=4))  # JSON 형식 출력

    def filter_output(self, data):  # setting.txt 기준 출력 필터링 함수
        try:  # 파일 읽기 시 예외 처리
            with open('setting.txt', 'r') as f:  # setting.txt 열기
                settings = [line.strip() for line in f if line.strip()]  # 빈 줄 제거 및 공백 제거
                return {k: v for k, v in data.items() if k in settings}  # 설정된 항목만 반환
        except FileNotFoundError:  # 파일이 없을 경우
            return data  # 전체 출력


runComputer = MissionComputer(env_values={})  # MissionComputer 인스턴스 생성

runComputer.get_mission_computer_info()  # 시스템 정보 출력

runComputer.get_mission_computer_load()  # 부하 정보 출력
