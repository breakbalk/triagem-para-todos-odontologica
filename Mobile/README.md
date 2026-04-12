# App mobile — COE (Sprint 1)

React Native com **Expo**. Esta sprint entrega:

- Ambiente Expo + navegação entre telas  
- **Login**, **cadastro**, **recuperação de senha** (RF01–RF03)  
- Tela **Home** após autenticar (Sprint 2: triagem)

## Antes de rodar o app

Use **dois terminais** ao mesmo tempo (não pare o Flask para rodar o Expo):

| Terminal 1 | Terminal 2 |
|------------|--------------|
| `Web/backend` → `python app.py` | `Mobile` → `npx expo start` |

1. Suba o Flask e anote a linha **`Running on http://192.168.x.x:5000`** (esse é o IP do PC na Wi‑Fi).

2. No celular físico, abra `src/config.js` e coloque esse IP em **`IP_DO_PC`** (ex.: `"192.168.0.232"`).  
   Isso evita erro quando o Expo mostra outro IP no QR (ex.: `26.x.x.x`).

3. **Emulador Android:** deixe `IP_DO_PC` vazio; o app usa `10.0.2.2`.

4. PC e celular na **mesma rede Wi‑Fi**; firewall do Windows pode pedir para liberar o Python.

## Instalar e abrir

```bash
cd Mobile
npm install
npx expo start
```

Depois pressione `a` para Android (emulador ou USB) ou escaneie o QR no app **Expo Go**.

## Login de teste (mesmo do site)

- E-mail: `admin@coe.unievangelica.edu.br`  
- Senha: `Admin@coe2026`

## Como o mobile autentica

O site usa **cookie** de sessão. No celular, o backend devolve também um **`mobile_token`** no JSON do login/cadastro. O app guarda no `AsyncStorage` e manda no header `Authorization: Bearer ...`.

## Estrutura (simples)

| Arquivo / pasta | Função |
|------------------|--------|
| `App.js` | Navegação e “abrir já logado” se tiver token |
| `src/config.js` | URL do servidor |
| `src/services/api.js` | Chamadas HTTP + token |
| `src/screens/*` | Telas |
| `src/components/*` | Campo e botão reutilizáveis |

Documentação geral: [`../docs/PLANEJAMENTO-MOBILE.md`](../docs/PLANEJAMENTO-MOBILE.md)
