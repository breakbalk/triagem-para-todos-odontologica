# Planejamento — parte Web (próximas entregas)

Base: *Relatório Incremental — Triagem Para Todos* (UniEVANGÉLICA, 01/04/2026) e estado atual do repositório.

## Objetivo do MVP (web)

Aplicação leve em navegador: cadastro/login, triagem digital com serviço e período, gravação em banco, painel para a equipe, tela de confirmação com orientações — **sem dependência de integração com Policlínicas** no escopo inicial.

---

## Sprint 01 (06/04/2026 – 19/04/2026) — status e o que falta

**Planejado no relatório:** modelagem do banco (usuários e triagens); ambiente Python + **Supabase** (PostgreSQL); cadastro e login; interfaces de autenticação.

| Entrega | Status sugerido | Ações |
|---------|-----------------|--------|
| MER / SQL no Supabase | Pendente | Criar tabelas `usuario` e `triagem` conforme README raiz (SQL Editor ou migrações); índices em `email`; charset UTF-8. |
| Backend (Flask) | **Em andamento no repo** | `Web/backend/app.py` concentra as rotas `/api/auth/*` e `/api/triagem/*`; dados em JSON via `storage.py` até o Supabase existir. |
| Cadastro / Login funcionais | Funcional (JSON local, sem Supabase) | Front chama `POST /api/auth/register` e `POST /api/auth/login`; sessão Flask. |
| Recuperar senha | Funcional (demo) | `forgot-password` + `reset-password`; token visível em modo demo (`COE_DEMO_RESET_TOKEN`). |

---

## Sprint 02 (20/04/2026 – 03/05/2026)

**Planejado:** tela inicial, navegação, formulário de triagem (nome, telefone, serviço, período), validação no backend.

| Tarefa | Detalhe |
|--------|---------|
| `home.html` | Pós-login: atalho para nova triagem e lista/resumo de solicitações do usuário. |
| `triagem.html` | Campos alinhados a RF04–RF06: nome, telefone; serviço (tratamento geral, prótese, pediatria, emergência); período (matutino, vespertino, noturno). |
| Validação server-side | Tipos, tamanhos, enum de serviço/período; associar triagem ao `id_usuario` autenticado. |
| Navegação | Fluxo linear: login → home → triagem → confirmação (ou erro); links consistentes com `Web/css` e `Web/js` (evitar duplicar `Web/css` vs `Web/assets/css` — padronizar uma árvore). |

---

## Sprint 03 (04/05/2026 – 17/05/2026)

**Planejado:** persistência, painel administrativo, listagem de triagens.

| Tarefa | Detalhe |
|--------|---------|
| API triagem | `POST` criar; `GET` listar (admin); `GET` por usuário (paciente). |
| `admin.html` + JS | Tabela ou cards com filtros básicos; opcional: campo de status (alinhado ao modelo mobile: Pendente / Analisado / Confirmado) se o MER for estendido. |
| Segurança mínima | Rota admin protegida (usuário equipe ou role); nunca expor senhas. |

---

## Sprint 04 (18/05/2026 – 01/06/2026)

**Planejado:** confirmação (pré-agendamento), resumo, orientações, testes, ajustes de UI/UX.

| Tarefa | Detalhe |
|--------|---------|
| `confirmacao.html` | RF08–RF09: exibir serviço e, se o backend gerar, data/horário ou protocolo. |
| Orientações RF10 | Texto fixo ou vindo do backend: RG/CPF, cartão SUS, comprovante de residência. |
| Testes | Fluxo completo em navegador; responsividade (RNF web do relatório). |
| Implantação | Preencher relatório: hospedado vs. local; se possível, link ou ambiente de testes. |

---

## Riscos e dependências

- **Duplicidade de estilos/scripts:** existem `Web/css`, `Web/js`, `Web/assets/css`, `Web/assets/js` — unificar para manutenção e caminhos relativos corretos.
- **E-mail:** recuperação de senha pode exigir configuração SMTP; documentar variáveis de ambiente.
- **Mobile:** o app consumirá a mesma API; estabilizar contratos JSON (login, triagem, listagem) nesta fase.

---

## Checklist rápido de “pronto para integrar mobile”

- [ ] API documentada (endpoints, payloads, códigos de erro).
- [ ] Triagem criada retorna identificador/protocolo para exibir na confirmação.
- [ ] CORS e HTTPS considerados para testes em dispositivo real.
