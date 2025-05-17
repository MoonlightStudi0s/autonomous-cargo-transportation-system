function controlCar(action) {
    fetch('/api/control', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            device_type: 'car',
            device_number: parseInt(document.querySelector('h1').textContent.match(/\d+/)[0]),
            action: action
        })
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));
}

function controlCrane(action) {
    fetch('/api/control', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            device_type: 'crane',
            device_number: 1,
            action: action
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if (action === 'toggle_magnet') {
            document.getElementById('magnet-status').textContent =
                data.magnet_active ? 'Включен' : 'Выключен';
        }
    })
    .catch(error => console.error('Error:', error));
}

// Обработка клавиатуры
document.addEventListener('keydown', (e) => {
    const key = e.key.toLowerCase();
    const controls = document.querySelector('.controls');

    if (controls) {
        if (key === 'w') controlCrane('up');
        if (key === 's') controlCrane('down');
        if (key === 'a') controlCrane('left');
        if (key === 'd') controlCrane('right');
        if (key === 'x') controlCrane('toggle_magnet');
    }
});