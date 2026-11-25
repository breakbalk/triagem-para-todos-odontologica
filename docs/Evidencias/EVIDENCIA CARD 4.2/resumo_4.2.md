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

## Padronização de nomenclatura (só nomes internos)
Convenção que já vale no projeto e foi mantida: Python em `snake_case`, JavaScript em `camelCase`, constantes em `MAIUSCULAS_COM_UNDERLINE`, nomes de funções em português (`criar_`, `listar_`, `buscar_`, `iniciar...`). Os desvios encontrados e corrigidos:
| Antes | Depois | Onde |
|---|---|---|
| `init_storage` (inglês) | `iniciar_storage` | `storage.py`, `storage_json.py`, `storage_supabase.py`, `app.py` |
| `insert_triagem` (inglês) | `inserir_triagem` | `storage.py`, `storage_json.py`, `storage_supabase.py`, `app.py`, `tests/test_api_triagem.py` |
| `_host`, `_porta` (underline na frente, fora do padrão JS) | `host`, `porta` | `Mobile/src/config.js` |

Ficou de fora de propósito: chaves do JSON, rotas e campos da API, que são o contrato entre Web e Mobile e não mudam antes dos testes E2E (4.1) e de carga (4.3). Os nomes das views Flask (`api_register`, `api_triagem_nova`...) seguem o caminho da rota e já são consistentes entre si.

## Funções duplicadas
- Python: as funções com o mesmo nome em `storage_json.py` e `storage_supabase.py` são as duas implementações da mesma interface (escolhidas por `COE_STORAGE`), não duplicação. Nenhuma função repetida dentro do mesmo módulo.
- JavaScript: `getJSON`, `postJSON` e `mascaraTelefone` existem em `Web/js/web-app.js` e no Mobile (`api.js`, `TriageScreen.js`). São plataformas separadas, sem código compartilhado entre elas, então não dá para unificar sem criar uma camada nova (fora do escopo).
- Nenhuma função duplicada dentro do mesmo arquivo.

## Build final do Mobile (Expo)
- `npm ci` em `Mobile/`: concluiu sem erro (só avisos de pacotes antigos de terceiros, sem impacto).
- `npx expo export --platform android`: **concluiu com sucesso**, 787 módulos empacotados, bundle Android gerado, sem erros nem avisos do código do projeto.
