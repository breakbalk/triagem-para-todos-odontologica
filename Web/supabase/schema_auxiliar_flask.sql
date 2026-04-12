-- Use este script quando usuarios e triagens JÁ EXISTIREM no Supabase (vazias ou não).
-- Ele só cria o que o backend Flask precisa além do MER: reset de senha e token mobile.
-- Rode uma vez no SQL Editor.

create extension if not exists "pgcrypto";

-- Recuperação de senha (RF03 demo)
create table if not exists public.password_reset (
  email text primary key,
  token text not null
);

-- Token Bearer para o app mobile (mesmo usuario_id de public.usuarios)
create table if not exists public.mobile_token (
  token text primary key,
  usuario_id uuid not null references public.usuarios (id_usuario) on delete cascade
);

alter table public.password_reset enable row level security;
alter table public.mobile_token enable row level security;

-- Com SUPABASE_KEY = service_role no Flask, o acesso continua funcionando com RLS ligado.
