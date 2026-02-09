const form = document.querySelector('form');

form.addEventListener('submit', async (e) => {
    e.preventDefault(); 

    const formData = new FormData(form);
    const data = {
        login: formData.get('login'), 
        senha: formData.get('senha')
    };

    try {
        const response = await fetch('http://127.0.0.1:8000/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            console.log('Login bem-sucedido!');
            
            localStorage.setItem('jwt_token', result.access_token);
            
            window.location.href = 'dashboard.html';
            
        } else {
            alert('Falha no login: ' + (result.detail || 'Usuário ou senha incorretos'));
        }

    } catch (error) {
        console.error('Erro na requisição de login:', error);
        alert('Erro ao conectar com o servidor.');
    }
});