from flask import Flask, render_template
import pika
import json

app = Flask(__name__)

# Подключение к RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Объявление обменника
channel.exchange_declare(exchange='train_num', exchange_type='fanout')

# Создание временной очереди
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# Привязка очереди к обменнику
channel.queue_bind(exchange='train_num', queue=queue_name)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream():
    def generate():
        for method_frame, properties, body in channel.consume(queue_name, inactivity_timeout=1):
            if body is not None:
                # Преобразование строки JSON в словарь
                data = json.loads(body)
                yield f"data: {json.dumps(data)}\n\n"

    return app.response_class(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
