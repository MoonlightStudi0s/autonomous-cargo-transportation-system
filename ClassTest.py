from flask import Response, jsonify
import cv2
import requests


class CarController:
    def __init__(self, app, ip, number, state):
        """
        Контроллер для управления машинкой
        :param app: Flask приложение
        :param ip: IP адрес машинки
        :param number: Номер машинки (1-4)
        :param state: Начальное состояние (True - разблокирована)
        """
        self.ip = ip
        self.number = number
        self.app = app
        self.state = state
        self.setup_video_stream()
        self.setup_control_routes()

    def setup_video_stream(self):
        """Настройка видео потока с уникальным endpoint"""

        def get_frames():
            cap = cv2.VideoCapture(f"http://{self.ip}:3000/video_feed")
            while True:
                success, frame = cap.read()
                if not success:
                    break
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        #уникальная функция для каждого экземпляра
        stream_func_name = f'car_video_stream_{self.number}'

        def stream_func():
            return Response(get_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

        stream_func.__name__ = stream_func_name

        self.app.add_url_rule(
            f'/car_video{self.number}',
            endpoint=f'car_video_{self.number}',
            view_func=stream_func
        )

    def setup_control_routes(self):
        """Настройка маршрутов управления машинкой"""
        methods = ['POST']

        routes = [
            ('wpress', self.wpress),
            ('wnotpress', self.wnotpress),
            ('spress', self.spress),
            ('snotpress', self.snotpress),
            ('apress', self.apress),
            ('anotpress', self.anotpress),
            ('dpress', self.dpress),
            ('dnotpress', self.dnotpress),
            ('Block', self.block),
            ('UnBlock', self.unblock)
        ]

        for route, view_func in routes:
            self.app.add_url_rule(
                f'/{route}{self.number}',
                endpoint=f'{route}_{self.number}',
                view_func=view_func,
                methods=methods
            )

    def send_command(self, command):
        """Отправка команды на машинку"""
        if not self.state:
            print(f"Машинка {self.number} заблокирована")
            return "Block"

        url = f'http://{self.ip}:3000/{command}'
        try:
            response = requests.post(url, timeout=1)
            if response.status_code == 200:
                print(command.upper())
                return command.upper()
            return "Error"
        except requests.exceptions.RequestException:
            return "Connection Error"

    # Методы управления
    def wpress(self):
        return self.send_command('wpress')

    def wnotpress(self):
        return self.send_command('wnotpress')

    def spress(self):
        return self.send_command('spress')

    def snotpress(self):
        return self.send_command('snotpress')

    def apress(self):
        return self.send_command('apress')

    def anotpress(self):
        return self.send_command('anotpress')

    def dpress(self):
        return self.send_command('dpress')

    def dnotpress(self):
        return self.send_command('dnotpress')

    def block(self):
        self.state = False
        return f"Машинка {self.number} заблокирована"

    def unblock(self):
        self.state = True
        return f"Машинка {self.number} разблокирована"


class CraneController:
    def __init__(self, app, ip, number, state):
        """
        Контроллер для управления краном
        :param app: Flask приложение
        :param ip: IP адрес крана
        :param number: Номер крана
        :param state: Начальное состояние (True - разблокирован)
        """
        self.ip = ip
        self.number = number
        self.app = app
        self.state = state
        self.magnet_active = False
        self.setup_video_stream()
        self.setup_control_routes()

    def setup_video_stream(self):
        """Настройка видео потока для крана"""

        def get_frames():
            cap = cv2.VideoCapture(f"http://{self.ip}:3000/video_feed")
            while True:
                success, frame = cap.read()
                if not success:
                    break
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        stream_func_name = f'crane_video_stream_{self.number}'

        def stream_func():
            return Response(get_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

        stream_func.__name__ = stream_func_name

        self.app.add_url_rule(
            f'/crane_video{self.number}',
            endpoint=f'crane_video_{self.number}',
            view_func=stream_func
        )

    def setup_control_routes(self):
        """Настройка маршрутов управления краном"""
        methods = ['POST']

        routes = [
            ('crane_up', self.move_up),
            ('crane_down', self.move_down),
            ('crane_left', self.move_left),
            ('crane_right', self.move_right),
            ('crane_magnet', self.toggle_magnet),
            ('Block', self.block),
            ('UnBlock', self.unblock)
        ]

        for route, view_func in routes:
            self.app.add_url_rule(
                f'/{route}{self.number}',
                endpoint=f'{route}_{self.number}',
                view_func=view_func,
                methods=methods
            )

    def send_crane_command(self, command):
        """Отправка команды на кран"""
        if not self.state:
            return jsonify({
                'status': 'blocked',
                'message': f'Кран {self.number} заблокирован'
            }), 403

        url = f'http://{self.ip}:3000/{command}'
        try:
            response = requests.post(url, timeout=1)
            if response.status_code == 200:
                return jsonify({
                    'status': 'success',
                    'action': command,
                    'magnet_active': self.magnet_active
                })
            return jsonify({'status': 'error'}), 500
        except requests.exceptions.RequestException:
            return jsonify({'status': 'connection_error'}), 503

    # Методы управления краном
    def move_up(self):
        return self.send_crane_command('up')

    def move_down(self):
        return self.send_crane_command('down')

    def move_left(self):
        return self.send_crane_command('left')

    def move_right(self):
        return self.send_crane_command('right')

    def toggle_magnet(self):
        self.magnet_active = not self.magnet_active
        command = 'magnet_on' if self.magnet_active else 'magnet_off'
        return self.send_crane_command(command)

    def block(self):
        self.state = False
        return jsonify({
            'status': 'success',
            'message': f'Кран {self.number} заблокирован'
        })

    def unblock(self):
        self.state = True
        return jsonify({
            'status': 'success',
            'message': f'Кран {self.number} разблокирован'
        })