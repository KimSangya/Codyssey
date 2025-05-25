import os
import wave
import datetime
import pyaudio


class Recorder:
    def __init__(self):
        self.folder = 'records'
        self.filename = ''
        self.duration = 5  # 초 단위 녹음 시간
        self.rate = 16000  # 호환성 고려해 16000Hz로 변경
        self.channels = 1
        self.format = pyaudio.paInt16
        self.device_index = None  # 사용할 마이크 장치 번호

    def create_folder(self):
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def generate_filename(self):
        now = datetime.datetime.now()
        self.filename = now.strftime('%Y%m%d-%H%M%S') + '.wav'
        return os.path.join(self.folder, self.filename)

    def list_input_devices(self):
        audio = pyaudio.PyAudio()
        print('사용 가능한 입력 장치 목록:')
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"{i}: {info['name']} (채널 수: {info['maxInputChannels']})")
        audio.terminate()

    def record_audio(self):
        self.create_folder()
        filepath = self.generate_filename()

        audio = pyaudio.PyAudio()

        if self.device_index is None:
            self.list_input_devices()
            self.device_index = int(input('사용할 입력 장치 번호를 입력하세요: '))

        stream = audio.open(format=self.format,
                            channels=self.channels,
                            rate=self.rate,
                            input=True,
                            input_device_index=self.device_index,
                            frames_per_buffer=1024)

        print('녹음 시작...')
        frames = []

        for _ in range(0, int(self.rate / 1024 * self.duration)):
            data = stream.read(1024)
            frames.append(data)

        print('녹음 완료. 저장 중...')

        stream.stop_stream()
        stream.close()
        audio.terminate()

        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))

        print('파일 저장 완료:', filepath)


def show_recordings(start_date, end_date):
    folder = 'records'
    if not os.path.exists(folder):
        print('records 폴더가 존재하지 않습니다.')
        return

    print('녹음 파일 목록:')
    for filename in os.listdir(folder):
        if filename.endswith('.wav'):
            file_date = filename.split('.')[0]
            try:
                file_dt = datetime.datetime.strptime(file_date, '%Y%m%d-%H%M%S')
                if start_date <= file_dt <= end_date:
                    print(' -', filename)
            except ValueError:
                continue


if __name__ == '__main__':
    recorder = Recorder()
    recorder.record_audio()

    # 보너스 기능: 날짜 범위 녹음 파일 보기
    # start = datetime.datetime(2025, 5, 1)
    # end = datetime.datetime(2025, 5, 31)
    # show_recordings(start, end)
