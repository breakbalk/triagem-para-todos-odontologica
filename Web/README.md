# Pasta Web — Triagem Para Todos

Frontend (HTML/CSS/JS) + **API Flask**. A persistência pode ser **JSON local** (padrão) ou **Supabase (PostgreSQL)**.

## Rodar o sistema completo (recomendado)

Na pasta `Web/backend`:

```bash
pip install -r requirements.txt
python app.py
```

O servidor sobe em **`0.0.0.0:5000`** por padrão (assim o **app mobile** na mesma rede Wi‑Fi alcança o PC). No navegador use **http://127.0.0.1:5000/** ou **http://localhost:5000/**.

**Resposta do login/cadastro:** além de `user`, a API pode enviar `mobile_token` (usado pelo app React Native no header `Authorization`; o site web ignora esse campo).

### Persistência: JSON (padrão)

Sem arquivo `.env` ou com `COE_STORAGE=json`, os dados vão para `Web/data/app_storage.json` (ignorado no Git).

### Persistência: Supabase

1. No painel do Supabase, abra **SQL**:
   - **Projeto novo / tabelas ainda não criadas:** rode [`supabase/schema.sql`](./supabase/schema.sql) inteiro.
   - **`usuarios` e `triagens` já existem** (mesmo MER, podem estar vazias): rode só [`supabase/schema_auxiliar_flask.sql`](./supabase/schema_auxiliar_flask.sql) — cria `password_reset` e `mobile_token` e não mexe nas tabelas da equipe.  
   Dados extras da triagem no app (nome, telefone, sintomas, status, protocolo) ficam em **`triagens.solicitacao_dados`** como JSON.
2. Copie `Web/backend/.env.example` para `Web/backend/.env`.
3. Preencha:
   - `COE_STORAGE=supabase`
   - `SUPABASE_URL` — URL do projeto (ex.: `https://xxxx.supabase.co`)
   - `SUPABASE_KEY` — no Flask, use de preferência a chave **`service_role`** (*Project Settings → API*). Ela ignora RLS e é **secreta**: não coloque no mobile nem em repositório público. A chave **anon** só funciona se você criar políticas RLS permissivas (não recomendado para este backend).
4. Rode `python app.py` de novo.

Variáveis completas: ver `Web/backend/.env.example`.

### Usuário administrador de demonstração

Na **primeira execução** sem usuários no banco, é criado um admin.

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
| `backend/` | `app.py` (Flask), `storage.py` (escolhe JSON ou Supabase), `storage_json.py`, `storage_supabase.py`. |
| `data/` | `app_storage.json` só no modo JSON (não versionar). |
| `supabase/schema.sql` | DDL para criar tabelas no Supabase. |

## Só o front (sem API)

Se abrir HTML com `python -m http.server`, login e triagem **não funcionarão** (não há `/api`). Use sempre o Flask acima.

## Documentação do projeto

- [`../docs/ENTREGAS-SPRINT-01-WEB.md`](../docs/ENTREGAS-SPRINT-01-WEB.md) — resumo das entregas da **Sprint 1** (web) para a equipe
- [`../docs/PLANEJAMENTO-WEB.md`](../docs/PLANEJAMENTO-WEB.md)
- [`../docs/ESTADO-ATUAL-E-GAPS.md`](../docs/ESTADO-ATUAL-E-GAPS.md)
