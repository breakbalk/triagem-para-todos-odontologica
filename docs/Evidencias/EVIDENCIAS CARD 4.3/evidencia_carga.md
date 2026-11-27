# Card 4.3 — Teste de carga concorrente

- **Data/hora:** 25/11/2026 19:59
- **Versão testada:** `main` em `02a700f`
- **Backend:** Flask local na porta 5000, com `COE_STORAGE=supabase`
- **Usuário de teste:** `sintetico.latencia@example.com` (fixo; liberado para a fila apenas nesta execução, via variável de ambiente)
- **Comando:** `scripts\medir_latencia.py --manter --saida "docs\Evidencias\EVIDENCIAS CARD 4.3"`
- **Carga:** uso normal (30 rodadas de cada endpoint, uma por vez) + concorrência (10 usuários simultâneos, 5 pedidos de cada endpoint por usuário)

## Resumo

| Fase | Endpoint | Pedidos | Erros | Média | Mediana | p95 | Máximo |
|---|---|---|---|---|---|---|---|
| uso normal | `POST /api/triagem` | 30 | 0 | 644 ms | 639 ms | 666 ms | 763 ms |
| uso normal | `GET /api/triagem/minhas` | 30 | 0 | 639 ms | 634 ms | 666 ms | 668 ms |
| uso normal | `GET /api/triagem/admin/todas` | 30 | 0 | 722 ms | 719 ms | 776 ms | 779 ms |
| concorrência | `POST /api/triagem` | 50 | 0 | 1389 ms | 1343 ms | 1655 ms | 1829 ms |
| concorrência | `GET /api/triagem/minhas` | 50 | 0 | 1377 ms | 1344 ms | 1622 ms | 1899 ms |
| concorrência | `GET /api/triagem/admin/todas` | 50 | 0 | 1489 ms | 1522 ms | 1632 ms | 1862 ms |

## Resultado

- **240 pedidos, 0 erros.**
- **0 HTTP 500:** o log do Flask teve 254 linhas de acesso, todas com status 200, e nenhum Traceback.
- **Todas as médias ≤ 2,0 s** — critério de aceite atendido.

## Nota: idempotência sob concorrência

Só 1 das 80 tentativas de `POST /api/triagem` gravou linha nova. O script envia sempre os mesmos dados, e a janela de
reenvio de 120 s do Card 3.5 (`JANELA_REENVIO_S` em `Web/backend/storage_supabase.py`) devolve a triagem já existente
quando a mesma pessoa reenvia dados idênticos. A idempotência se manteve sob concorrência: nenhuma triagem duplicada.

## Base depois da carga

Logo após a carga, a base tinha **223 = 222 + 1** triagens (as 222 do backup validado em `evidencia_backup.md` + a
triagem criada pelo teste).

**Limpeza feita em 25/11/2026 20:17** com `scripts\medir_latencia.py --limpar`. O script apagou o usuário de teste, e a
triagem dele saiu em cascata (`ON DELETE CASCADE`). Saída: `[LATENCIA] Usuário de teste apagado: 1 (triagens e tokens dele em cascata)`.

| Contagem | Antes | Depois |
|---|---|---|
| Triagens (total) | 223 | 222 |
| Usuários `sintetico.latencia@example.com` | 1 | 0 |
| Usuários `latencia*` / `sintetico.latencia*` `@example.com` | 1 | 0 |

Base de volta ao estado do backup (**222 triagens**).

## Arquivos

- `latencia_20261125_195911.md` e `latencia_20261125_195911.csv` são a saída bruta do script.
