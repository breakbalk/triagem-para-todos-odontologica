# Revisão do Card 3.4 — erro 500 no cliente Supabase (PR #18)

Revisora: Maria Eduarda · Autor: Lucas Maciel · Revisão feita em 11/11/2026

**Veredito: aprovado, com 2 observações não bloqueantes.**

## O que o PR faz
- O cliente global `_sb_client` virou um cliente por thread (`threading.local()`).
- Leituras e updates repetem até 3 vezes em `httpx.RemoteProtocolError`; o INSERT não repete sozinho.
- `httpx` entrou no `requirements.txt`.

## Conferência
| Item | Resultado |
|---|---|
| Testes offline | 30 verdes (executados na revisão) |
| Erros 500 na concorrência | 0 em 450 requisições (3 execuções), contra 7 de 150 na Sprint 2 |
| Tempo médio (limite 2,0 s) | até 457 ms: atende |
| Limpeza do banco | usuários 105, triagens 221 e tokens 3, iguais antes e depois |
| Evidências anexadas | relatórios e CSV das 3 execuções e `resumo_3.4.md` |

## Observações (não bloqueantes)
1. O servidor de desenvolvimento do Flask cria uma thread por requisição, e cada thread abre um cliente novo que ninguém fecha. Em uso prolongado isso pode acumular conexões e explica a média cerca de 100 ms maior. Registrar como débito técnico ou usar um pool de clientes.
2. O retry cobre só `RemoteProtocolError`; timeouts e outros erros de rede não são repetidos.

O autor ressalva que 3 execuções não provam a ausência de erro. A revisão concorda com essa leitura.

## Encaminhamento
As duas observações foram registradas como dívida técnica em `revalidacao_12-11.md`, junto com a nova medição de 12/11 (0 erros em 720 pedidos).
