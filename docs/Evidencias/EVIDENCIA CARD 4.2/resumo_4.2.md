# Evidência — Card 4.2 (refatoração e limpeza de code smells)

Responsável: Lucas Maciel · Revisor: Cristiano Machado · Execução: 23/11/2026

## O que saiu (sem mudar comportamento)
| Item | Motivo |
|---|---|
| `Web/assets/css/style.css`, `Web/assets/js/{auth,main,triagem}.js` | arquivos vazios (0 bytes), sem nenhuma referência no projeto |
| `Web/backend/db.py`, `Web/backend/models.py` | arquivos vazios (0 bytes), ninguém importa |
| `Web/index.html` | vazio (0 bytes); a rota `/` já redireciona para `/pages/login.html` |
| `Web/js/script.js` | protótipo antigo, nenhuma página linka (todas usam `web-app.js`); só imprimia um aviso no console |
| `usuario_eh_admin()` em `app.py` | função morta; o código usa `usuario_tem_acesso_admin()` |
| `cpf_limpo` em `storage_json.py` e `storage_supabase.py` | variável calculada e nunca usada |
| `console.log` de depuração em `Mobile/src/config.js` | log de desenvolvimento (a importação `Device` continua em uso) |
| Comentário "Flask/FastAPI" em `test_routes.py` | o projeto só usa Flask; também tirado um espaço sobrando |

## O que ficou de propósito
- `print()` em `scripts/*.py` e `Web/tools/minify_css.py`: são a saída de linha de comando desses utilitários, não depuração.
- `console.warn` em `web-app.js` (falha de conexão): é tratamento de erro do Card 3.3.
- Importações de `storage.py`: é a fachada que reexporta o backend escolhido; o analisador acusa "não usado", mas é o propósito do arquivo.

## Validação
- Testes do backend: **40 passaram** antes e depois.
- Análise estática (pyflakes) nos arquivos alterados: sem alertas novos.
- Inicialização local (`python app.py`, armazenamento JSON): `/health` 200, `/pages/login.html` 200, `/pages/admin.html` 200, `/css/style.min.css` 200, `/js/web-app.js` 200. `/index.html` passa a dar 404 (antes servia página em branco).
- Nenhuma rota ou regra de negócio foi alterada.

## Fora do escopo desta entrega
- Padronização de nomes (variáveis em português e inglês misturadas): mexer em nomes de API/JSON quebraria web e mobile; ficou como sugestão para depois dos testes E2E do 4.1.
- Build do Mobile (Expo): não rodado aqui; a única mudança é a remoção de um bloco `console.log`.
