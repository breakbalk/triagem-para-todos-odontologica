# Card 3.4 — Validação do cliente Supabase por thread (09/11/2026)

Branch `feature/card-3.4-concorrencia-sb-client`, backend local contra o Supabase real
(`COE_STORAGE=supabase`), medido com `python scripts/medir_latencia.py` (Card 2.2).

## Resultado

| Situação | Sprint 2 (cliente global) | Card 3.4 (cliente por thread + retry) |
|---|---|---|
| 10 usuários simultâneos x 5 pedidos de cada endpoint (script) | 7 erros 500 de 150 (fase concorrente) | **0 erros de 450** na fase concorrente (3 execuções x 150); 0 de 720 contando o uso normal |
| 10 logins simultâneos x 5 rodadas (`POST /api/auth/login`) | 4 de 10 deram 500 na 1ª tentativa | **0 erros de 50** |
| Tempo médio na fila do admin, 10 simultâneos | 339 ms | 452–457 ms |
| Tempo médio ao salvar, 10 simultâneos | 328 ms | 355–403 ms |

Critério de tempo (média <= 2,0 s): atendido nas três execuções (pior média 457 ms).
Log do servidor: nenhuma linha com HTTP 500 nem `RemoteProtocolError`.

O custo é uma média ~100 ms maior na concorrência (cada thread abre o próprio cliente
na primeira requisição); dentro do SLA com folga.

## Limpeza

O usuário `sintetico.latencia@example.com` é apagado no fim de cada execução (triagens e
tokens saem em cascata). Contagem antes e depois, na tabela real: usuarios 105, triagens 221,
mobile_token 3 — iguais.

## Arquivos

- `latencia_20261109_184749.*`, `latencia_20261109_184902.*`, `latencia_20261109_184941.*`:
  relatório e dados brutos de cada execução.

Observação: 3 execuções não provam ausência de erro, só mostram que ele deixou de aparecer
em um cenário em que antes aparecia em quase toda execução.
