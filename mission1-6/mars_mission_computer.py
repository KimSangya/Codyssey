import random

class DummySensor: # class 생성 및 변수 추가.
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }

    def set_env(self): 
        self.env_values['mars_base_internal_temperature'] = random.uniform(18, 30)
        self.env_values['mars_base_external_temperature'] = random.uniform(0, 21)
        self.env_values['mars_base_internal_humidity'] = random.uniform(50, 60)
        self.env_values['mars_base_external_illuminance'] = random.uniform(500, 715)
        self.env_values['mars_base_internal_co2'] = random.uniform(0.02, 0.1)
        self.env_values['mars_base_internal_oxygen'] = random.uniform(4, 7)

    def get_env(self):
        filename = 'sensor_log.txt'

        # 파일을 열어서 첫 줄 확인 (헤더가 있는지 확인)
        header = "Timestamp, Internal Temperature, External Temperature, Internal Humidity, External Illuminance, Internal CO2, Internal Oxygen\n"
        try:
            with open(filename, 'r') as log_file:
                first_line = log_file.readline()
        except FileNotFoundError:
            first_line = ""

        # 헤더가 없으면 추가
        with open(filename, 'a') as log_file:
            if first_line.strip() != header.strip():
                log_file.write(header)

        # 랜덤 날짜 생성 (연도는 2025로 고정)
        year = 2025
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        timestamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(year, month, day, hour, minute, second)

        log_entry = f"{timestamp}, " \
                    f"{self.env_values['mars_base_internal_temperature']:.2f}, " \
                    f"{self.env_values['mars_base_external_temperature']:.2f}, " \
                    f"{self.env_values['mars_base_internal_humidity']:.2f}, " \
                    f"{self.env_values['mars_base_external_illuminance']:.2f}, " \
                    f"{self.env_values['mars_base_internal_co2']:.4f}, " \
                    f"{self.env_values['mars_base_internal_oxygen']:.2f}\n"

        with open(filename, 'a') as log_file:
            log_file.write(log_entry)

        return self.env_values

# 인스턴스 생성
ds = DummySensor()

# 환경 값 설정 및 확인
ds.set_env()
env_data = ds.get_env()
print(env_data)
