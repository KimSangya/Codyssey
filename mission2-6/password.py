def caesar_cipher_decode(target_text):
    decoded_texts = []
    
    for shift in range(1, 27):  # 1부터 26까지 시프트를 시도
        decoded_text = ''
        for char in target_text:
            if char.isalpha():  # 알파벳인 경우만 복호화
                # 대문자 처리
                if char.isupper():
                    decoded_text += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
                # 소문자 처리
                elif char.islower():
                    decoded_text += chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
            else:
                decoded_text += char  # 알파벳이 아닌 문자는 그대로 추가
        
        decoded_texts.append(decoded_text)  # 복호화된 텍스트를 저장

    return decoded_texts  # 모든 복호화된 텍스트 리스트를 반환

def save_result(decoded_text):
    try:
        with open('result.txt', 'w') as f:
            f.write(decoded_text)
        print('결과가 result.txt 파일에 저장되었습니다.')
    except Exception as e:
        print(f'파일 저장 중 오류가 발생했습니다: {e}')

# 파일 읽기
try:
    with open('password.txt', 'r') as file:
        target_text = file.read().strip()
except FileNotFoundError:
    print('password.txt 파일을 찾을 수 없습니다.')

# 암호 해독
decoded_texts = caesar_cipher_decode(target_text)

# 복호화된 텍스트 출력 및 확인
for idx, decoded_text in enumerate(decoded_texts, 1):
    print(f'{idx}번째 시프트: {decoded_text}')

# 사용자가 눈으로 확인한 후 번호 입력
selected_shift = int(input('어떤 번호의 복호화된 텍스트가 올바른지 입력하세요 (1~26): '))

# 해당 번호의 결과를 result.txt에 저장
if 1 <= selected_shift <= 26:
    save_result(decoded_texts[selected_shift - 1])  # 번호는 1부터 시작하므로 -1 해주어야 합니다.
else:
    print('잘못된 번호입니다. 1부터 26 사이의 숫자를 입력해주세요.')
