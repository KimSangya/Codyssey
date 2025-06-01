import os  # 파일 및 폴더 경로 조작을 위한 표준 라이브러리
import csv  # CSV 파일을 읽고 쓰기 위한 표준 라이브러리
import speech_recognition as sr  # 음성을 텍스트로 변환하는 외부 라이브러리 (문제에서 STT는 허용됨)

# WAV 오디오 파일을 텍스트로 변환하는 함수
def convert_audio_to_text(file_path):
    recognizer = sr.Recognizer()  # 음성 인식기 객체 생성
    with sr.AudioFile(file_path) as source:  # 지정된 WAV 파일 열기
        audio_data = recognizer.record(source)  # 전체 음성 데이터를 한 번에 읽기
        try:
            # 구글 STT API를 이용해 텍스트로 변환 (언어는 한국어)
            text = recognizer.recognize_google(audio_data, language='ko-KR')
            return text  # 변환된 텍스트 반환
        except sr.UnknownValueError:
            return '인식 실패'  # 음성을 제대로 이해하지 못한 경우
        except sr.RequestError:
            return 'API 오류'  # API 서버 또는 네트워크 오류

# 변환된 텍스트를 같은 이름의 CSV 파일로 저장하는 함수
def save_text_to_csv(wav_file):
    base_name = os.path.splitext(wav_file)[0]  # 확장자 제거한 파일 이름 추출
    csv_file = base_name + '.csv'  # .csv 확장자 붙이기
    wav_path = os.path.join('records', wav_file)  # 원본 WAV 파일 경로
    csv_path = os.path.join('records', csv_file)  # 저장할 CSV 파일 경로

    text = convert_audio_to_text(wav_path)  # 오디오를 텍스트로 변환

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:  # CSV 파일 쓰기 모드로 열기
        writer = csv.writer(f)  # CSV writer 객체 생성
        writer.writerow(['시간', '텍스트'])  # 첫 줄: 헤더
        writer.writerow(['00:00', text])  # 두 번째 줄: 시간(00:00)과 변환된 텍스트

    print(f'{csv_file} 저장 완료.')  # 저장 완료 메시지 출력

# records 폴더 내 모든 WAV 파일을 처리하는 함수
def process_all_wav_files():
    folder = 'records'  # 대상 폴더 이름

    if not os.path.exists(folder):  # 폴더가 존재하지 않으면
        print('records 폴더가 없습니다.')  # 경고 메시지 출력
        return  # 함수 종료

    for filename in os.listdir(folder):  # 폴더 내 모든 파일에 대해 반복
        if filename.endswith('.wav'):  # .wav 파일만 선택
            print(f'{filename} 처리 중...')  # 현재 파일 출력
            save_text_to_csv(filename)  # WAV 파일을 CSV로 변환 및 저장

# CSV 파일들 안에서 특정 키워드를 검색하는 함수 (보너스 기능)
def search_keyword_in_csv(keyword):
    folder = 'records'  # 검색할 대상 폴더
    found = False  # 키워드 발견 여부를 저장할 변수

    for filename in os.listdir(folder):  # 폴더 내 파일 반복
        if filename.endswith('.csv'):  # .csv 파일만 선택
            path = os.path.join(folder, filename)  # 전체 경로 생성
            with open(path, newline='', encoding='utf-8') as f:  # 파일 열기
                reader = csv.reader(f)  # CSV reader 객체 생성
                next(reader)  # 헤더 건너뜀

                for row in reader:  # 각 행 반복
                    if keyword in row[1]:  # 텍스트 열에서 키워드 검색
                        print(f'[검색 결과] {filename} - {row[0]}: {row[1]}')  # 결과 출력
                        found = True  # 키워드 발견 표시

    if not found:  # 결과가 없을 경우
        print('키워드가 포함된 결과를 찾지 못했습니다.')

# 메인 실행 블록
if __name__ == '__main__':
    process_all_wav_files()  # 모든 .wav 파일을 처리하여 .csv로 저장

    keyword = input('검색할 키워드를 입력하세요: ')  # 사용자로부터 키워드 입력 받기
    search_keyword_in_csv(keyword)  # 입력한 키워드로 모든 CSV 파일 검색
