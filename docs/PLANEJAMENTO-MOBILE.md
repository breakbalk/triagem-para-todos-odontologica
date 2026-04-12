# Planejamento — parte Mobile (próximas entregas)

Base: *Relatório de Desenvolvimento — Programação Mobile Aplicada* (Lucas Marques Maciel, versão 1.0, 04/04/2026) e repositório atual.

## Escopo do app

- **Nome:** COE (Clínica Odontológica de Ensino).  
- **Plataforma alvo:** Android (React Native, conforme relatório).  
- **Papel:** extensão do projeto web — mesmos requisitos RF01–RF11, com foco em touch, telas pequenas e baixo consumo (RNF mobile).

## Modelo de dados (relatório mobile)

Além de usuários e triagens, o documento cita tabela de **Status** (Pendente, Analisado, Confirmado). Alinhar com o backend web na Sprint 03 ou incluir campo `status` em `triagem` para evitar divergência entre web e app.

---

## Sprint 01 (06/04/2026 – 19/04/2026)

**Objetivo:** ambiente React Native (Expo recomendado para builds rápidos em Android), estrutura de pastas, navegação, fluxo de autenticação.

| Tarefa | Detalhe |
|--------|---------|
| Bootstrap do projeto | `Mobile/package.json`, `app.json`, `babel.config.js`, Expo ~52. |
| Navegação | Stack em `App.js`: Login, Cadastro, Recuperar, Home. |
| Telas | `src/screens/*` — RF01–RF03 + Home placeholder para Sprint 2. |
| Estado de auth | `AsyncStorage` + `mobile_token` devolvido pela API (`Authorization: Bearer`); ver `Mobile/README.md`. |

**Backend:** `Web/backend` grava tokens em `mobile_tokens` no JSON e aceita Bearer nas mesmas rotas que usam sessão no navegador.

---

## Sprint 02 (20/04/2026 – 03/05/2026)

**Objetivo:** Home com “Nova triagem” e “Meus agendamentos”; fluxo de triagem com etapas simples (dados pessoais → sintomas/descrição se aplicável → especialidade/serviço).

| Tarefa | Detalhe |
|--------|---------|
| Home | Botões grandes, acessíveis ao polegar; lista vazia tratada com mensagem amigável. |
| Formulário | RF04–RF06: nome, telefone, tipo de serviço, período; validação inline. |
| UX | Barra de progresso entre etapas (conforme wireframe do relatório); radios/selects grandes em vez de texto livre quando possível. |

---

## Sprint 03 (04/05/2026 – 17/05/2026)

**Objetivo:** integração com o backend (mesma API do web).

| Tarefa | Detalhe |
|--------|---------|
| `src/services/api.js` | Base URL configurável (`EXPO_PUBLIC_API_URL` ou `.env`); `fetch`/`axios` com tratamento de erro de rede. |
| Endpoints | Login, registro, envio de triagem, listagem “meus” para a home. |
| Offline leve (opcional) | Fila local ou mensagem clara se não houver conexão (RNF rede móvel). |

---

## Sprint 04 (18/05/2026 – 01/06/2026)

**Objetivo:** tela de confirmação com resumo e protocolo; polimento UI/UX; testes em aparelho real.

| Tarefa | Detalhe |
|--------|---------|
| Confirmação | RF08–RF09; exibir orientações RF10 (documentos). |
| Feedback | Toasts ou modais para sucesso/erro; loading em botões. |
| Entrega | APK para testes na clínica; preencher tabela de implantação do relatório (instalado / APK / loja). |

---

## Dependências críticas

1. **API web estável** — o app não deve mockar dados em produção além do necessário para desenvolvimento.  
2. **Contrato único** — mesmos nomes de campos JSON que o front web e o backend.  
3. **LGPD** — não logar dados sensíveis em console em build de release.

---

## Sugestões de “próximos passos” (pós-MVP, relatório)

- Publicação em loja (Google Play), se houver política institucional.  
- Notificações push para lembrete de consulta (depende de backend e política da clínica).  
- Melhorias de acessibilidade (TalkBack, contraste, tamanho de fonte).
