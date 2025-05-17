document.addEventListener('DOMContentLoaded', function() {
    // Элементы интерфейса
    const authContainer = document.getElementById('auth-container');
    const deviceSelectContainer = document.getElementById('device-select-container');
    const carSelectContainer = document.getElementById('car-select-container');
    const craneControlContainer = document.getElementById('crane-control-container');
    const carControlContainer = document.getElementById('car-control-container');

    // Кнопки навигации
    const loginForm = document.getElementById('login-form');
    const craneBtn = document.getElementById('crane-btn');
    const carBtn = document.getElementById('car-btn');
    const backToAuth = document.getElementById('back-to-auth');
    const backToDevice = document.getElementById('back-to-device');
    const craneBack = document.getElementById('crane-back');
    const carBack = document.getElementById('car-back');

    // Кнопки управления краном
    const craneUp = document.getElementById('crane-up');
    const craneDown = document.getElementById('crane-down');
    const craneLeft = document.getElementById('crane-left');
    const craneRight = document.getElementById('crane-right');
    const toggleMagnet = document.getElementById('toggle-magnet');
    const magnetStatus = document.getElementById('magnet-status');

    // Кнопки управления машинкой
    const carForward = document.getElementById('car-forward');
    const carBackward = document.getElementById('car-backward');
    const carLeft = document.getElementById('car-left');
    const carRight = document.getElementById('car-right');
    const carStop = document.getElementById('car-stop');
    const carNumberDisplay = document.getElementById('car-number');

    // Состояния
    let magnetActive = false;
    let currentCar = null;

    // Обработчики навигации
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        // Здесь должна быть проверка авторизации
        if (username === 'admin' && password === 'qwerty') {
            authContainer.classList.add('hidden');
            deviceSelectContainer.classList.remove('hidden');
        } else {
            alert('Неверные логин или пароль');
        }
    });

    craneBtn.addEventListener('click', function() {
        deviceSelectContainer.classList.add('hidden');
        craneControlContainer.classList.remove('hidden');
    });

    carBtn.addEventListener('click', function() {
        deviceSelectContainer.classList.add('hidden');
        carSelectContainer.classList.remove('hidden');
    });

    backToAuth.addEventListener('click', function() {
        deviceSelectContainer.classList.add('hidden');
        authContainer.classList.remove('hidden');
    });

    backToDevice.addEventListener('click', function() {
        carSelectContainer.classList.add('hidden');
        deviceSelectContainer.classList.remove('hidden');
    });

    craneBack.addEventListener('click', function() {
        craneControlContainer.classList.add('hidden');
        deviceSelectContainer.classList.remove('hidden');
    });

    carBack.addEventListener('click', function() {
        carControlContainer.classList.add('hidden');
        carSelectContainer.classList.remove('hidden');
    });

    // Обработчики выбора машинки
    document.querySelectorAll('.car-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            currentCar = this.getAttribute('data-car');
            carNumberDisplay.textContent = currentCar;
            carSelectContainer.classList.add('hidden');
            carControlContainer.classList.remove('hidden');
        });
    });

    // Управление краном
    craneUp.addEventListener('click', () => sendCommand('crane', 'up'));
    craneDown.addEventListener('click', () => sendCommand('crane', 'down'));
    craneLeft.addEventListener('click', () => sendCommand('crane', 'left'));
    craneRight.addEventListener('click', () => sendCommand('crane', 'right'));

    toggleMagnet.addEventListener('click', function() {
        magnetActive = !magnetActive;
        magnetStatus.textContent = magnetActive ? 'Включен' : 'Выключен';
        magnetStatus.style.color = magnetActive ? '#27ae60' : '#e74c3c';
        sendCommand('crane', magnetActive ? 'magnet_on' : 'magnet_off');
    });

    // Управление машинкой
    carForward.addEventListener('click', () => sendCommand('car', 'forward'));
    carBackward.addEventListener('click', () => sendCommand('car', 'backward'));
    carLeft.addEventListener('click', () => sendCommand('car', 'left'));
    carRight.addEventListener('click', () => sendCommand('car', 'right'));
    carStop.addEventListener('click', () => sendCommand('car', 'stop'));

    // Обработка клавиатуры
    document.addEventListener('keydown', function(e) {
        if (craneControlContainer.classList.contains('hidden') === false) {
            // Управление краном
            switch(e.key.toLowerCase()) {
                case 'w': sendCommand('crane', 'up'); break;
                case 's': sendCommand('crane', 'down'); break;
                case 'a': sendCommand('crane', 'left'); break;
                case 'd': sendCommand('crane', 'right'); break;
                case 'x':
                    magnetActive = !magnetActive;
                    magnetStatus.textContent = magnetActive ? 'Включен' : 'Выключен';
                    magnetStatus.style.color = magnetActive ? '#27ae60' : '#e74c3c';
                    sendCommand('crane', magnetActive ? 'magnet_on' : 'magnet_off');
                    break;
            }
        } else if (carControlContainer.classList.contains('hidden') === false) {
            // Управление машинкой
            switch(e.key.toLowerCase()) {
                case 'w': sendCommand('car', 'forward'); break;
                case 's': sendCommand('car', 'stop'); break;
                case 'a': sendCommand('car', 'left'); break;
                case 'd': sendCommand('car', 'right'); break;
                case 'z': sendCommand('car', 'backward'); break;
            }
        }
    });

    // Функция отправки команд на сервер
    function sendCommand(deviceType, command) {
        let url = '/';
        let data = {};

        if (deviceType === 'crane') {
            url = '/crane_control';
            data = { action: command };
        } else if (deviceType === 'car') {
            url = '/car_control';
            data = {
                action: command,
                car_number: currentCar
            };
        }

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.text())
        .then(data => console.log('Success:', data))
        .catch(error => console.error('Error:', error));
    }
});