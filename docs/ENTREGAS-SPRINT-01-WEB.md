# Sprint 01 — entregas da parte Web (para a equipe)

**Período oficial (relatório):** 06/04/2026 – 19/04/2026  
**Objetivo da sprint:** ambiente Python, cadastro/login e interfaces de autenticação; base de API para o restante do MVP.

Este documento resume **o que está implementado no repositório** na parte web. Detalhes técnicos de execução: [`Web/README.md`](../Web/README.md). Planejamento das próximas sprints: [`PLANEJAMENTO-WEB.md`](./PLANEJAMENTO-WEB.md).

---

## O que foi entregue

### Backend (Flask)

- Servidor único em **`Web/backend/app.py`**: todas as rotas `/api/...` (autenticação, triagem, usuário logado).
- **`Web/backend/storage.py`**: persistência em **JSON** (`Web/data/app_storage.json`) até existir Supabase/PostgreSQL.
- Remoção dos blueprints antigos em **`Web/backend/routes/`** (lógica concentrada em `app.py`).
- API compatível com **sessão por cookie** (navegador) e **`Authorization: Bearer`** + **`mobile_token`** (app mobile).
- Servidor em **`0.0.0.0:5000`** para acesso na rede local.

### Requisitos funcionais cobertos (web)

| RF | Descrição (resumo) | Onde |
|----|--------------------|------|
| RF01 | Cadastro de usuário | `POST /api/auth/register` + `pages/cadastro.html` |
| RF02 | Login | `POST /api/auth/login` + `pages/login.html` |
| RF03 | Recuperação de senha | fluxo demo com token (`COE_DEMO_RESET_TOKEN`) + `pages/recuperar-senha.html` |

### Front-end (páginas e integração)

- **`Web/js/web-app.js`**: lógica por página (`data-page` no `<body>`), `fetch` com cookie de sessão.
- **Páginas HTML** em `Web/pages/`: login, cadastro, recuperar senha, home, triagem, confirmação, admin (fluxo utilizável conforme o estado atual da API).
- **`Web/css/style.css`**: estilos compartilhados (incluindo telas após login).
- **Identidade visual** e imagens em `Web/assets/img/` (login/cadastro responsivos).

### O que ficou explícito para outra sprint / outro membro

- **Banco Supabase (PostgreSQL):** modelagem e tabelas — ainda **não** substituem o JSON; ver [`PLANEJAMENTO-WEB.md`](./PLANEJAMENTO-WEB.md) Sprint 01.
- **Produção:** hospedagem, HTTPS, e-mail real na recuperação de senha — fora do escopo desta entrega (fluxo demo documentado no `Web/README.md`).

---

## Arquivos principais (referência rápida)

| Caminho | Função |
|---------|--------|
| `Web/backend/app.py` | Rotas Flask e regras da API |
| `Web/backend/storage.py` | Leitura/gravação de usuários, triagens, tokens mobile, reset de senha |
| `Web/js/web-app.js` | Integração JS ↔ API |
| `Web/pages/*.html` | Telas |
| `Web/css/style.css` | Estilos |

---

## Como rodar (1 linha)

```bash
cd Web/backend && pip install -r requirements.txt && python app.py
```

Abrir **http://127.0.0.1:5000** no navegador. Credenciais de admin de demonstração: **`Web/README.md`**.
