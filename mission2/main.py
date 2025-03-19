file_path = 'Mars_Base_Inventory_List.csv'

def read_csv(file_path):
    """CSV 파일을 읽어 리스트로 변환"""
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        headers = lines[0].strip().split(',')
        for line in lines[1:]:
            values = line.strip().split(',')
            try:
                flammability = float(values[-1])  # 마지막 열이 인화성 지수
                data.append((values[0], flammability))
            except ValueError:
                continue  # 변환 실패 시 건너뜀
    except Exception as e:
        print(f'파일을 읽는 중 오류 발생: {e}')
    return data

def sort_by_flammability(data):
    """인화성 지수를 기준으로 정렬"""
    return sorted(data, key=lambda x: x[1], reverse=True)

def filter_dangerous_materials(data, threshold=0.7):
    """인화성 지수가 기준 이상인 항목 필터링"""
    return [item for item in data if item[1] >= threshold]

def save_to_csv(data, file_name):
    """데이터를 CSV 형식으로 저장"""
    try:
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write('Substance,Flammability\n')
            for item in data:
                file.write(f'{item[0]},{item[1]}\n')
    except Exception as e:
        print(f'파일 저장 중 오류 발생: {e}')

def save_to_binary(data, file_name):
    """데이터를 이진 파일로 저장"""
    try:
        with open(file_name, 'wb') as file:
            for item in data:
                file.write(f'{item[0]},{item[1]}\n'.encode('utf-8'))
    except Exception as e:
        print(f'이진 파일 저장 중 오류 발생: {e}')

def read_from_binary(file_name):
    """이진 파일을 읽고 출력"""
    try:
        with open(file_name, 'rb') as file:
            content = file.read().decode('utf-8')
            print(content)
    except Exception as e:
        print(f'이진 파일 읽기 중 오류 발생: {e}')

# 실행
inventory_data = read_csv(file_path)
sorted_data = sort_by_flammability(inventory_data)
dangerous_materials = filter_dangerous_materials(sorted_data)

# 위험 물질 목록 출력
print('🔥 인화성 지수 0.7 이상 위험 물질 목록:')
for item in dangerous_materials:
    print(f'- {item[0]} (인화성: {item[1]})')

# 위험 물질 목록 저장
dangerous_file_path = 'Mars_Base_Inventory_danger.csv'
save_to_csv(dangerous_materials, dangerous_file_path)

# 이진 파일 저장 및 읽기
binary_file_path = 'Mars_Base_Inventory_List.bin'
save_to_binary(sorted_data, binary_file_path)
read_from_binary(binary_file_path)

# 결과 출력
print(f'인화성 높은 순 정렬 데이터: {sorted_data[:5]}')
print(f'위험 물질 목록 저장 완료: {dangerous_file_path}')
print(f'이진 파일 저장 완료: {binary_file_path}')
