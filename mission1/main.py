def read_log_file(filename): #각 함수 설정
    """로그 파일을 읽어 리스트로 반환하는 함수"""
    try: # try except 예외처리 
        with open(filename, 'r', encoding='utf-8') as file:
            logs = file.readlines() # 로그 파일을 읽어서 리스트로 반환하는 친구
            return logs
    except FileNotFoundError: # 파일이 없다면 다시 실행
        print('Error: Log file not found.')
        return []

"""
    # 로그를 시간대로 출력하는 함수
    def print_logs(logs):
    for log in logs:
        print(log.strip())
"""

def print_logs_in_reverse(logs):
    """로그를 시간의 역순으로 출력하는 함수"""
    for log in reversed(logs): # 파일을 최신순으로 출력
        print(log.strip()) #개행 문자 제거 후 출력 (시작과 끝 문자를 제거하는 부분)

def extract_error_logs(logs, error_keywords):
    """오류 관련 로그만 필터링하는 함수"""
    error_logs = [log for log in logs if any(keyword in log for keyword in error_keywords)]
    return error_logs

def save_error_logs(filename, error_logs):
    """필터링된 오류 로그를 파일로 저장하는 함수"""
    with open(filename, 'w', encoding='utf-8') as file:
        file.writelines(error_logs)

def main():
    """메인 실행 함수"""
    print('Hello Mars')  # Python 설치 확인을 위한 출력

    log_filename = 'mission_computer_main.log'
    logs = read_log_file(log_filename)
    
    if logs:
        # 반대로 읽기 시작하는 부분
        print_logs_in_reverse(logs)

        # 특정 키워드가 포함된 로그만 필터링
        error_keywords = ['unstable', 'explosion']
        error_logs = extract_error_logs(logs, error_keywords)

        if error_logs:
            error_log_filename = 'error_logs.txt'
            save_error_logs(error_log_filename, error_logs)
            print(f'Error logs saved to {error_log_filename}')

if __name__ == '__main__': # 파일이 직접 실행될때 사용.
    main()
