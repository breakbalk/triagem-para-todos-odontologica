# Card 4.3 — Validação do backup do banco (Supabase)

- **Arquivo:** `backup_card43_base_limpa.sql` (dump em texto plano)
- **Data/hora do backup:** 25/11/2026 19:48
- **Ferramenta:** `pg_dump` 17.12 — banco de origem PostgreSQL 17.11
- **Schema:** `public`
- **Tamanho:** 112.928 bytes (110,3 KB)
- **Resultado:** backup íntegro — 4 tabelas com dados, restrições e índice único de protocolo presentes

> O arquivo `.sql` **não foi versionado** neste repositório: ele contém dados de usuários e hashes de senha.
> Fica guardado localmente. Esta evidência registra apenas estrutura e contagens — nenhuma linha de dados do dump,
> nome, CPF ou e-mail foi incluída aqui.

## Tabelas e linhas de dados

Contagem das linhas entre cada `COPY public.<tabela> ... FROM stdin;` e o terminador `\.`.

| Tabela | Linhas de dados |
|---|---|
| triagens | 222 |
| usuarios | 107 |
| mobile_token | 15 |
| password_reset | 0 |

## Restrições e índices

| Tipo | Tabela | Definição | Presente |
|---|---|---|---|
| PRIMARY KEY | mobile_token | `mobile_token_pkey (token)` | ✅ |
| PRIMARY KEY | password_reset | `password_reset_pkey (email)` | ✅ |
| PRIMARY KEY | triagens | `triagens_pkey (id_triagem)` | ✅ |
| PRIMARY KEY | usuarios | `usuarios_pkey (id_usuario)` | ✅ |
| UNIQUE | usuarios | `usuarios_cpf_key (cpf)` | ✅ |
| UNIQUE | usuarios | `usuarios_email_key (email)` | ✅ |
| FOREIGN KEY | triagens | `fk_usuario (usuario_id) → usuarios(id_usuario) ON DELETE CASCADE` | ✅ |
| FOREIGN KEY | mobile_token | `mobile_token_usuario_id_fkey (usuario_id) → usuarios(id_usuario) ON DELETE CASCADE` | ✅ |
| NOT NULL | triagens | `protocolo character varying(50) NOT NULL` | ✅ |
| Índice único | triagens | `idx_triagem_protocolo` (UNIQUE, btree em `protocolo`) | ✅ |

Também presentes no dump: índice `idx_triagens_usuario_id`, CHECK `usuarios_cpf_formato` (CPF com exatamente 11 dígitos)
e Row Level Security habilitado nas 4 tabelas.

## Protocolos na tabela `triagens`

| Verificação | Resultado |
|---|---|
| Protocolos lidos | 222 |
| Vazios (`\N` ou em branco) | 0 |
| Distintos | 222 |
| Repetidos | 0 |

## Por que 222 triagens e não 219

As 3 triagens mais recentes do dump foram criadas em 25/11/2026, entre 17:05 e 17:07 (horário de Brasília),
cerca de 2h40 antes do backup. A triagem anterior a elas é de 09/10/2026.

| data_triagem (UTC) | Horário de Brasília | Protocolo |
|---|---|---|
| 2026-11-25 20:05:33 | 25/11 17:05 | TRG-2026-b31f96b4 |
| 2026-11-25 20:06:45 | 25/11 17:06 | TRG-2026-3bf598eb |
| 2026-11-25 20:07:54 | 25/11 17:07 | TRG-2026-30db33a3 |

Essas 3 triagens explicam a diferença entre as 222 encontradas e as 219 esperadas.
