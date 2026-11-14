# -*- coding: utf-8 -*-
"""
Persistência no Supabase conforme MER da equipe:

- public.usuarios (id_usuario uuid, nome, email, senha, telefone, cpf, data_criacao)
- public.triagens (id_triagem uuid, usuario_id, servico, periodo, solicitacao_dados, data_triagem)

Campos extras do app (nome/telefone na triagem, sintomas, status, protocolo) ficam em
solicitacao_dados como JSON. Tabelas password_reset e mobile_token são auxiliares (ver Web/supabase/schema.sql).

Admin: não há coluna is_admin; quem coincide com COE_ADMIN_EMAIL é tratado como admin no retorno da API.
"""

import json
import os
import random
import threading
import time
import uuid
from datetime import datetime

import httpx

_local = threading.local()

# Erro de rede em que a conexão HTTP/2 reaproveitada já tinha sido fechada pelo servidor.
_ERROS_REDE = (httpx.RemoteProtocolError,)
_TENTATIVAS = 3
_ESPERA_S = 0.05


def _sb():
    """Cliente Supabase da thread atual: cada thread do Flask tem o seu (sem compartilhar a conexão HTTP/2)."""
    cli = getattr(_local, "cliente", None)
    if cli is None:
        from supabase import create_client

        url = os.environ.get("SUPABASE_URL", "").strip()
        key = os.environ.get("SUPABASE_KEY", "").strip()
        if not url or not key:
            raise RuntimeError(
                "COE_STORAGE=supabase exige SUPABASE_URL e SUPABASE_KEY no Web/backend/.env — veja .env.example."
            )
        cli = _local.cliente = create_client(url, key)
    return cli


def _descartar_cliente():
    _local.cliente = None


def _com_retry(executar, tentativas=_TENTATIVAS):
    """Repete a chamada se a conexão foi derrubada (httpx.RemoteProtocolError), com um cliente novo a cada vez."""
    for i in range(tentativas):
        try:
            return executar()
        except _ERROS_REDE:
            if i == tentativas - 1:
                raise
            _descartar_cliente()
            time.sleep(_ESPERA_S * (i + 1))


class _Consulta:
    """Encapsula a cadeia table().select()...: o execute() repete em erro de conexão.

    INSERT não repete sozinho (repetir pode duplicar a linha); use execute_com_retry() quando o insert for idempotente.
    """

    def __init__(self, nome, passos=()):
        self._nome = nome
        self._passos = passos
        self._insert = any(n == "insert" for n, _, _ in passos)

    def _montar(self):
        q = _sb().table(self._nome)
        for n, a, k in self._passos:
            q = getattr(q, n)(*a, **k)
        return q

    def __getattr__(self, n):
        if n.startswith("_"):
            raise AttributeError(n)
        return lambda *a, **k: _Consulta(self._nome, self._passos + ((n, a, k),))

    def execute(self):
        return _com_retry(lambda: self._montar().execute(), 1 if self._insert else _TENTATIVAS)

    def execute_com_retry(self):
        return _com_retry(lambda: self._montar().execute())


def _tabela(nome):
    return _Consulta(nome)


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

    r = _tabela("usuarios").select("id_usuario").limit(1).execute()
    if r.data and len(r.data) > 0:
        return

    email = _admin_email_padrao()
    senha = os.environ.get("COE_ADMIN_PASSWORD", "Admin@coe2026")
    h = generate_password_hash(senha)
    tel = ""
    _tabela("usuarios").insert(
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
    r = _tabela("usuarios").select("*").eq("email", email).limit(1).execute()
    if not r.data:
        return None
    return _row_user(r.data[0])


def buscar_usuario_por_id(user_id):
    uid = str(user_id).strip()
    r = _tabela("usuarios").select("*").eq("id_usuario", uid).limit(1).execute()
    if not r.data:
        return None
    return _row_user(r.data[0])


def criar_usuario(nome, email, password_hash, telefone="", cpf=None):
    email = email.strip().lower()
    tel = (telefone or "").strip() or None
    cpf_limpo = (cpf or "").strip() or None
    try:
        ins = (
            _tabela("usuarios")
            .insert(
                {
                    "nome": nome.strip(),
                    "email": email,
                    "senha": password_hash,
                    "telefone": tel,
                    "cpf": cpf or None,
                }
            )
            .execute()
        )
    except Exception as e:
        msg = str(e).lower()
        if "usuarios_cpf_key" in msg:
            raise ValueError("CPF já cadastrado.") from e
        if "duplicate" in msg or "unique" in msg or "23505" in msg:
            raise ValueError("E-mail ou CPF já cadastrado.") from e
        raise
    if not ins.data:
        raise ValueError("E-mail ou CPF já cadastrado.")
    return _row_user(ins.data[0])


def atualizar_senha_por_email(email, password_hash):
    email = email.strip().lower()
    r = (
        _tabela("usuarios")
        .update({"senha": password_hash})
        .eq("email", email)
        .execute()
    )
    if not r.data:
        raise ValueError("Usuário não encontrado.")


def _protocolo_para(id_triagem, ano):
    """Protocolo TRG-AAAA-xxxxxxxx derivado do UUID (mesmo formato dos registros existentes)."""
    return "TRG-%s-%s" % (ano, str(id_triagem).replace("-", "")[:8])


def criar_triagem(user_id, nome, telefone, servico, periodo, sintomas=""):
    uid_str = str(user_id).strip()
    extra = {
        "nome": nome.strip(),
        "telefone": telefone.strip(),
        "sintomas": (sintomas or "").strip(),
        "status": "Pendente",
    }
    ano_proto = datetime.now().year
    ins = None
    # A coluna protocolo é NOT NULL + UNIQUE (Card 3.6): o UUID e o protocolo são gerados
    # ANTES do insert. Em colisão do índice único (8 hex do UUID), gera novo UUID e tenta de novo.
    for _tentativa in range(5):
        id_t = str(uuid.uuid4())
        extra["protocolo"] = _protocolo_para(id_t, ano_proto)
        try:
            ins = (
                _tabela("triagens")
                .insert(
                    {
                        "id_triagem": id_t,
                        "usuario_id": uid_str,
                        "servico": servico,
                        "periodo": periodo,
                        "solicitacao_dados": json.dumps(extra),
                        "protocolo": extra["protocolo"],
                    }
                )
                .execute()
            )
            break
        except Exception as exc:
            msg = str(exc)
            if "23505" in msg or "duplicate key" in msg.lower():
                continue
            raise
    if ins is None or not ins.data:
        raise RuntimeError("Não foi possível criar a triagem.")
    row = ins.data[0]
    id_t = str(row["id_triagem"])
    data_triagem_db = row.get("data_triagem")
    if hasattr(data_triagem_db, "isoformat"):
        data_solicitacao = data_triagem_db.isoformat()
    elif data_triagem_db is None:
        data_solicitacao = datetime.now().isoformat()
    else:
        data_solicitacao = str(data_triagem_db)
    return {
        "id": id_t,
        "user_id": uid_str,
        "nome": extra["nome"],
        "telefone": extra["telefone"],
        "servico": servico,
        "periodo": periodo,
        "sintomas": extra["sintomas"],
        "status": extra["status"],
        "data_solicitacao": data_solicitacao,
        "protocolo": extra["protocolo"],
    }


def insert_triagem(user_id, nome, telefone, servico, periodo, sintomas=""):
    """Alias explícito para documentação (INSERT de triagem)."""
    return criar_triagem(user_id, nome, telefone, servico, periodo, sintomas)


def listar_triagens_do_usuario(user_id):
    uid = str(user_id).strip()
    r = (
        _tabela("triagens")
        .select("*")
        .eq("usuario_id", uid)
        .order("id_triagem", desc=True)
        .execute()
    )
    return [_row_triagem(row) for row in (r.data or [])]


def listar_todas_triagens():
    r = _tabela("triagens").select("*").order("id_triagem", desc=True).execute()
    return [_row_triagem(row) for row in (r.data or [])]


def atualizar_status_triagem(protocolo, novo_status):
    protocolo = (protocolo or "").strip()
    if not protocolo:
        return False
    r = _tabela("triagens").select("*").order("id_triagem", desc=True).execute()
    for row in (r.data or []):
        ex = _extras_solicitacao(row.get("solicitacao_dados"))
        if str(ex.get("protocolo", "")).strip() != protocolo:
            continue
        ex["status"] = (novo_status or "").strip() or "Pendente"
        _tabela("triagens").update({"solicitacao_dados": json.dumps(ex)}).eq("id_triagem", row["id_triagem"]).execute()
        return True
    return False


def salvar_token_reset(email):
    email = email.strip().lower()
    token = str(random.randint(10000000, 99999999))
    _tabela("password_reset").delete().eq("email", email).execute()
    _tabela("password_reset").insert({"email": email, "token": token}).execute()
    return token


def pegar_token_reset(email):
    email = email.strip().lower()
    r = _tabela("password_reset").select("token").eq("email", email).limit(1).execute()
    if not r.data:
        return None
    return r.data[0]["token"]


def limpar_token_reset(email):
    email = email.strip().lower()
    _tabela("password_reset").delete().eq("email", email).execute()


def criar_token_mobile(user_id):
    token = str(random.randint(10**15, 10**16 - 1))
    uid = str(user_id).strip()
    _tabela("mobile_token").insert({"token": token, "usuario_id": uid}).execute()
    return token


def user_id_do_token_mobile(token):
    if not token:
        return None
    r = _tabela("mobile_token").select("usuario_id").eq("token", token).limit(1).execute()
    if not r.data:
        return None
    return str(r.data[0]["usuario_id"])


def apagar_token_mobile(token):
    if not token:
        return
    _tabela("mobile_token").delete().eq("token", token).execute()
