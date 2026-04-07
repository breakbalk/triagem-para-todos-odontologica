/* --- MODULARIZAÇÃO DE LÓGICA DE FRONT-END --- */

document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Captura os formulários
    const formCadastro = document.getElementById('form-cadastro'); // Usando o ID que colocamos no HTML
    const formLogin = document.querySelector('form[action="/login"]');

    // 2. Lógica específica para a TELA DE CADASTRO
    if (formCadastro) {
        formCadastro.addEventListener('submit', (event) => {
            const senha = document.getElementById('senha').value;
            const confirmarSenha = document.getElementById('confirmar_senha').value;
            const username = document.getElementById('username').value;

            // Validação de Nome de Usuário (não pode ser vazio ou só espaços)
            if (username.trim().length < 3) {
                event.preventDefault();
                alert('O nome de usuário deve ter pelo menos 3 caracteres.');
                return;
            }

            // Validação de igualdade de senhas
            if (senha !== confirmarSenha) {
                event.preventDefault(); 
                alert('Atenção: As senhas não coincidem. Por favor, verifique.');
            } else if (senha.length < 6) {
                event.preventDefault();
                alert('Atenção: A senha deve ter no mínimo 6 caracteres.');
            }
        });
    }

    // 3. Lógica específica para a TELA DE LOGIN
    if (formLogin) {
        formLogin.addEventListener('submit', (event) => {
            const btn = formLogin.querySelector('.btn-primary');
            if (btn) {
                btn.innerText = "CARREGANDO...";
                btn.style.opacity = "0.7";
                btn.style.cursor = "not-allowed";
            }
            console.log("Tentativa de login enviada...");
        });
    }
});