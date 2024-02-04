from flask import Flask, render_template, Response
import pika
import json

def create_connection():
    # Создание соединения с RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    return connection

def create_channel(connection):
    # Создание канала
    channel = connection.channel()
    channel.exchange_declare(exchange='train_num', exchange_type='fanout')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='train_num', queue=queue_name)

    return channel, queue_name

def create_app(channel, queue_name):
    # Создание объекта Flask
    app = Flask(__name__)

    @app.route('/')
    def index():
        # Отображение главной страницы
        return render_template('index.html')

    @app.route('/stream')
    def stream():
        # Генерация событий для сервера с использованием Server-Sent Events
        def generate():
            for method_frame, properties, body in channel.consume(queue_name, inactivity_timeout=1):
                if body is not None:
                    data = json.loads(body)
                    yield f"data: {json.dumps(data)}\n\n"

        return Response(generate(), mimetype='text/event-stream')

    return app

def main():
    # Основная функция
    connection = create_connection()
    channel, queue_name = create_channel(connection)

    app = create_app(channel, queue_name)

    if __name__ == '__main__':
        # Запуск сервера Flask в режиме отладки
        app.run(debug=True)

if __name__ == '__main__':
    main()
