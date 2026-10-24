-- Card 2.1 [T04/MQ04] — Auditoria de segurança: RLS em usuarios e triagens.
-- Rode no SQL Editor do Supabase. É idempotente (pode rodar de novo). Para desfazer: rls_rollback.sql.
--
-- Como o projeto funciona hoje:
--   * O Flask usa a chave SECRET (service_role) -> ela ignora o RLS, então o app continua igual.
--   * O login é do próprio Flask (sessão + mobile_token), não o Supabase Auth. Por isso auth.uid()
--     ainda não corresponde a nenhum usuarios.id_usuario: as políticas abaixo são a defesa para o dia
--     em que alguém chamar a API REST do Supabase direto (chave anon/publishable ou JWT de usuário).
--   * Resultado esperado hoje: anon e authenticated NÃO leem, não alteram e não apagam nada.

begin;

-- 1) RLS ligado nas quatro tabelas (já estava no schema.sql; reafirmado aqui).
alter table public.usuarios       enable row level security;
alter table public.triagens       enable row level security;
alter table public.password_reset enable row level security;
alter table public.mobile_token   enable row level security;

-- 2) anon (sem login): nenhum acesso. Sem privilégio, a API responde 401 "permission denied".
revoke all on public.usuarios, public.triagens, public.password_reset, public.mobile_token from anon;

-- 3) authenticated (usuário comum com JWT): só o necessário, e só nos próprios registros.
revoke all on public.usuarios, public.triagens, public.password_reset, public.mobile_token from authenticated;
-- usuarios: pode ler o próprio cadastro, SEM a coluna senha (hash). Não altera nem apaga.
grant select (id_usuario, nome, email, telefone, cpf, data_criacao) on public.usuarios to authenticated;
-- triagens: pode ver e criar as próprias. Não altera status nem apaga (isso é da fila administrativa).
grant select, insert on public.triagens to authenticated;
-- password_reset e mobile_token: nenhum acesso (só o backend, via service_role).

-- 4) Políticas (auth.uid() = dono do registro).
drop policy if exists usuarios_select_proprio on public.usuarios;
create policy usuarios_select_proprio on public.usuarios
  for select to authenticated
  using (id_usuario = (select auth.uid()));

drop policy if exists triagens_select_proprias on public.triagens;
create policy triagens_select_proprias on public.triagens
  for select to authenticated
  using (usuario_id = (select auth.uid()));

drop policy if exists triagens_insert_proprias on public.triagens;
create policy triagens_insert_proprias on public.triagens
  for insert to authenticated
  with check (usuario_id = (select auth.uid()));

-- Não há política de UPDATE/DELETE nem de "ver todas": a fila geral (admin/secretaria) só passa
-- pelo backend com a chave secret, depois da checagem de papel feita pelo Flask (401/403).

commit;

-- Conferência (somente leitura):
-- select relname, relrowsecurity from pg_class where relname in ('usuarios','triagens','password_reset','mobile_token');
-- select tablename, policyname, cmd, roles from pg_policies where schemaname = 'public' order by 1, 2;
