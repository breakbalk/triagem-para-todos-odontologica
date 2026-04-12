# Pasta Web — Triagem Para Todos

Frontend (HTML/CSS/JS) + **API Flask** para desenvolvimento **sem Supabase** (persistência local em JSON por enquanto).

Quem implementar o banco: substitua `backend/storage.py` por integração com **Supabase** (ou consultas SQL ao Postgres) e chame essas funções a partir de `backend/app.py` (todas as URLs `/api/...` estão neste arquivo).

## Rodar o sistema completo (recomendado)

Na pasta `Web/backend`:

```bash
pip install -r requirements.txt
python app.py
```

O servidor sobe em **`0.0.0.0:5000`** por padrão (assim o **app mobile** na mesma rede Wi‑Fi alcança o PC). No navegador use **http://127.0.0.1:5000/** ou **http://localhost:5000/**.

**Resposta do login/cadastro:** além de `user`, a API pode enviar `mobile_token` (usado pelo app React Native no header `Authorization`; o site web ignora esse campo).

### Usuário administrador de demonstração

Na **primeira execução** é criado um admin (dados gravados em `Web/data/app_storage.json`, ignorado no git).

| Variável | Padrão |
|----------|--------|
| `COE_ADMIN_EMAIL` | `admin@coe.unievangelica.edu.br` |
| `COE_ADMIN_PASSWORD` | `Admin@coe2026` |

Use esse e-mail e senha no login para acessar **Painel equipe** (`/pages/admin.html`).

### Recuperação de senha (RF03) em modo demo

Com `COE_DEMO_RESET_TOKEN=1` (padrão), após informar o e-mail a API devolve um `demo_token` para você colar na segunda etapa (em produção viria por e-mail).

## Estrutura principal

| Caminho | Uso |
|---------|-----|
| `pages/` | Telas: login, cadastro, recuperar senha, home, triagem, confirmação, admin. |
| `css/style.css` | Estilos globais + layout das telas logadas. |
| `js/web-app.js` | Chamadas `fetch` à API e lógica por página (`data-page` no `<body>`). |
| `backend/` | `app.py` (Flask + todas as rotas `/api`), `storage.py` (JSON). |
| `data/` | Arquivo gerado localmente `app_storage.json` (não versionar). |

## Só o front (sem API)

Se abrir HTML com `python -m http.server`, login e triagem **não funcionarão** (não há `/api`). Use sempre o Flask acima.

## Documentação do projeto

- [`../docs/PLANEJAMENTO-WEB.md`](../docs/PLANEJAMENTO-WEB.md)
- [`../docs/ESTADO-ATUAL-E-GAPS.md`](../docs/ESTADO-ATUAL-E-GAPS.md)
