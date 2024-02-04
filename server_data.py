import pika
import random
import time
import json
from datetime import datetime
import psycopg2

def setup_rabbitmq():
    # Устанавливаем соединение с RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='train_num', exchange_type='fanout')
    return connection, channel

def setup_postgres():
    # Устанавливаем соединение с PostgreSQL
    db_connection = psycopg2.connect(
        host='localhost',
        user='postgres',
        password='12345',
        database='Train'
    )
    db_cursor = db_connection.cursor()
    return db_connection, db_cursor

def send_train_data(channel):
    # Генерируем случайные данные поезда и отправляем их в RabbitMQ
    entrance_track = random.randint(1, 2)
    exit_track = random.randint(1, 2)
    train_length = random.randint(1, 4)
    timestamp = datetime.now()

    data = {'входной парк': entrance_track,
            'выходной парк': exit_track,
            'длина поезда': train_length}

    json_data = json.dumps(data)

    channel.basic_publish(exchange='train_num', routing_key='', body=json_data)
    print(f"Отправлено: {json_data}")

def log_train_data(db_cursor, entrance_track, exit_track, train_length, timestamp):
    # Записываем данные поезда в базу данных PostgreSQL
    db_cursor.execute("INSERT INTO train_logs (entrance_track, exit_track, train_length, timestamp) VALUES (%s, %s, %s, %s)",
                      (entrance_track, exit_track, train_length, timestamp))
    db_cursor.connection.commit()

def main():
    # Инициализация RabbitMQ и PostgreSQL
    rabbitmq_connection, rabbitmq_channel = setup_rabbitmq()
    postgres_connection, postgres_cursor = setup_postgres()

    try:
        while True:
            # Генерация, отправка и логирование данных поезда
            entrance_track = random.randint(1, 2)
            exit_track = random.randint(1, 2)
            train_length = random.randint(1, 4)
            timestamp = datetime.now()

            send_train_data(rabbitmq_channel)
            log_train_data(postgres_cursor, entrance_track, exit_track, train_length, timestamp)

            time.sleep(4)

    except KeyboardInterrupt:
        print("Программа завершена по запросу пользователя.")
    finally:
        # Закрытие соединений при завершении программы
        rabbitmq_connection.close()
        postgres_cursor.close()
        postgres_connection.close()

if __name__ == "__main__":
    main()
