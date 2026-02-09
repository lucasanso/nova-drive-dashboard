function verificarAcesso() {
    const token = localStorage.getItem('meu_token');

    if (!token) {
        alert("Acesso negado! Faça login primeiro.");
        window.location.href = 'index.html'; 
        return;
    }
}

verificarAcesso()