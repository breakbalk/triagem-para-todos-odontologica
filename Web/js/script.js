/* --- MODULARIZAÇÃO DE LÓGICA DE FRONT-END --- */

document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Captura os formulários (Login e Cadastro)
    const formCadastro = document.querySelector('form[action="/registrar"]');
    const formLogin = document.querySelector('form[action="/login"]');

    // 2. Lógica específica para a TELA DE CADASTRO
    if (formCadastro) {
        formCadastro.addEventListener('submit', (event) => {
            const senha = document.getElementById('senha').value;
            const confirmarSenha = document.getElementById('confirmar_senha').value;

            // Validação de igualdade de senhas
            if (senha !== confirmarSenha) {
                event.preventDefault(); // Impede o envio dos dados para o Back-end
                alert('Atenção: As senhas não coincidem. Por favor, verifique.');
            } else if (senha.length < 6) {
                event.preventDefault();
                alert('Atenção: A senha deve ter no mínimo 6 caracteres.');
            }
        });
    }

    // 3. Lógica específica para a TELA DE LOGIN (Opcional)
    if (formLogin) {
        formLogin.addEventListener('submit', () => {
            console.log("Tentativa de login enviada...");
            // Aqui poderíamos adicionar um efeito de "Carregando" no botão
        });
    }
});