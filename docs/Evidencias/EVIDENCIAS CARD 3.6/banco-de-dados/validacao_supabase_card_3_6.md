# Evidência — Card 3.6: DDL + backfill validados na base real do Supabase

**Projeto:** Triagem para Todos (`vyimivjsbovvqlmcztyk`) · **Tabela:** `public.triagens`
**Migração aplicada:** `20261110002707 card_3_6_triagens_protocolo_unique`
**Validação executada em:** 2026-11-10 14:38:51 UTC (consulta real via SQL na base de produção)
**Scripts:** `sql/card_3_6_protocolo.sql` (DDL + backfill) · `sql/ris_rollback.sql` / `sql/rls_rollback.sql` (rollback)

> Registro textual gerado a partir da saída real das consultas. Não é captura de tela da interface do Supabase;
> para o relatório, recomenda-se anexar também um print do SQL Editor executando a consulta abaixo.

## Consulta de validação
```sql
SELECT now() AS executado_em,
 (SELECT COUNT(*) FROM public.triagens) AS total_linhas,
 (SELECT COUNT(*) FROM public.triagens WHERE protocolo IS NULL) AS protocolos_nulos,
 (SELECT COUNT(*) FROM (SELECT protocolo FROM public.triagens GROUP BY protocolo HAVING COUNT(*)>1) d) AS protocolos_duplicados,
 (SELECT COUNT(DISTINCT protocolo) FROM public.triagens) AS protocolos_distintos;
```

## Resultado
| Verificação | Resultado |
|---|---|
| Linhas na tabela (nenhuma perdida) | **221** |
| Protocolos NULL | **0** |
| Protocolos duplicados | **0** |
| Protocolos distintos | **221** (= total de linhas) |
| Formato `TRG-AAAA-xxxxxxxx` | 221 de 221 |
| Prefixos de 8 hex do UUID distintos | 221 (nenhuma colisão) |
| Coluna `protocolo` | `NOT NULL` (is_nullable = NO) |
| Índice | `CREATE UNIQUE INDEX idx_triagem_protocolo ON public.triagens USING btree (protocolo)` |
| Teste de unicidade | inserção de protocolo duplicado rejeitada pelo índice (registro de teste removido) |
| Plano de consulta | Index Scan em `idx_triagem_protocolo` |

**Conclusão:** DDL e backfill executados sem perda de dados e sem inconsistências.

## Rollback
`sql/ris_rollback.sql` (cópia idêntica `sql/rls_rollback.sql`): remove `idx_triagem_protocolo` e a coluna `protocolo` em transação (`BEGIN … COMMIT`).

## Tratamento de colisões (60 mil registros)
O protocolo usa 8 caracteres hexadecimais do UUID (16^8 ≈ 4,29 bilhões de combinações), por ano.
Pelo paradoxo do aniversário, P = 1 − e^(−n(n−1)/2N):

| Registros (mesmo ano) | Probabilidade de ≥1 colisão |
|---|---|
| 221 (atual) | 0,0006% |
| 10.000 | 1,16% |
| **60.000** | **34,24%** |
| 100.000 | 68,78% |

Como a regra está hoje:
- **Backfill:** colisões existentes são resolvidas (2ª ocorrência em diante recebe `-` + 4 últimos chars do UUID) e uma trava aborta a migração se sobrar NULL/duplicado.
- **Novos registros:** o `UNIQUE INDEX` impede duplicata (o INSERT falha, sem corromper dados), mas **não regenera** o protocolo automaticamente.

Recomendação (a decidir com o time): (a) usar o UUID completo ou ≥12 chars hex; ou (b) gerar o protocolo no banco com função/trigger que verifica existência e tenta novamente; no mínimo, o backend deve tratar `unique_violation` com novo sorteio e retry.
