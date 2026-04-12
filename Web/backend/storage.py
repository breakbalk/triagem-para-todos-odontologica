# -*- coding: utf-8 -*-
"""
Camada de persistência do COE.

COE_STORAGE=json — arquivo Web/data/app_storage.json (padrão).
COE_STORAGE=supabase — tabelas no Supabase (veja Web/supabase/schema.sql e .env.example).
"""

import os

_mode = os.environ.get("COE_STORAGE", "json").strip().lower()

if _mode == "supabase":
    from storage_supabase import (  # noqa: E402
        apagar_token_mobile,
        atualizar_senha_por_email,
        buscar_usuario_por_email,
        buscar_usuario_por_id,
        criar_token_mobile,
        criar_triagem,
        criar_usuario,
        init_storage,
        limpar_token_reset,
        listar_todas_triagens,
        listar_triagens_do_usuario,
        pegar_token_reset,
        salvar_token_reset,
        user_id_do_token_mobile,
    )
else:
    from storage_json import (  # noqa: E402
        apagar_token_mobile,
        atualizar_senha_por_email,
        buscar_usuario_por_email,
        buscar_usuario_por_id,
        criar_token_mobile,
        criar_triagem,
        criar_usuario,
        init_storage,
        limpar_token_reset,
        listar_todas_triagens,
        listar_triagens_do_usuario,
        pegar_token_reset,
        salvar_token_reset,
        user_id_do_token_mobile,
    )
