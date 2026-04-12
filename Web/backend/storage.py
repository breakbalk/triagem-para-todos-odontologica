# -*- coding: utf-8 -*-
"""
Guarda usuários e triagens em um arquivo JSON (Web/data/app_storage.json).

Não usa Supabase de propósito ainda: outra pessoa do grupo pode trocar este arquivo
por consultas ao banco depois. A ideia é só ler/gravar um dicionário Python e salvar em JSON — bem direto.

Estrutura do arquivo:
- users: dicionário id (string) -> dados do usuário
- users_by_email: e-mail -> id (para achar rápido no login)
- triagens: lista de triagens
- next_user_id / next_triagem_id: contadores para gerar IDs novos
"""

import json
import os
import random
from datetime import datetime

# Pasta Web/ (um nível acima de backend/)
_WEB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_WEB_DIR, "data")
_ARQUIVO = os.path.join(_DATA_DIR, "app_storage.json")

# Tudo fica nesta variável global depois do load()
dados = {}


def _pasta_data():
    """Cria Web/data se não existir."""
    if not os.path.isdir(_DATA_DIR):
        os.makedirs(_DATA_DIR)


def _estado_vazio():
    """Começo quando não tem arquivo ainda."""
    return {
        "users": {},
        "users_by_email": {},
        "triagens": [],
        "password_reset": {},
        # token (string) -> id do usuário — usado pelo app mobile (cookie de sessão não funciona bem no RN)
        "mobile_tokens": {},
        "next_user_id": 1,
        "next_triagem_id": 1,
    }


def _salvar():
    """Grava o dicionário `dados` no arquivo JSON."""
    _pasta_data()
    f = open(_ARQUIVO, "w", encoding="utf-8")
    json.dump(dados, f, ensure_ascii=False, indent=2)
    f.close()


def _criar_admin_padrao():
    """
    Se não tiver ninguém cadastrado, cria um administrador para testar.
    Senha padrão: Admin@coe2026 (pode mudar com variável de ambiente).
    """
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
    """
    Chama isso uma vez quando o servidor Flask liga.
    Lê o JSON do disco (ou começa vazio e cria o admin).
    """
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

    # Garante chaves que talvez faltem num arquivo antigo
    for chave, padrao in _estado_vazio().items():
        if chave not in dados:
            dados[chave] = padrao

    if len(dados["users"]) == 0:
        _criar_admin_padrao()
        _salvar()


def buscar_usuario_por_email(email):
    """Devolve o dict do usuário ou None."""
    email = email.strip().lower()
    uid = dados["users_by_email"].get(email)
    if uid is None:
        return None
    return dados["users"].get(uid)


def buscar_usuario_por_id(user_id):
    uid = str(int(user_id))
    return dados["users"].get(uid)


def criar_usuario(nome, email, password_hash, telefone=""):
    """Cadastro (RF01). Se e-mail já existe, levanta ValueError."""
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
    """Usado na recuperação de senha (RF03)."""
    email = email.strip().lower()
    uid = dados["users_by_email"].get(email)
    if uid is None:
        raise ValueError("Usuário não encontrado.")
    dados["users"][uid]["password_hash"] = password_hash
    _salvar()


def criar_triagem(user_id, nome, telefone, servico, periodo, sintomas=""):
    """Salva uma triagem e devolve o registro (com protocolo)."""
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


def listar_triagens_do_usuario(user_id):
    """Só as triagens desse usuário (paciente)."""
    uid = int(user_id)
    lista = []
    for t in dados["triagens"]:
        if t["user_id"] == uid:
            lista.append(t)
    return lista


def listar_todas_triagens():
    """Painel da equipe: todas as triagens."""
    # Devolve cópia da lista para não mexer no original por engano
    return list(dados["triagens"])


def salvar_token_reset(email):
    """Gera token de recuperação (em produção iria por e-mail)."""
    email = email.strip().lower()
    # Número grande só para teste (e-mail mandaria um link com isso)
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
    """Gera um token e grava no JSON. O app envia depois no header Authorization: Bearer ..."""
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
