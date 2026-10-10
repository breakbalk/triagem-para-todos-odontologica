# Card 2.2 [T05/MQ05] — Latência das APIs

Critério de aceite: **tempo médio ≤ 2,0 s** para salvar triagem e consultar a fila.

Endpoints medidos:

| Ação | Endpoint |
|---|---|
| Salvar triagem | `POST /api/triagem` |
| Paciente vê as próprias triagens | `GET /api/triagem/minhas` |
| Recepção consulta a fila | `GET /api/triagem/admin/todas` |

## 1. Preparar o backend

No `Web/backend/.env` (nunca commitar):

```
COE_STORAGE=supabase
SUPABASE_URL=...
SUPABASE_KEY=...            # chave secret (service_role): o RLS bloqueia a anon
COE_SECRETARIA_EMAILS=sintetico.latencia@example.com
```

A fila só abre para admin ou secretaria. A linha `COE_SECRETARIA_EMAILS` dá esse
acesso ao usuário de teste, assim ninguém precisa usar a senha do admin.

Suba o backend: `cd Web/backend && python app.py`

## 2. Medição automática (script)

Da raiz do repositório:

```
pip install -r scripts/requirements-dev.txt
python scripts/medir_latencia.py
```

Ele roda em duas fases:

- **Uso normal:** 30 pedidos de cada endpoint, um por vez (`--rodadas`).
- **Concorrência moderada:** 10 usuários ao mesmo tempo (`--usuarios`), cada um com
  sessão própria, fazendo 5 pedidos de cada endpoint (`--lote`).

O resultado tem média, mediana, p95, máximo e o veredito (APROVADO ou REPROVADO).
Ele sai em `docs/Evidencias/EVIDENCIA CARD 2.2/`, como `.md` (tabela) e `.csv`
(cada pedido).

Dados de teste:

- usuário `sintetico.latencia@example.com` (domínio reservado, RFC 2606), com senha
  aleatória que não é gravada;
- telefone `(00) 90000-0000` e "LATENCIA" no sintoma.

No fim, o script apaga o usuário, e as triagens e tokens dele saem junto
(ON DELETE CASCADE). Com os valores padrão, uma execução grava 80 triagens.

Se a execução cair no meio, rode `python scripts/medir_latencia.py --limpar`.

## 3. Medição no Postman (checklist do card)

1. Importe `COE-latencia.postman_collection.json`.
2. Rode **"0. Cadastrar usuário de teste (uma vez)"**. Ele gera a senha sozinho.
3. Para medir **um pedido de cada vez**, abra a pasta **Medição** e clique em
   **Run** (Collection Runner). Use Iterations = 30. O Runner mostra o tempo de
   cada pedido e a média.
4. Para medir **em lote ou com usuários ao mesmo tempo**, use a mesma pasta, aba
   **Performance**, com 10 usuários virtuais e duração de 1 minuto. O Postman mostra
   a média, o p90 e os erros.
5. No fim, apague o usuário de teste com `python scripts/medir_latencia.py --limpar`.

Cada pedido testa se o status é 200 e se respondeu em até 2,0 s.

## Testes do script (offline)

```
python -m unittest scripts/test_medir_latencia.py
```

Sobe o backend com storage JSON numa thread. Não acessa o Supabase.
