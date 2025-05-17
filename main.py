from flask import Flask, render_template, request, redirect, url_for, jsonify
from ClassTest import CarController, CraneController
import requests

app = Flask(__name__, template_folder='templates')

# Инициализация устройств
crane = CraneController(app, ip='192.168.22.XXX', number=1, state=True)
car1 = CarController(app, ip='192.168.22.181', number=1, state=True)
car2 = CarController(app, ip='192.168.22.154', number=2, state=True)
car3 = CarController(app, ip='192.168.22.121', number=3, state=True)
car4 = CarController(app, ip='192.168.22.154', number=4, state=True)

devices = {
    'crane': crane,
    'cars': [car1, car2, car3, car4]
}


@app.route('/')
def index():
    """Страница авторизации"""
    return render_template('auth.html')


@app.route('/login', methods=['POST'])
def login():
    """Обработка авторизации"""
    username = request.form.get('username')
    password = request.form.get('password')

    if username == "admin" and password == "qwerty":
        return render_template('device_selection.html')
    else:
        return redirect(url_for('index'))


@app.route('/select_device', methods=['POST'])
def select_device():
    """Выбор типа устройства"""
    device_type = request.form.get('device_type')

    if device_type == "crane":
        return render_template('crane_control.html')
    elif device_type == "car":
        return render_template('car_selection.html', cars=devices['cars'])
    else:
        return redirect(url_for('index'))


@app.route('/select_car/<int:car_number>')
def select_car(car_number):
    """Выбор конкретной машинки"""
    if 1 <= car_number <= len(devices['cars']):
        return render_template('car_control.html', car_number=car_number)
    return redirect(url_for('index'))


# API для управления устройствами
@app.route('/api/control', methods=['POST'])
def api_control():
    data = request.json
    device_type = data.get('device_type')
    device_number = data.get('device_number')
    action = data.get('action')

    if device_type == 'crane' and device_number == 1:
        if action in ['up', 'down', 'left', 'right']:
            return crane.send_crane_command(action)
        elif action == 'toggle_magnet':
            return crane.toggle_magnet()

    elif device_type == 'car' and 1 <= device_number <= 4:
        car = devices['cars'][device_number - 1]
        if action in ['forward', 'backward', 'left', 'right', 'stop']:
            if action == 'forward':
                return jsonify({'result': car.wpress()})
            elif action == 'backward':
                return jsonify({'result': car.spress()})
            elif action == 'left':
                return jsonify({'result': car.apress()})
            elif action == 'right':
                return jsonify({'result': car.dpress()})
            elif action == 'stop':
                return jsonify({'result': car.snotpress()})

    return jsonify({'error': 'Invalid command'}), 400


# Блокировка/разблокировка
@app.route('/api/block', methods=['POST'])
def api_block():
    data = request.json
    device_type = data.get('device_type')
    device_number = data.get('device_number')
    action = data.get('action')  # 'block' or 'unblock'

    if device_type == 'crane' and device_number == 1:
        return crane.block() if action == 'block' else crane.unblock()

    elif device_type == 'car' and 1 <= device_number <= 4:
        car = devices['cars'][device_number - 1]
        return car.block() if action == 'block' else car.unblock()

    return jsonify({'error': 'Invalid device'}), 400


@app.route('/api/status')
def api_status():
    """Получение статусов всех устройств"""
    status = {
        'crane': {
            'number': 1,
            'state': crane.state,
            'magnet_active': crane.magnet_active
        },
        'cars': [
            {
                'number': car.number,
                'state': car.state,
                'ip': car.ip
            } for car in devices['cars']
        ]
    }
    return jsonify(status)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)