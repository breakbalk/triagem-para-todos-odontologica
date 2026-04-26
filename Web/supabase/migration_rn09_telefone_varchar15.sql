-- RN09 — telefone mascarado (ex.: (62) 99999-9999) cabe em 15 caracteres.
-- Rode no SQL Editor do Supabase se a tabela usuarios já existir com telefone sem limite ou muito curto.

alter table public.usuarios
  alter column telefone type varchar(15)
  using (
    case
      when telefone is null then null
      else left(trim(telefone::text), 15)
    end
  );
