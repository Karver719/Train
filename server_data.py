import pika
import random
import time
import json
from datetime import datetime
import psycopg2

# Подключение к RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Объявление обменника
channel.exchange_declare(exchange='train_num', exchange_type='fanout')

# Подключение к PostgreSQL
db_connection = psycopg2.connect(
    host='localhost',
    user='postgres',
    password='12345',
    database='Train'
)
db_cursor = db_connection.cursor()

while True:
    # Генерация рандомного числа
    entrance_track = random.randint(1, 2)
    exit_track = random.randint(1, 2)
    train_length = random.randint(1, 4)
    timestamp = datetime.now()

    # Создание словаря
    data = {'входной парк': entrance_track,
            'выходной парк': exit_track,
            'длина поезда': train_length}

    # Преобразование словаря в строку JSON
    json_data = json.dumps(data)

    # Отправка JSON на обменник
    channel.basic_publish(exchange='train_num', routing_key='', body=json_data)
    print(f"Отправлено: {json_data}")

    # Запись данных в PostgreSQL
    db_cursor.execute("INSERT INTO train_logs (entrance_track, exit_track, train_length, timestamp) VALUES (%s, %s, %s, %s)",
                      (entrance_track, exit_track, train_length, timestamp))
    db_connection.commit()

    # Задержка в секундах (может быть изменено в зависимости от требований)
    time.sleep(1)

# Закрытие соединения
connection.close()
