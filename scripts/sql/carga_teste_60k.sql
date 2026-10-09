-- Card 3.2 — massa de teste de volume (20.000 usuários, 60.000 triagens) SOMENTE no schema teste_carga.
-- Rode no SQL Editor do Supabase, bloco por bloco. Não toca em public.*.
-- Dados 100% sintéticos: e-mails @example.com, telefone com DDD 00, senha inválida (ninguém loga), sem CPF.

-- ============ 1) Schema e tabelas (mesma estrutura de public.*) ============
create schema if not exists teste_carga;

create table if not exists teste_carga.usuarios
  (like public.usuarios including defaults including constraints including indexes);
create table if not exists teste_carga.triagens
  (like public.triagens including defaults including constraints including indexes);

alter table teste_carga.triagens
  add constraint triagens_usuario_fk
  foreign key (usuario_id) references teste_carga.usuarios (id_usuario) on delete cascade;

alter table teste_carga.usuarios enable row level security;
alter table teste_carga.triagens enable row level security;

-- ============ 2) 20.000 usuários sintéticos ============
insert into teste_carga.usuarios (nome, email, senha, telefone, data_criacao)
select 'Paciente Sintetico ' || g,
       'sintetico.' || lpad(g::text, 5, '0') || '@example.com',
       md5(random()::text),  -- não é hash válido: nenhuma senha funciona
       '(00) 9' || lpad((random() * 9999)::int::text, 4, '0') || '-' || lpad((random() * 9999)::int::text, 4, '0'),
       now() - random() * interval '90 days'
from generate_series(1, 20000) g;

-- ============ 3) 60.000 triagens sintéticas ============
with ids as (select array_agg(id_usuario) as a from teste_carga.usuarios)
insert into teste_carga.triagens (usuario_id, servico, periodo, solicitacao_dados, data_triagem)
select a[1 + floor(random() * 20000)::int],
       (array['tratamento_geral', 'protese', 'pediatria', 'emergencia'])[1 + floor(random() * 4)::int],
       (array['matutino', 'vespertino', 'noturno'])[1 + floor(random() * 3)::int],
       json_build_object(
         'nome', 'Paciente Sintetico',
         'telefone', '(00) 90000-0000',
         'sintomas', 'Massa de teste de volume',
         'status', (array['Pendente', 'Em Atendimento', 'Finalizado', 'Cancelado'])[1 + floor(random() * 4)::int],
         'origem', 'massa_sintetica',
         'protocolo', 'TRG-TESTE-' || lpad(g::text, 6, '0')
       )::text,
       now() - random() * interval '90 days'
from ids, generate_series(1, 60000) g;

analyze teste_carga.usuarios;
analyze teste_carga.triagens;

-- ============ 4) Conferência (esperado: 20000 e 60000) ============
select (select count(*) from teste_carga.usuarios) as usuarios,
       (select count(*) from teste_carga.triagens) as triagens;

-- ============ 5) Teste do índice: ANTES (guarde o print) ============
explain (analyze, buffers)
select * from teste_carga.triagens
where data_triagem >= now() - interval '7 days'
order by data_triagem desc
limit 50;

-- ============ 6) Cria o índice e mede DEPOIS (guarde o print) ============
create index if not exists idx_teste_triagens_data on teste_carga.triagens (data_triagem);
analyze teste_carga.triagens;

explain (analyze, buffers)
select * from teste_carga.triagens
where data_triagem >= now() - interval '7 days'
order by data_triagem desc
limit 50;

-- ============ 7) Limpeza no fim (apaga TUDO que está em teste_carga) ============
-- drop schema teste_carga cascade;
