# Card 4.3 — Inspeção de logs (dados sensíveis / PII)

- **Data/hora do teste:** 25/11/2026 19:12
- **Versão testada:** `main` em `02a700f` (Merge pull request #24)
- **Resultado:** OK — nenhum dado sensível apareceu no log do Flask

## Como o teste foi feito

1. Backend Flask **local**, na porta **5001**, com `COE_STORAGE=json` (armazenamento em arquivo local, **sem acesso ao Supabase**) e `FLASK_HOST=127.0.0.1`.
   A saída do Flask (stdout + stderr) foi gravada em um arquivo de log fora do repositório.
2. O script [`teste_logs_pii.py`](teste_logs_pii.py) enviou ao backend as operações que carregam dados sensíveis:
   cadastro com CPF e telefone, login com senha errada, login correto, criação de triagem, consulta das próprias triagens,
   pedido de redefinição de senha e redefinição com token.
3. Em seguida, o script procurou no log cada valor sensível enviado: CPF (com e sem máscara), senha, senha nova, e-mail,
   telefone e token de redefinição.
4. Todos os dados usados são **fictícios** (CPF de teste público, e-mail no domínio reservado `example.com`).
5. Ao final, o Flask foi parado e o arquivo local `Web/data/app_storage.json` (ignorado pelo git) foi restaurado ao estado anterior ao teste.

## Saída do `teste_logs_pii.py`

```
=== Respostas da API (status HTTP) ===
cadastro             -> 200
login senha errada   -> 401
login correto        -> 200
triagem              -> 200
minhas triagens      -> 200
pedido de reset      -> 200
reset de senha       -> 200

=== Dados sensíveis encontrados no log do Flask ===
CPF (só números)    : não aparece
CPF (com máscara)   : não aparece
senha               : não aparece
senha nova          : não aparece
e-mail              : não aparece
telefone            : não aparece
token de reset      : não aparece

RESULTADO: OK — nenhum dado sensível no log
```

## Log do Flask (`flask_card43.log`)

A linha do *Debugger PIN* foi removida desta evidência.

```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5001
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
127.0.0.1 - - [25/Nov/2026 19:12:58] "POST /api/auth/register HTTP/1.1" 200 -
127.0.0.1 - - [25/Nov/2026 19:12:58] "POST /api/auth/login HTTP/1.1" 401 -
127.0.0.1 - - [25/Nov/2026 19:12:58] "POST /api/auth/login HTTP/1.1" 200 -
127.0.0.1 - - [25/Nov/2026 19:12:58] "POST /api/triagem HTTP/1.1" 200 -
127.0.0.1 - - [25/Nov/2026 19:12:58] "GET /api/triagem/minhas HTTP/1.1" 200 -
127.0.0.1 - - [25/Nov/2026 19:12:58] "POST /api/auth/forgot-password HTTP/1.1" 200 -
127.0.0.1 - - [25/Nov/2026 19:12:58] "POST /api/auth/reset-password HTTP/1.1" 200 -
```

O log registra apenas método, rota e status HTTP de cada requisição. Corpo das requisições, parâmetros e cabeçalhos não são registrados.

## Observação

O Flask roda com **`Debug mode: on`** (`app.run(..., debug=True)` em `Web/backend/app.py`). Esse modo ativa o depurador
interativo do Werkzeug e **não pode ir para produção**. Em produção, o backend deve rodar com debug desligado e em um
servidor WSGI apropriado.
