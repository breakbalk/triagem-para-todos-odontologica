# Revalidação do Card 3.4 — 12/11/2026 (depois do rebase na main com o Card 3.6)

Base real (Supabase de produção), backend local com `COE_STORAGE=supabase`, `scripts/medir_latencia.py` 3 vezes (cada uma: 30 pedidos sequenciais por endpoint + 10 usuários simultâneos × 5 pedidos por endpoint).

| Execução | Pedidos | Erros 500 |
|---|---|---|
| 1 | 240 | 0 |
| 2 | 240 | 0 |
| 3 | 240 | 0 |

**0 erros em 720 pedidos** (Sprint 2: 7 de 150 na fila com 10 simultâneos). Concorrência, média: salvar 204–285 ms, minhas 189–296 ms, fila 323–409 ms; pior máximo 676 ms. Critério de 2,0 s atendido.
Os relatórios de duas execuções estão nesta pasta (`latencia_20261112_*`).
Banco antes e depois: usuarios 105, triagens 221, mobile_token 8; usuário sintético apagado.

## Dívida técnica (observações da revisão da Maria, não bloqueantes)
- Clientes por thread não são fechados explicitamente nem há pool com limite: em servidor com muitas threads vivas cada uma mantém seu cliente.
- O retry cobre só `httpx.RemoteProtocolError` (o erro observado); outros erros de rede (timeouts, `ConnectError`) não repetem.
