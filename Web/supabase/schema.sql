-- Schema alinhado ao MER da equipe (usuarios + triagens em UUID).
-- Rode no SQL Editor do Supabase. Inclui tabelas auxiliares para reset de senha e token mobile.

create extension if not exists "pgcrypto";

-- === MER equipe ===
create table if not exists public.usuarios (
  id_usuario uuid primary key default gen_random_uuid(),
  nome varchar not null,
  email varchar not null unique,
  senha text not null,
  telefone varchar(15),
  data_criacao timestamptz default now()
);

create table if not exists public.triagens (
  id_triagem uuid primary key default gen_random_uuid(),
  usuario_id uuid not null references public.usuarios (id_usuario) on delete cascade,
  servico varchar not null,
  periodo varchar not null,
  solicitacao_dados text,
  data_triagem timestamptz default now()
);

create index if not exists idx_triagens_usuario_id on public.triagens (usuario_id);

-- === Auxiliares (não estavam no diagrama; usadas pelo Flask) ===
create table if not exists public.password_reset (
  email text primary key,
  token text not null
);

create table if not exists public.mobile_token (
  token text primary key,
  usuario_id uuid not null references public.usuarios (id_usuario) on delete cascade
);

-- RLS: com service_role no backend, o acesso do Flask segue funcionando.
alter table public.usuarios enable row level security;
alter table public.triagens enable row level security;
alter table public.password_reset enable row level security;
alter table public.mobile_token enable row level security;
