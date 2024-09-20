function register() {
    const login = document.getElementById('login').value.trim();
    const password = document.getElementById('password').value.trim();
    if (!login || !password) {
        alert('Пожалуйста, введите логин и пароль.');
        return;
    }
    fetch('/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ login, password })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.status === 'success') {
            login();  // После успешной регистрации сразу выполнить вход
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });
}

function login() {
    const login = document.getElementById('login').value.trim();
    const password = document.getElementById('password').value.trim();
    if (!login || !password) {
        alert('Пожалуйста, введите логин и пароль.');
        return;
    }
    fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ login, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            document.cookie = `login=${login}; path=/`;
            setTimeout(() => {
                window.location.href = '/chat';  // Переход на страницу чата
            }, 1000);
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });
}

function loginWithCookie() {
    const cookies = document.cookie.split('; ').reduce((acc, cookie) => {
        const [key, value] = cookie.split('=');
        acc[key] = value;
        return acc;
    }, {});
    if (cookies.login) {
        fetch('/validate_cookie', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ login: cookies.login })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                setTimeout(() => {
                    window.location.href = '/chat';
                }, 1000);
            } else {
                alert('Неверная куки. Пожалуйста, войдите вручную.');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
    } else {
        alert('Куки не найдены. Пожалуйста, войдите вручную.');
    }
}
