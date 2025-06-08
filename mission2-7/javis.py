import os  # 폴더 생성, 경로 조작 등 파일 시스템 작업에 사용
import wave  # 녹음된 데이터를 WAV 오디오 파일로 저장하는 데 사용
import datetime  # 날짜 및 시간 정보 처리에 사용
import pyaudio  # 마이크로부터 오디오 입력을 받기 위한 외부 라이브러리


class Recorder:
    def __init__(self):
        self.folder = 'records'  # 녹음 파일을 저장할 폴더 이름
        self.filename = ''  # 녹음될 파일의 이름 (자동 생성 예정)
        self.duration = 5  # 녹음 시간(초) 설정
        self.rate = 16000  # 샘플링 레이트 설정 (1초당 샘플 수)
        self.channels = 1  # 채널 수 설정: 1=모노, 2=스테레오
        self.format = pyaudio.paInt16  # 오디오 포맷 설정 (16비트 정수형)
        self.device_index = None  # 사용할 마이크 장치 번호 (초기값은 None)

    def create_folder(self):
        if not os.path.exists(self.folder):  # 폴더가 없으면
            os.makedirs(self.folder)  # 폴더를 생성

    def generate_filename(self):
        now = datetime.datetime.now()  # 현재 날짜 및 시간 가져오기
        self.filename = now.strftime('%Y%m%d-%H%M%S') + '.wav'  # 파일명 형식 지정
        return os.path.join(self.folder, self.filename)  # 전체 경로 반환

    def list_input_devices(self):
        audio = pyaudio.PyAudio()  # PyAudio 인스턴스 생성
        print('사용 가능한 입력 장치 목록:')
        for i in range(audio.get_device_count()):  # 모든 오디오 장치 순회
            info = audio.get_device_info_by_index(i)  # 각 장치 정보 가져오기
            if info['maxInputChannels'] > 0:  # 입력 채널이 있는 장치만 출력
                print(f"{i}: {info['name']} (채널 수: {info['maxInputChannels']})")
        audio.terminate()  # PyAudio 인스턴스 종료

    def record_audio(self):
        self.create_folder()  # records 폴더 없으면 생성
        filepath = self.generate_filename()  # 저장할 파일 경로 생성

        audio = pyaudio.PyAudio()  # PyAudio 인스턴스 생성

        if self.device_index is None:  # 마이크 장치 번호가 설정되지 않았다면
            self.list_input_devices()  # 사용 가능한 장치 목록 출력
            self.device_index = int(input('사용할 입력 장치 번호를 입력하세요: '))  # 사용자에게 입력 받기

        # 마이크 입력 스트림 열기
        stream = audio.open(
            format=self.format,  # 오디오 포맷 (16비트)
            channels=self.channels,  # 채널 수 (모노)
            rate=self.rate,  # 샘플링 레이트 (16000Hz)
            input=True,  # 입력 장치 사용
            input_device_index=self.device_index,  # 선택한 장치 사용
            frames_per_buffer=1024  # 버퍼 크기 설정
        )

        print('녹음 시작...')
        frames = []  # 녹음 데이터를 저장할 리스트

        for _ in range(0, int(self.rate / 1024 * self.duration)):  # 녹음 시간만큼 루프
            data = stream.read(1024)  # 버퍼 크기만큼 마이크로부터 읽기
            frames.append(data)  # 데이터를 프레임 리스트에 저장

        print('녹음 완료. 저장 중...')

        stream.stop_stream()  # 스트림 중지
        stream.close()  # 스트림 종료
        audio.terminate()  # PyAudio 인스턴스 종료

        # WAV 파일로 저장
        with wave.open(filepath, 'wb') as wf:  # 저장 파일 열기 (쓰기 모드)
            wf.setnchannels(self.channels)  # 채널 수 설정
            wf.setsampwidth(audio.get_sample_size(self.format))  # 샘플 폭 설정
            wf.setframerate(self.rate)  # 샘플링 레이트 설정
            wf.writeframes(b''.join(frames))  # 모든 오디오 데이터를 파일에 기록

        print('파일 저장 완료:', filepath)  # 저장 완료 메시지 출력


def show_recordings(start_date, end_date):
    folder = 'records'  # 녹음 파일 폴더 경로

    if not os.path.exists(folder):  # 폴더가 없다면
        print('records 폴더가 존재하지 않습니다.')
        return

    print('녹음 파일 목록:')
    for filename in os.listdir(folder):  # 폴더 안의 파일 모두 확인
        if filename.endswith('.wav'):  # .wav 파일만 필터링
            file_date = filename.split('.')[0]  # 파일 이름에서 날짜 추출
            try:
                file_dt = datetime.datetime.strptime(file_date, '%Y%m%d-%H%M%S')  # 문자열을 datetime 객체로 변환
                if start_date <= file_dt <= end_date:  # 날짜 범위에 포함된다면
                    print(' -', filename)  # 파일 이름 출력
            except ValueError:
                continue  # 날짜 형식이 잘못되었으면 무시


if __name__ == '__main__':
    recorder = Recorder()  # Recorder 클래스 인스턴스 생성
    recorder.record_audio()  # 녹음 기능 실행

    # 보너스 기능 (주석 해제 시 사용 가능)
    # start = datetime.datetime(2025, 5, 1)
    # end = datetime.datetime(2025, 5, 31)
    # show_recordings(start, end)  # 해당 날짜 범위 내 녹음 파일 출력
