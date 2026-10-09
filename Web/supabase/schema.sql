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
  -- CPF opcional (o app mobile não pede): só os 11 números, sem repetir.
  cpf text constraint usuarios_cpf_key unique
           constraint usuarios_cpf_formato check (cpf ~ '^[0-9]{11}$'),
  data_criacao timestamptz default now()
);

-- Banco criado antes do CPF (o do projeto recebeu isto em 09/10/2026, migração add_cpf_usuarios):
-- alter table public.usuarios add column cpf text;
-- alter table public.usuarios add constraint usuarios_cpf_formato check (cpf ~ '^[0-9]{11}$');
-- alter table public.usuarios add constraint usuarios_cpf_key unique (cpf);

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
