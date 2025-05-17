from flask import Response, jsonify
import cv2
import requests


class CarController:
    def __init__(self, app, ip, number, state):
        """
        :param app: Flask приложение
        :param ip: IP машинки
        :param number: номер машинки (1-4)
        :param state: начальное состояние (True - разблокирована)
        """
        self.ip = ip
        self.number = number
        self.app = app
        self.state = state
        self.setup_routes()
        self.Frames()

    def Frames(self):
        """Запуск трансляции с камеры машинки"""

        def getFrames():
            cap = cv2.VideoCapture(f"http://{self.ip}:3000/video_feed")
            while True:
                success, frame = cap.read()
                if not success:
                    break
                else:
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        @self.app.route(f'/car_video{self.number}')
        def stream():
            return Response(getFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def setup_routes(self):
        """Настройка маршрутов для управления машинкой"""
        self.app.add_url_rule(
            f'/car_control/{self.number}/<action>',
            f'car_control_{self.number}',
            self.handle_car_action,
            methods=['POST']
        )

    def handle_car_action(self, action):
        """Обработка действий для машинки"""
        if not self.state:
            return jsonify({'status': 'blocked', 'message': f'Машинка {self.number} заблокирована'}), 403

        actions_map = {
            'forward': ('wpress', 'wnotpress'),
            'backward': ('spress', 'snotpress'),
            'left': ('apress', 'anotpress'),
            'right': ('dpress', 'dnotpress'),
            'stop': ('snotpress', 'snotpress')
        }

        if action not in actions_map:
            return jsonify({'status': 'error', 'message': 'Неизвестное действие'}), 400

        press_cmd, release_cmd = actions_map[action]
        url = f'http://{self.ip}:3000/{press_cmd}'

        try:
            response = requests.post(url, timeout=1)
            if response.status_code == 200:
                return jsonify({'status': 'success', 'action': action})
            return jsonify({'status': 'error', 'message': 'Ошибка устройства'}), 500
        except requests.exceptions.RequestException:
            return jsonify({'status': 'error', 'message': 'Не удалось соединиться с устройством'}), 503

    def block(self):
        """Блокировка машинки"""
        self.state = False
        return jsonify({'status': 'success', 'message': f'Машинка {self.number} заблокирована'})

    def unblock(self):
        """Разблокировка машинки"""
        self.state = True
        return jsonify({'status': 'success', 'message': f'Машинка {self.number} разблокирована'})


class CraneController:
    def __init__(self, app, ip, number, state):
        """
        :param app: Flask приложение
        :param ip: IP крана
        :param number: номер крана
        :param state: начальное состояние (True - разблокирован)
        """
        self.ip = ip
        self.number = number
        self.app = app
        self.state = state
        self.magnet_active = False
        self.setup_routes()
        self.Frames()

    def Frames(self):
        """Запуск трансляции с камеры крана"""

        def getFrames():
            cap = cv2.VideoCapture(f"http://{self.ip}:3000/video_feed")
            while True:
                success, frame = cap.read()
                if not success:
                    break
                else:
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        @self.app.route(f'/crane_video{self.number}')
        def stream():
            return Response(getFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def setup_routes(self):
        """Настройка маршрутов для управления краном"""
        self.app.add_url_rule(
            f'/crane_control/{self.number}/<action>',
            f'crane_control_{self.number}',
            self.handle_crane_action,
            methods=['POST']
        )

    def handle_crane_action(self, action):
        """Обработка действий для крана"""
        if not self.state:
            return jsonify({'status': 'blocked', 'message': f'Кран {self.number} заблокирован'}), 403

        actions_map = {
            'up': 'up_command',
            'down': 'down_command',
            'left': 'left_command',
            'right': 'right_command',
            'magnet_on': 'magnet_on_command',
            'magnet_off': 'magnet_off_command'
        }

        if action not in actions_map:
            return jsonify({'status': 'error', 'message': 'Неизвестное действие'}), 400

        # Для магнита сохраняем состояние
        if action == 'magnet_on':
            self.magnet_active = True
        elif action == 'magnet_off':
            self.magnet_active = False

        # Здесь должна быть реальная команда для крана
        command = actions_map[action]
        url = f'http://{self.ip}:3000/{command}'

        try:
            response = requests.post(url, timeout=1)
            if response.status_code == 200:
                return jsonify({
                    'status': 'success',
                    'action': action,
                    'magnet_active': self.magnet_active
                })
            return jsonify({'status': 'error', 'message': 'Ошибка устройства'}), 500
        except requests.exceptions.RequestException:
            return jsonify({'status': 'error', 'message': 'Не удалось соединиться с устройством'}), 503

    def block(self):
        """Блокировка крана"""
        self.state = False
        return jsonify({'status': 'success', 'message': f'Кран {self.number} заблокирован'})

    def unblock(self):
        """Разблокировка крана"""
        self.state = True
        return jsonify({'status': 'success', 'message': f'Кран {self.number} разблокирован'})