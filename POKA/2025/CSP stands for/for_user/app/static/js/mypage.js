fetch('/api/user', {
    credentials: 'same-origin'
})
    .then(res => {
        if (!res.ok) throw new Error('문제가 발생했습니다');
        return res.json();
    })
    .then(data => {
        document.getElementById('username').textContent = data.username;
        document.getElementById('email').textContent = data.email;
    })
    .catch(err => {
        alert(err.message);
        window.location.href = '/login';
    });

document.getElementById('editButton')
    .addEventListener('click', () => { window.location.href = '/mypage_modify'; });

document.getElementById('deleteButton')
    .addEventListener('click', () => { window.location.href = '/logout'; });
