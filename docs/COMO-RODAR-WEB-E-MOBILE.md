# Como abrir e testar o projeto (Web + Mobile)

Guia para qualquer pessoa da equipe rodar o **sistema web** (Flask + páginas HTML) e o **app mobile** (Expo) na própria máquina.

---

## O que instalar antes (uma vez só)

| Ferramenta | Para quê |
|------------|----------|
| **Python 3** + `pip` | Backend web (`Flask`) |
| **Node.js** (LTS) + `npm` | App mobile (`Expo` / `npm`) |
| **Git** | Clonar o repositório |
| No celular: **Expo Go** (Play Store / App Store) | Testar o app sem cabo |

> **Dica:** depois de instalar o Node, feche e abra o terminal para o `npm` ser reconhecido no Windows.

---

## 1. Projeto web (backend + site)

O site **não funciona** só abrindo o HTML no Explorer: as telas chamam a API (`/api/...`). É obrigatório subir o **Flask**.

### Passos

1. Abra o terminal na pasta do repositório e entre no backend:

   ```bash
   cd Web/backend
   ```

2. Instale as dependências Python (na primeira vez ou quando mudar o `requirements.txt`):

   ```bash
   pip install -r requirements.txt
   ```

   **Banco Supabase (opcional):** rode o SQL em `Web/supabase/schema.sql` no painel, copie `Web/backend/.env.example` para `.env`, defina `COE_STORAGE=supabase`, `SUPABASE_URL` e `SUPABASE_KEY` (de preferência `service_role` no servidor). Sem `.env`, o padrão continua sendo JSON em `Web/data/`.

3. Inicie o servidor:

   ```bash
   python app.py
   ```

4. Quando aparecer algo como **Running on http://127.0.0.1:5000** e **Running on http://192.168.x.x:5000**, o servidor está ok.

5. No **navegador**, acesse:

   - **http://127.0.0.1:5000/** ou **http://localhost:5000/**

   Você pode ir direto para o login: **http://127.0.0.1:5000/pages/login.html**

### Credenciais de administrador (demonstração)

Na primeira execução é criado um usuário admin (JSON local **ou** Supabase, conforme `COE_STORAGE`).

| | |
|--|--|
| E-mail | `admin@coe.unievangelica.edu.br` |
| Senha | `Admin@coe2026` |

Mais detalhes: [`Web/README.md`](../Web/README.md).

---

## 2. Projeto mobile (Expo)

O app **conversa com o mesmo backend**. O Flask precisa estar **rodando** (seção 1). Use **outro terminal** — não feche o do Python.

### Passos

1. Entre na pasta do app:

   ```bash
   cd Mobile
   ```

   Se o terminal já mostrar o caminho `...\triagem-para-todos-odontologica\Mobile>`, **não** rode `cd Mobile` de novo (senão o Windows tenta `Mobile\Mobile` e dá erro).

2. Instale as dependências (na primeira vez ou após `git pull` que mude o `package.json`):

   ```bash
   npm install
   ```

3. **Celular físico na mesma Wi‑Fi do PC**

   - No terminal do Flask, anote o IP da linha **Running on http://192.168....:5000** (não use `127.0.0.1` no celular).
   - Abra `Mobile/src/config.js` e coloque esse IP em **`IP_DO_PC`** (ex.: `"192.168.0.232"`).
   - Abra `Mobile/package.json` e confira o script **`start:lan`**: o valor **`REACT_NATIVE_PACKAGER_HOSTNAME`** deve ser o **mesmo IP** (para o QR code do Metro bater com a sua rede).

4. Suba o bundler do Expo:

   ```bash
   npm run start:lan
   ```

   (Este script já configura o hostname LAN no Windows; em caso de dúvida, use a documentação do [`Mobile/README.md`](../Mobile/README.md).)

5. No celular, abra o **Expo Go** e **escaneie o QR code** do terminal.

6. Faça login ou cadastro. Os usuários são os mesmos do site (mesmo `app_storage.json` no PC que está rodando o Flask).

### Emulador Android (opcional)

Se estiver usando **emulador** no mesmo PC do Flask, em `Mobile/src/config.js` deixe **`IP_DO_PC`** vazio (`""`) para o app usar **`10.0.2.2`** (equivalente ao `localhost` visto de dentro do emulador).

### Se aparecer “porta 8081 em uso”

Aceite usar outra porta (ex.: **8082**) ou feche o outro processo Expo/Metro que ficou aberto em segundo plano.

---

## Resumo: duas janelas de terminal

| Terminal | Pasta | Comando |
|----------|--------|---------|
| **1** | `Web/backend` | `python app.py` |
| **2** | `Mobile` | `npm run start:lan` |

---

## Problemas frequentes

| Sintoma | O que verificar |
|---------|-----------------|
| Site sem login / erro de rede | Flask está rodando? URL é `http://127.0.0.1:5000` e não `file://` |
| Mobile não loga | Mesmo Wi‑Fi que o PC; `IP_DO_PC` = IP do Flask; firewall liberando porta **5000** |
| Expo fala de SDK diferente | Atualizar **Expo Go** na loja; alinhar com a versão do **Expo** no `Mobile/package.json` |
| `npm` / `python` não reconhecidos | PATH do Windows; reinstalar Node/Python marcando “Add to PATH” |

---

## Onde ler mais

| Documento | Conteúdo |
|-----------|----------|
| [`Web/README.md`](../Web/README.md) | Backend, admin, recuperação de senha em modo demo |
| [`Mobile/README.md`](../Mobile/README.md) | Mobile, token Bearer, estrutura de pastas |
| [`docs/README.md`](./README.md) | Índice da documentação de planejamento |
