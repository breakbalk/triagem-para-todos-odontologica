-- ==========================================
-- SCRIPT DE ROLLBACK - CARD 3.6
-- ==========================================
BEGIN;

-- 1. Remover o indice unico criado
DROP INDEX IF EXISTS public.idx_triagem_protocolo;

-- 2. Remover a coluna protocolo da tabela
ALTER TABLE public.triagens
  DROP COLUMN IF EXISTS protocolo;

COMMIT;
