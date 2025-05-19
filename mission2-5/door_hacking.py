import time
import zipfile
import io
from multiprocessing import Pool, current_process

# 전역 변수 설정
charset = 'abcdefghijklmnopqrstuvwxyz0123456789'
zip_file = 'emergency_storage_key.zip'

def try_password(start_idx):
    """각 프로세스가 시도할 비밀번호 조합"""
    # 6자리 비밀번호 시작 인덱스를 기반으로 프로세스별 분배
    start_time = time.time()

    # ZIP 파일을 메모리로 로딩
    with open(zip_file, 'rb') as f:
        zip_data = io.BytesIO(f.read())

    # ZIP 파일 열기
    zf = zipfile.ZipFile(zip_data, 'r')

    # 압축 파일 이름 목록(첫 번쨰 파일 이름) 
    fname = zf.namelist()[0]

    # 6자리 비밀번호 시도
    for i in range(start_idx, len(charset), 4):  # 4개의 프로세스로 분배
        for c2 in charset:
            for c3 in charset:
                for c4 in charset:
                    for c5 in charset:
                        for c6 in charset:
                            password = f"{charset[i]}{c2}{c3}{c4}{c5}{c6}"
                            try:
                                # 파일 열기 시도
                                with zf.open(fname, 'r', pwd=password.encode()) as file:
                                    file.read(1)  # 파일이 정상인지 최소 1바이트 읽기
                                    print(f"정답 찾음: {password}")

                                    # 찾은 password를 password.txt에 저장
                                    with open("password.txt", "w") as f:
                                        f.write(password)

                                    print(f"총 소요 시간: {time.time() - start_time}")
                                    return password
                            except:
                                continue
    return None


def unlock_zip():
    # 시작 시간 측정
    start_time = time.time()
    print('시작 시간:', start_time)

    # 멀티프로세싱 Pool 생성, 시스템 CPU core 수 만큼 프로세스 생성
    with Pool() as pool:
        # 각 프로세스에 대해 시작 인덱스를 나누어서 작업 분배
        tasks = [i for i in range(4)]
        results = pool.map(try_password, tasks)

        # 결과 확인
        print('---', results)

    print('최종 종료 시간:', time.time())
    print('총 소요 시간:', time.time() - start_time)
    return None


if __name__ == "__main__":
    unlock_zip()
