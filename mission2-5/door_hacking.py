import time
import zipfile
import io
from multiprocessing import Process, current_process, Manager, cpu_count
from itertools import product

charset = 'abcdefghijklmnopqrstuvwxyz0123456789'
zip_file = 'emergency_storage_key.zip'

def try_password(start_char_idx, zip_bytes, found_event, result):
    start_time = time.time()
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    fname = zf.namelist()[0]

    start_char = charset[start_char_idx]
    print(f"[{current_process().name}] 시작: 첫 글자 '{start_char}'부터 시도 중...")

    count = 0
    for suffix in product(charset, repeat=5):
        if found_event.is_set():
            return

        password = start_char + ''.join(suffix)
        count += 1

        if count % 100000 == 0:
            print(f"[{current_process().name}] 진행 중... 현재 시도: {password} ({count:,}회차)")

        try:
            with zf.open(fname, 'r', pwd=password.encode()) as file:
                file.read(1)
                print(f"[{current_process().name}] ✅ 정답 찾음: {password}")
                with open("password.txt", "w") as f:
                    f.write(password)
                result['password'] = password
                print(f"⏱️ 소요 시간: {time.time() - start_time:.2f}초")
                found_event.set()
                return
        except:
            continue

def unlock_zip():
    start_time = time.time()

    with open(zip_file, 'rb') as f:
        zip_bytes = f.read()

    manager = Manager()
    found_event = manager.Event()
    result = manager.dict()

    num_processes = cpu_count()
    print(f"총 사용 가능한 코어 수: {num_processes}")
    print("🔓 암호 해제를 시작합니다...\n")

    procs = []
    for i in range(len(charset)):
        if i % num_processes == 0 and i > 0:
            for p in procs:
                p.start()
            for p in procs:
                p.join()
            if found_event.is_set():
                break
            procs = []

        p = Process(target=try_password, args=(i, zip_bytes, found_event, result))
        procs.append(p)

    # 남은 프로세스 실행
    for p in procs:
        p.start()
    for p in procs:
        p.join()

    print("\n✅ 최종 종료 시간:", time.time())
    print("⏱️ 총 소요 시간:", time.time() - start_time)
    if 'password' in result:
        print("🔐 찾은 비밀번호:", result['password'])
    else:
        print("❌ 비밀번호를 찾지 못했습니다.")

if __name__ == "__main__":
    unlock_zip()
