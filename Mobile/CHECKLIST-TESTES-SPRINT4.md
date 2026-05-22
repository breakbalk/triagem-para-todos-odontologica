# Checklist manual — Sprint 4 (mobile)

Marque após subir backend + Expo (`npm run start` / `start:lan`).

- [ ] Boot: splash “Carregando aplicativo…”
- [ ] Login: e-mail/senha vazios → alerta; credenciais inválidas → mensagem clara
- [ ] Cadastro: validações; alerta “Conta criada” → Home
- [ ] Home: pull-to-refresh atualiza lista
- [ ] Home: banner verde após sync / laranja se pendente / azul se cache
- [ ] Nova triagem online → confirmação com protocolo servidor + banner verde
- [ ] Nova triagem offline → protocolo LOCAL + banner laranja na confirmação
- [ ] Voltar online → Home mostra sincronização e protocolo TRG na lista
- [ ] Sair: confirmação antes de logout
- [ ] Recuperar senha: passos 1 e 2 com textos legíveis
