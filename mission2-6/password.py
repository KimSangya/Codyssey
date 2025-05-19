def caesar_cipher_decode(target_text):
    """
    카이사르 암호 복호화 함수: 알파벳을 왼쪽으로 시프트하여 복호화된 결과 출력
    """
    for shift in range(26):
        decoded = ''
        for char in target_text:
            if 'a' <= char <= 'z':
                decoded += chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
            elif 'A' <= char <= 'Z':
                decoded += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            else:
                decoded += char
        print(f'[{shift}] {decoded}')

        # 보너스 과제: 간단한 단어 사전
        common_words = ['the', 'and', 'this', 'that', 'secret', 'password']
        for word in common_words:
            if word in decoded.lower():
                print('자동 탐지됨: 추정 키 =', shift)
                return shift, decoded
    return None, None


def main():
    try:
        with open('password.txt', 'r') as file:
            encrypted_text = file.read().strip()
    except FileNotFoundError:
        print('password.txt 파일이 존재하지 않습니다.')
        return
    except Exception as e:
        print('파일 읽기 중 오류:', e)
        return

    shift_value, guessed_text = caesar_cipher_decode(encrypted_text)

    if guessed_text:
        try:
            with open('result.txt', 'w') as result_file:
                result_file.write(guessed_text)
            print('자동 탐지된 결과를 result.txt에 저장했습니다.')
        except Exception as e:
            print('파일 저장 중 오류:', e)
    else:
        try:
            chosen = int(input('위 결과 중 정답으로 보이는 번호를 입력하세요: '))
        except ValueError:
            print('숫자를 입력해주세요.')
            return

        if not (0 <= chosen <= 25):
            print('0부터 25 사이의 숫자만 입력 가능합니다.')
            return

        decoded_final = ''
        for char in encrypted_text:
            if 'a' <= char <= 'z':
                decoded_final += chr((ord(char) - ord('a') - chosen) % 26 + ord('a'))
            elif 'A' <= char <= 'Z':
                decoded_final += chr((ord(char) - ord('A') - chosen) % 26 + ord('A'))
            else:
                decoded_final += char

        try:
            with open('result.txt', 'w') as result_file:
                result_file.write(decoded_final)
            print('선택한 결과를 result.txt에 저장했습니다.')
        except Exception as e:
            print('파일 저장 중 오류:', e)


if __name__ == '__main__':
    main()
