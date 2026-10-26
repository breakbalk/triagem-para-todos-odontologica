-- Desfaz rls_policies.sql (Card 2.1): remove as políticas e devolve os privilégios padrão do Supabase.
-- O RLS continua LIGADO (como no schema.sql original).

begin;

drop policy if exists usuarios_select_proprio  on public.usuarios;
drop policy if exists triagens_select_proprias on public.triagens;
drop policy if exists triagens_insert_proprias on public.triagens;

grant all on public.usuarios, public.triagens, public.password_reset, public.mobile_token to anon, authenticated;

commit;
