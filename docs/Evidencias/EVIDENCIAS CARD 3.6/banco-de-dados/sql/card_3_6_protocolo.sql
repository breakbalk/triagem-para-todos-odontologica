-- =====================================================================
-- CARD 3.6 - Coluna protocolo + backfill + UNIQUE INDEX (public.triagens)
-- JA APLICADO no projeto Supabase "Triagem para Todos" (migracao
-- card_3_6_triagens_protocolo_unique). Versao adaptada ao esquema real:
--   PK: id_triagem (uuid) | data: data_triagem | JSON em texto: solicitacao_dados
-- =====================================================================

-- 1) Coluna (nullable para o backfill)
ALTER TABLE public.triagens ADD COLUMN IF NOT EXISTS protocolo VARCHAR(50);

-- 2) Backfill: protocolo existente no JSON; senao gera TRG-YYYY-<8 primeiros chars do UUID>
UPDATE public.triagens
SET protocolo = COALESCE(
      CASE WHEN pg_input_is_valid(solicitacao_dados, 'jsonb')
           THEN NULLIF(BTRIM(solicitacao_dados::jsonb->>'protocolo'), '') END,
      CONCAT('TRG-', TO_CHAR(data_triagem, 'YYYY'), '-', LEFT(id_triagem::text, 8))
    )
WHERE protocolo IS NULL;

-- 2.1) Colisoes: a partir da 2a ocorrencia acrescenta os 4 ultimos caracteres do UUID
WITH dup AS (
  SELECT id_triagem,
         ROW_NUMBER() OVER (PARTITION BY protocolo ORDER BY data_triagem, id_triagem) AS rn
  FROM public.triagens
)
UPDATE public.triagens t
SET protocolo = LEFT(t.protocolo, 45) || '-' || RIGHT(t.id_triagem::text, 4)
FROM dup
WHERE t.id_triagem = dup.id_triagem AND dup.rn > 1;

-- 2.2) Trava: aborta tudo se sobrar NULL ou duplicata
DO $$
DECLARE qtd_null integer; qtd_dup integer;
BEGIN
  SELECT COUNT(*) INTO qtd_null FROM public.triagens WHERE protocolo IS NULL;
  SELECT COUNT(*) INTO qtd_dup FROM (SELECT protocolo FROM public.triagens GROUP BY protocolo HAVING COUNT(*) > 1) d;
  IF qtd_null > 0 OR qtd_dup > 0 THEN
    RAISE EXCEPTION 'Backfill incompleto: % NULL, % duplicados', qtd_null, qtd_dup;
  END IF;
END $$;

-- 3) Indice unico + NOT NULL
CREATE UNIQUE INDEX IF NOT EXISTS idx_triagem_protocolo ON public.triagens (protocolo);
ALTER TABLE public.triagens ALTER COLUMN protocolo SET NOT NULL;
