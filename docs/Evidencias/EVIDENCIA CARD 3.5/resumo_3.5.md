# Evidência — Card 3.5 (protocolo gerado no app + reenvio idempotente)

Revalidação de **12/11/2026**, depois do rebase na `main` (que traz o Card 3.6: `triagens.protocolo` NOT NULL + índice único) e do conserto apontado na revisão da Maria Eduarda.
A validação de 09/11 foi feita antes da migração do 3.6 e **deixou de valer**.

## O que mudou no código
- O insert agora envia a coluna `protocolo` (igual ao `TRG-<ano>-<8 hex>` que também vai em `solicitacao_dados`).
- Erro 23505 no insert: se a linha com aquele `id_triagem` já existe (1ª tentativa gravou e a resposta se perdeu), devolve essa linha; se não existe, é colisão do protocolo → gera **novo UUID** e tenta de novo (até 5 vezes).
- Banco falso dos testes agora exige `protocolo` (23502) e único (23505); 3 testes novos. Suíte do backend: 40 testes verdes.

## Execução na base real (Supabase de produção, `scripts/queda_pos_envio.py`)
Usuário sintético `sintetico.latencia@example.com`, apagado no fim.

```
1) queda simulada após o insert: quedas=1, linhas no banco=1, protocolo=TRG-2026-75fda5d5, id=75fda5d5-317d-4cb5-b193-d552e51ad588
2) reenvio idêntico: linhas=1, mesmo id=True, mesmo protocolo=True
3) dados diferentes: linhas=2, protocolos distintos=True
órfãos/__TEMP__ no banco: 0
OK
```

- Queda de conexão logo depois do insert gravar: **1 linha só**, sem `__TEMP__`, sem update.
- Reenvio do mesmo formulário: devolve a mesma triagem (mesmo id e protocolo).
- Dados diferentes: outra triagem, protocolo próprio.
- O insert passou com `protocolo` NOT NULL ativo (o que falhava antes do conserto).
- Banco antes e depois: usuarios 105, triagens 221, mobile_token 8 (iguais).
