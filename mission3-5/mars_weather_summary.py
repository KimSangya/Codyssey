import mysql.connector
from datetime import datetime


class MySQLHelper:
    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()

    def create_table(self):
        query = (
            'CREATE TABLE IF NOT EXISTS mars_weather ('
            'weather_id INT AUTO_INCREMENT PRIMARY KEY, '
            'mars_date DATETIME NOT NULL, '
            'temp INT, '
            'storm INT'
            ')'
        )
        self.cursor.execute(query)
        self.connection.commit()

    def insert_weather(self, mars_date, temp, storm):
        query = (
            'INSERT INTO mars_weather (mars_date, temp, storm) '
            'VALUES (%s, %s, %s)'
        )
        self.cursor.execute(query, (mars_date, temp, storm))
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()


def read_csv_and_insert(helper, csv_path):
    with open(csv_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

        for index, line in enumerate(lines):
            if index == 0:
                continue  # skip header

            parts = line.strip().split(',')

            if len(parts) < 4:
                continue  # invalid line

            date_str = parts[1].strip()
            temp_str = parts[2].strip()
            storm_str = parts[3].strip()

            try:
                mars_date = datetime.strptime(date_str, '%Y-%m-%d')
                temp = int(float(temp_str))  # 소수점 버림
                storm = int(storm_str)
                helper.insert_weather(mars_date, temp, storm)
            except Exception as e:
                print('에러:', e, '| 데이터:', parts)
                continue  # skip invalid data


def main():
    host = 'localhost'
    user = 'root'
    password = '-' # 자신의 DB내용
    database = 'weather'

    helper = MySQLHelper(host, user, password, database)
    helper.create_table()
    read_csv_and_insert(helper, 'mars_weathers_data.csv')
    helper.close()


if __name__ == '__main__':
    main()
