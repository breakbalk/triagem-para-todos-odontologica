# Card 3.5 — Validação na base real: queda de conexão depois do envio (09/11/2026)

Branch `feature/card-3.5-protocolo-idempotente`, Supabase real (`COE_STORAGE=supabase`),
script `python scripts/queda_pos_envio.py` (usuário `sintetico.latencia@example.com`, apagado no fim
com `python scripts/medir_latencia.py --limpar`).

O script faz o insert chegar ao banco e então levanta `httpx.RemoteProtocolError` (a resposta se perde),
exatamente o cenário que deixava a triagem com protocolo `__TEMP__` e o paciente com erro.

```
1) queda simulada após o insert: quedas=1, linhas no banco=1, protocolo=TRG-2026-7e1b1fb7, id=7e1b1fb7-306f-4267-a317-6394aee3077d
2) reenvio idêntico: linhas=1, mesmo id=True, mesmo protocolo=True
3) dados diferentes: linhas=2, protocolos distintos=True
órfãos/__TEMP__ no banco: 0
OK
```

| Verificação direta no Supabase | Resultado |
|---|---|
| Linhas da triagem depois da queda + retry | 1 (sem duplicata) |
| `__TEMP__` em `solicitacao_dados` | 0 |
| Protocolo no formato `TRG-ano-xxxxxxxx`, igual aos 8 primeiros caracteres do UUID | sim |
| Reenvio idêntico em até 2 min | devolve a mesma triagem (mesmo id e protocolo) |
| Dados diferentes | nova triagem, protocolo próprio |
| Contagem depois da limpeza | usuarios 105, triagens 221, mobile_token 3 (iguais às de antes) |

Observação: `medir_latencia.py` manda sempre os mesmos dados; com a idempotência, os POSTs
repetidos do mesmo usuário em 2 min viram uma triagem só. A carga de 10 usuários do Card 3.4 vale
para leitura e login; a escrita está coberta aqui e nos testes offline.
