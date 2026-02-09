
// Aqui será selecionado o primeiro elemento 'form' do html.
// A diferença entre querySelector e getElementById é que o querySelector utiliza seletor CSS (muito vantajoso porque sei do webscraping)
// Pode-se utilziar querySelectorAll também

const form = document.querySelector('form');

form.addEventListener('submit', async (e) => {
    // Impede o carregamento dá página pois, sempre que ocorre o 'submit' a página é recarregada.
    e.preventDefault();

    /*
    Se não quisermos utilizar formData, que é específico de formulário podemos fazer isso abaixo:
    const nome = document.querySelector('#nome').value;
    const email = document.querySelector('#email').value;
    */

    const formData = new FormData(form);
    const data = {
        login: formData.get('login'), 
        senha: formData.get('senha')
    };

    try {
        // O await espera a resposta do servidor em http://127.0.0.1:8000/sign-up
        const response = await fetch('http://127.0.0.1:8000/sign-up', {
            method: 'POST',
            headers: {
                // É como se fosse a etiqueta do que estamos enviando para a API
                // Explicando para o FastAPI que o que estamos enviando é um JSON
                'Content-Type': 'application/json'
            },
            // Transformando o objeto data em JSON 
            body: JSON.stringify(data)
        }
    );
        const result = await response.json();
        console.log(result);
    } catch (error) {
        console.error('Erro na requisição:', error);
    }
});