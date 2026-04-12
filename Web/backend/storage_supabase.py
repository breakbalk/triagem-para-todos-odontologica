# -*- coding: utf-8 -*-
"""
Persistência no Supabase conforme MER da equipe:

- public.usuarios (id_usuario uuid, nome, email, senha, telefone, data_criacao)
- public.triagens (id_triagem uuid, usuario_id, servico, periodo, solicitacao_dados, data_triagem)

Campos extras do app (nome/telefone na triagem, sintomas, status, protocolo) ficam em
solicitacao_dados como JSON. Tabelas password_reset e mobile_token são auxiliares (ver Web/supabase/schema.sql).

Admin: não há coluna is_admin; quem coincide com COE_ADMIN_EMAIL é tratado como admin no retorno da API.
"""

import json
import os
import random
from datetime import datetime

_sb_client = None


def _sb():
    global _sb_client
    if _sb_client is None:
        from supabase import create_client

        url = os.environ.get("SUPABASE_URL", "").strip()
        key = os.environ.get("SUPABASE_KEY", "").strip()
        if not url or not key:
            raise RuntimeError(
                "COE_STORAGE=supabase exige SUPABASE_URL e SUPABASE_KEY no Web/backend/.env — veja .env.example."
            )
        _sb_client = create_client(url, key)
    return _sb_client


def _admin_email_padrao():
    return os.environ.get("COE_ADMIN_EMAIL", "admin@coe.unievangelica.edu.br").lower().strip()


def _row_user(row):
    if not row:
        return None
    email = (row.get("email") or "").strip()
    email_l = email.lower()
    return {
        "id": str(row["id_usuario"]),
        "nome": row["nome"],
        "email": email,
        "password_hash": row["senha"],
        "telefone": row.get("telefone") or "",
        "is_admin": email_l == _admin_email_padrao(),
    }


def _extras_solicitacao(raw):
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return {}
    s = str(raw).strip()
    if s.startswith("{"):
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            return {"sintomas": s}
    return {"sintomas": s}


def _row_triagem(row):
    if not row:
        return None
    ex = _extras_solicitacao(row.get("solicitacao_dados"))
    tid = str(row["id_triagem"])
    uid = str(row["usuario_id"])
    ds = row.get("data_triagem")
    if ds is None:
        ds_str = ""
    elif hasattr(ds, "isoformat"):
        ds_str = ds.isoformat()
    else:
        ds_str = str(ds)
    protocolo = ex.get("protocolo") or ("TRG-%s-%s" % (datetime.now().year, tid.replace("-", "")[:8]))
    return {
        "id": tid,
        "user_id": uid,
        "nome": ex.get("nome", ""),
        "telefone": ex.get("telefone", ""),
        "servico": row["servico"],
        "periodo": row["periodo"],
        "sintomas": ex.get("sintomas", ""),
        "status": ex.get("status", "Pendente"),
        "data_solicitacao": ds_str,
        "protocolo": protocolo,
    }


def _criar_admin_padrao():
    from werkzeug.security import generate_password_hash

    r = _sb().table("usuarios").select("id_usuario").limit(1).execute()
    if r.data and len(r.data) > 0:
        return

    email = _admin_email_padrao()
    senha = os.environ.get("COE_ADMIN_PASSWORD", "Admin@coe2026")
    h = generate_password_hash(senha)
    tel = ""
    _sb().table("usuarios").insert(
        {
            "nome": "Administrador COE",
            "email": email,
            "senha": h,
            "telefone": tel,
        }
    ).execute()


def init_storage():
    _sb()
    _criar_admin_padrao()


def buscar_usuario_por_email(email):
    email = email.strip().lower()
    r = _sb().table("usuarios").select("*").eq("email", email).limit(1).execute()
    if not r.data:
        return None
    return _row_user(r.data[0])


def buscar_usuario_por_id(user_id):
    uid = str(user_id).strip()
    r = _sb().table("usuarios").select("*").eq("id_usuario", uid).limit(1).execute()
    if not r.data:
        return None
    return _row_user(r.data[0])


def criar_usuario(nome, email, password_hash, telefone=""):
    email = email.strip().lower()
    tel = (telefone or "").strip() or None
    try:
        ins = (
            _sb()
            .table("usuarios")
            .insert(
                {
                    "nome": nome.strip(),
                    "email": email,
                    "senha": password_hash,
                    "telefone": tel,
                }
            )
            .execute()
        )
    except Exception as e:
        msg = str(e).lower()
        if "duplicate" in msg or "unique" in msg or "23505" in msg:
            raise ValueError("E-mail já cadastrado.") from e
        raise
    if not ins.data:
        raise ValueError("E-mail já cadastrado.")
    return _row_user(ins.data[0])


def atualizar_senha_por_email(email, password_hash):
    email = email.strip().lower()
    r = (
        _sb()
        .table("usuarios")
        .update({"senha": password_hash})
        .eq("email", email)
        .execute()
    )
    if not r.data:
        raise ValueError("Usuário não encontrado.")


def criar_triagem(user_id, nome, telefone, servico, periodo, sintomas=""):
    uid_str = str(user_id).strip()
    agora = datetime.now()
    extra = {
        "nome": nome.strip(),
        "telefone": telefone.strip(),
        "sintomas": (sintomas or "").strip(),
        "status": "Pendente",
        "protocolo": "__TEMP__",
    }
    ins = (
        _sb()
        .table("triagens")
        .insert(
            {
                "usuario_id": uid_str,
                "servico": servico,
                "periodo": periodo,
                "solicitacao_dados": json.dumps(extra),
                "data_triagem": agora.isoformat(),
            }
        )
        .execute()
    )
    if not ins.data:
        raise RuntimeError("Não foi possível criar a triagem.")
    id_t = str(ins.data[0]["id_triagem"])
    extra["protocolo"] = "TRG-%s-%s" % (agora.year, id_t.replace("-", "")[:8])
    _sb().table("triagens").update({"solicitacao_dados": json.dumps(extra)}).eq("id_triagem", id_t).execute()
    return {
        "id": id_t,
        "user_id": uid_str,
        "nome": extra["nome"],
        "telefone": extra["telefone"],
        "servico": servico,
        "periodo": periodo,
        "sintomas": extra["sintomas"],
        "status": extra["status"],
        "data_solicitacao": agora.isoformat(),
        "protocolo": extra["protocolo"],
    }


def listar_triagens_do_usuario(user_id):
    uid = str(user_id).strip()
    r = (
        _sb()
        .table("triagens")
        .select("*")
        .eq("usuario_id", uid)
        .order("id_triagem", desc=True)
        .execute()
    )
    return [_row_triagem(row) for row in (r.data or [])]


def listar_todas_triagens():
    r = _sb().table("triagens").select("*").order("id_triagem", desc=True).execute()
    return [_row_triagem(row) for row in (r.data or [])]


def salvar_token_reset(email):
    email = email.strip().lower()
    token = str(random.randint(10000000, 99999999))
    _sb().table("password_reset").delete().eq("email", email).execute()
    _sb().table("password_reset").insert({"email": email, "token": token}).execute()
    return token


def pegar_token_reset(email):
    email = email.strip().lower()
    r = _sb().table("password_reset").select("token").eq("email", email).limit(1).execute()
    if not r.data:
        return None
    return r.data[0]["token"]


def limpar_token_reset(email):
    email = email.strip().lower()
    _sb().table("password_reset").delete().eq("email", email).execute()


def criar_token_mobile(user_id):
    token = str(random.randint(10**15, 10**16 - 1))
    uid = str(user_id).strip()
    _sb().table("mobile_token").insert({"token": token, "usuario_id": uid}).execute()
    return token


def user_id_do_token_mobile(token):
    if not token:
        return None
    r = _sb().table("mobile_token").select("usuario_id").eq("token", token).limit(1).execute()
    if not r.data:
        return None
    return str(r.data[0]["usuario_id"])


def apagar_token_mobile(token):
    if not token:
        return
    _sb().table("mobile_token").delete().eq("token", token).execute()
