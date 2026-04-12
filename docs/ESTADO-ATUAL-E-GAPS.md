# Estado atual do repositório e lacunas

**Referência:** relatórios extensionistas (Mobile — Lucas Marques Maciel; Web incremental — equipe, 01/04/2026).  
**Data desta análise:** 12/04/2026.

## Visão alinhada aos documentos

Os dois relatórios descrevem o mesmo domínio (**COE — Clínica Odontológica de Ensino, UniEVANGÉLICA**), o mesmo problema (triagem presencial/telefônica com gargalos) e requisitos funcionais comuns (**RF01–RF11**): cadastro, login, recuperação de senha, formulário de triagem (nome, telefone, serviço, período), confirmação/pré-agendamento, orientações sobre documentos e navegação entre telas.

**Backlog Kanban:** [Trello — Triagem Para Todos Odontológica](https://trello.com/b/nlhKm18f/triagem-para-todos-odontologica) (criado em 27/03/2026).

**Restrições institucionais (ambos os relatórios):** sistema legado (Policlínicas) sem API; hardware modesto; poucos dispositivos móveis na instituição — a solução deve ser leve e sem depender de integração complexa no MVP.

---

## O que já existe no repositório (evidência no código)

| Área | Situação |
|------|----------|
| **Web — identidade visual e telas de autenticação** | `Web/pages/login.html` e `Web/pages/cadastro.html` com formulários, links entre si e para recuperação de senha; `Web/css/style.css` e `Web/js/script.js` com validação de nome de usuário, senha e feedback visual no envio. |
| **Web — ativos de interface** | Imagens responsivas e identidade em `Web/assets/img/` (login/cadastro desktop, tablet, mobile, ícone). |
| **README raiz** | Descreve arquitetura alvo (cliente-servidor, Python, Supabase), MER, sprints e equipe. |
| **Mobile** | Estrutura de pastas (`screens`, `navigation`, `services`, `components`) e arquivos nomeados (login, cadastro, recuperação, home, triagem, sucesso), porém **sem implementação útil nos blobs versionados** (arquivos vazios no histórico Git). |
| **Backend / páginas Web** | API Flask em `Web/backend/app.py` + persistência em JSON (`storage.py`). Páginas em `Web/pages/` (login, cadastro, home, triagem, confirmação, admin, recuperar senha). **Supabase** (tabelas/SQL no painel ou migrações) ainda é responsabilidade de outro membro — trocar `storage.py` quando o BD existir. |

---

## Lacunas em relação ao MVP dos relatórios

1. **Supabase:** modelagem relacional (PostgreSQL) e substituição de `storage.py` por banco — pendente conforme divisão da equipe.
2. **Produção:** hospedagem, HTTPS, e-mail real na recuperação de senha (hoje há fluxo demo com token no JSON).
3. **Mobile (React Native):** app ainda precisa de implementação real (telas + `api.js` apontando para este servidor).
4. **README raiz:** pode estar desatualizado em relação ao mobile; o detalhe da web está em `Web/README.md` e neste `docs/`.

---

## Calendário de sprints (documentos oficiais)

| Sprint | Período (2026) | Foco resumido |
|--------|----------------|---------------|
| 01 | 06/04 – 19/04 | Ambiente, BD, cadastro/login (web); ambiente + autenticação (mobile) |
| 02 | 20/04 – 03/05 | Formulário de triagem e navegação (web); home + triagem no app (mobile) |
| 03 | 04/05 – 17/05 | Persistência + painel admin (web); integração com API (mobile) |
| 04 | 18/05 – 01/06 | Confirmação, orientações, testes/UI (web); confirmação e polimento (mobile) |

---

## Próximos passos documentados

- **Web:** `docs/PLANEJAMENTO-WEB.md`
- **Mobile:** `docs/PLANEJAMENTO-MOBILE.md`
