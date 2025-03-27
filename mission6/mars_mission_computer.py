import random  # ✅ random은 허용됨

class DummySensor:
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
        log_entry = f"{self.env_values['mars_base_internal_temperature']:.2f}, " \
                    f"{self.env_values['mars_base_external_temperature']:.2f}, " \
                    f"{self.env_values['mars_base_internal_humidity']:.2f}, " \
                    f"{self.env_values['mars_base_external_illuminance']:.2f}, " \
                    f"{self.env_values['mars_base_internal_co2']:.4f}, " \
                    f"{self.env_values['mars_base_internal_oxygen']:.2f}\n"

        with open('sensor_log.txt', 'a') as log_file:
            log_file.write(log_entry)

        return self.env_values

# 인스턴스 생성
ds = DummySensor()

# 환경 값 설정 및 확인
ds.set_env()
env_data = ds.get_env()
print(env_data)
