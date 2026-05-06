# -*- coding: utf-8 -*-
"""
Persistência em arquivo JSON (Web/data/app_storage.json).
Usado quando COE_STORAGE não é supabase.
"""

import json
import os
import random
from datetime import datetime

_WEB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_WEB_DIR, "data")
_ARQUIVO = os.path.join(_DATA_DIR, "app_storage.json")

dados = {}


def _pasta_data():
    if not os.path.isdir(_DATA_DIR):
        os.makedirs(_DATA_DIR)


def _estado_vazio():
    return {
        "users": {},
        "users_by_email": {},
        "triagens": [],
        "password_reset": {},
        "mobile_tokens": {},
        "next_user_id": 1,
        "next_triagem_id": 1,
    }


def _salvar():
    _pasta_data()
    f = open(_ARQUIVO, "w", encoding="utf-8")
    json.dump(dados, f, ensure_ascii=False, indent=2)
    f.close()


def _criar_admin_padrao():
    from werkzeug.security import generate_password_hash

    if len(dados["users"]) > 0:
        return

    email = os.environ.get("COE_ADMIN_EMAIL", "admin@coe.unievangelica.edu.br")
    email = email.lower().strip()
    senha = os.environ.get("COE_ADMIN_PASSWORD", "Admin@coe2026")

    uid = str(dados["next_user_id"])
    dados["users"][uid] = {
        "id": int(uid),
        "nome": "Administrador COE",
        "email": email,
        "password_hash": generate_password_hash(senha),
        "telefone": "",
        "is_admin": True,
    }
    dados["users_by_email"][email] = uid
    dados["next_user_id"] = int(uid) + 1


def init_storage():
    global dados
    _pasta_data()

    if not os.path.isfile(_ARQUIVO):
        dados = _estado_vazio()
        _criar_admin_padrao()
        _salvar()
        return

    f = open(_ARQUIVO, "r", encoding="utf-8")
    dados = json.load(f)
    f.close()

    for chave, padrao in _estado_vazio().items():
        if chave not in dados:
            dados[chave] = padrao

    if len(dados["users"]) == 0:
        _criar_admin_padrao()
        _salvar()


def buscar_usuario_por_email(email):
    email = email.strip().lower()
    uid = dados["users_by_email"].get(email)
    if uid is None:
        return None
    return dados["users"].get(uid)


def buscar_usuario_por_id(user_id):
    uid = str(int(user_id))
    return dados["users"].get(uid)


def criar_usuario(nome, email, password_hash, telefone=""):
    email = email.strip().lower()
    if email in dados["users_by_email"]:
        raise ValueError("E-mail já cadastrado.")

    uid = str(dados["next_user_id"])
    registro = {
        "id": int(uid),
        "nome": nome.strip(),
        "email": email,
        "password_hash": password_hash,
        "telefone": (telefone or "").strip(),
        "is_admin": False,
    }
    dados["users"][uid] = registro
    dados["users_by_email"][email] = uid
    dados["next_user_id"] = int(uid) + 1
    _salvar()
    return registro


def atualizar_senha_por_email(email, password_hash):
    email = email.strip().lower()
    uid = dados["users_by_email"].get(email)
    if uid is None:
        raise ValueError("Usuário não encontrado.")
    dados["users"][uid]["password_hash"] = password_hash
    _salvar()


def criar_triagem(user_id, nome, telefone, servico, periodo, sintomas=""):
    tid = int(dados["next_triagem_id"])
    ano = datetime.now().year
    protocolo = "TRG-%s-%06d" % (ano, tid)
    agora = datetime.now().isoformat()

    registro = {
        "id": tid,
        "user_id": int(user_id),
        "nome": nome.strip(),
        "telefone": telefone.strip(),
        "servico": servico,
        "periodo": periodo,
        "sintomas": (sintomas or "").strip(),
        "status": "Pendente",
        "data_solicitacao": agora,
        "protocolo": protocolo,
    }
    dados["triagens"].append(registro)
    dados["next_triagem_id"] = tid + 1
    _salvar()
    return registro


def insert_triagem(user_id, nome, telefone, servico, periodo, sintomas=""):
    """Alias explícito para documentação (INSERT de triagem)."""
    return criar_triagem(user_id, nome, telefone, servico, periodo, sintomas)


def listar_triagens_do_usuario(user_id):
    uid = int(user_id)
    lista = []
    for t in dados["triagens"]:
        if t["user_id"] == uid:
            lista.append(t)
    return lista


def listar_todas_triagens():
    return list(dados["triagens"])


def atualizar_status_triagem(protocolo, novo_status):
    protocolo = (protocolo or "").strip()
    if not protocolo:
        return False
    for t in dados["triagens"]:
        if str(t.get("protocolo", "")).strip() == protocolo:
            t["status"] = (novo_status or "").strip() or "Pendente"
            _salvar()
            return True
    return False


def salvar_token_reset(email):
    email = email.strip().lower()
    token = str(random.randint(10000000, 99999999))
    dados["password_reset"][email] = {"token": token}
    _salvar()
    return token


def pegar_token_reset(email):
    email = email.strip().lower()
    info = dados["password_reset"].get(email)
    if info is None:
        return None
    return info["token"]


def limpar_token_reset(email):
    email = email.strip().lower()
    if email in dados["password_reset"]:
        del dados["password_reset"][email]
        _salvar()


def criar_token_mobile(user_id):
    token = str(random.randint(10 ** 15, 10 ** 16 - 1))
    dados["mobile_tokens"][token] = int(user_id)
    _salvar()
    return token


def user_id_do_token_mobile(token):
    if not token:
        return None
    uid = dados["mobile_tokens"].get(token)
    return uid


def apagar_token_mobile(token):
    if token and token in dados["mobile_tokens"]:
        del dados["mobile_tokens"][token]
        _salvar()
