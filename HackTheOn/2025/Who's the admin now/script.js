function submitLoginForm(event) {
    event.preventDefault();

    const user_id = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const error = document.getElementById('login-error');

    if (!user_id || !password) {
        error.textContent = "Please fill in all fields.";
        return;
    }

    fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect;
        } else {
            error.textContent = data.message;
        }
    })
    .catch(() => {
        error.textContent = 'An unexpected error occurred.';
    });
}

function checkEmailDuplicate(email) {
    const help = document.getElementById('email-help');
    if (!email) return;
    fetch('/valid_user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ "user_id": email })
    })
    .then(res => res.json())
    .then(data => {
        if (data.exists) {
            help.textContent = 'Email already registered';
            help.className = 'help is-danger';
            document.getElementById('register-btn').disabled = true;
        } else {
            help.textContent = 'Email available';
            help.className = 'help is-success';
            validatePasswordMatch();
        }
    })
    .catch(() => {
        help.textContent = 'Error checking email';
        help.className = 'help is-danger';
    });
}

function validatePasswordMatch() {
    const pwd = document.getElementById('password').value;
    const confirmPwd = document.getElementById('confirm-password').value;
    const help = document.getElementById('password-help');
    const emailHelp = document.getElementById('email-help');

    if (pwd.length > 0) {
        if (pwd !== confirmPwd) {
            help.textContent = "Passwords do not match";
            help.className = 'help is-danger';
            document.getElementById('register-btn').disabled = true;
        } else {
            help.textContent = "Passwords match";
            help.className = 'help is-success';
            if (emailHelp.classList.contains('is-success')) {
                document.getElementById('register-btn').disabled = false;
            }
        }
    } 
}

function submitRegistrationForm(event) {
    event.preventDefault();

    const user_id = document.querySelector('#register-email').value;
    const username = document.querySelector('input[name="username"]').value;
    const password = document.querySelector('#password').value;

    fetch('/join', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id, username, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            window.location.href = data.redirect;
        } else {
            alert(data.message);
        }
    })
    .catch(() => alert('Registration failed.'));
}