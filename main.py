from flask import Flask, render_template, request, redirect, url_for
import requests
import time
from ClassTest import *



app = Flask(__name__, template_folder='templates')

# Инициализация устройств
Crane = CraneController(app, ip='192.168.22.XXX', number=1, state=True)
Vehicle1 = CarController(app, ip='192.168.22.181', number=1, state=True)
Vehicle2 = CarController(app, ip='192.168.22.154', number=2, state=True)
devices = [Crane, Vehicle1, Vehicle2]


@app.route('/')
def index():
    """Страница авторизации"""
    return render_template('auth.html')


@app.route('/login', methods=['POST'])
def login():
    """Проверка авторизации"""
    username = request.form['username']
    password = request.form['password']

    if username == "admin" and password == "qwerty":
        return render_template('device_selection.html')
    else:
        return redirect(url_for('index'))


@app.route('/select_device', methods=['POST'])
def select_device():
    """Выбор типа устройства (кран/машина)"""
    device_type = request.form['device_type']

    if device_type == "crane":
        return render_template('crane_control.html')
    elif device_type == "car":
        return render_template('car_selection.html')
    else:
        return redirect(url_for('index'))


@app.route('/select_car', methods=['POST'])
def select_car():
    """Выбор конкретной машины"""
    car_number = request.form['car_number']
    return render_template('car_control.html', number=car_number)


# Управление краном
@app.route('/crane_control', methods=['POST'])
def crane_control():
    action = request.form['action']

    if action == 'forward':
        # Отправка команды "вперед" крану
        pass
    elif action == 'backward':
        # Отправка команды "назад" крану
        pass
    elif action == 'up':
        # Отправка команды "вверх" крану
        pass
    elif action == 'down':
        # Отправка команды "вниз" крану
        pass
    elif action == 'toggle_magnet':
        # Переключение состояния магнита
        pass

    return "OK"


# Управление машиной
@app.route('/car_control', methods=['POST'])
def car_control():
    car_number = request.form.get('car_number')
    action = request.form['action']

    # Обработка команд для машины
    if action == 'forward':
        pass
    elif action == 'backward':
        pass
    elif action == 'left':
        pass
    elif action == 'right':
        pass

    return "OK"


# Блокировки/разблокировки
@app.route('/block_all', methods=['POST'])
def block_all():
    for device in devices:
        device.block()
    return "All devices blocked"


@app.route('/unblock_all', methods=['POST'])
def unblock_all():
    for device in devices:
        device.unblock()
    return "All devices unblocked"


if __name__ == '__main__':
    app.run(host='192.168.0.102', port=3000, debug=True)