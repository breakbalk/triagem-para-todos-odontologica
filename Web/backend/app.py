# -*- coding: utf-8 -*-
"""
Servidor Flask do projeto COE — tudo em um arquivo para ficar fácil de ler.

Rodar (na pasta Web/backend):
    pip install -r requirements.txt
    python app.py

Abrir: http://127.0.0.1:5000/

Fluxo:
1) O navegador pede HTML/CSS/JS (arquivos na pasta Web/).
2) O JavaScript chama URLs /api/... com JSON.
3) A sessão guarda quem está logado (cookie).
"""

import os
import re
import sys

# Pasta onde está este arquivo (backend/)
_BACKEND = os.path.dirname(os.path.abspath(__file__))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from dotenv import load_dotenv

load_dotenv(os.path.join(_BACKEND, ".env"))

from flask import Flask, jsonify, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import storage

# Pasta Web/ (pai de backend/) — daqui saem pages/, css/, js/, assets/
_WEB = os.path.dirname(_BACKEND)

app = Flask(__name__, static_folder=_WEB, static_url_path="")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "troque-em-producao")

# --- listas fixas (mesmo significado do relatório do projeto) ---
SERVICOS_OK = ["tratamento_geral", "protese", "pediatria", "emergencia"]
PERIODOS_OK = ["matutino", "vespertino", "noturno"]
STATUS_TRIAGEM_OK = ["Pendente", "Em Atendimento", "Finalizado", "Cancelado"]

# RN09 — mesmo formato da máscara no front: (DD) 99999-9999 (15 caracteres).
_TELEFONE_RN09 = re.compile(r"^\(\d{2}\) \d{5}-\d{4}$")


def telefone_valido_rn09(valor):
    return bool(_TELEFONE_RN09.match((valor or "").strip()))


def nivel_acesso_do_usuario(u):
    """Níveis suportados no relatório: comum, secretaria, admin."""
    if not u:
        return "comum"
    if bool(u.get("is_admin", False)):
        return "admin"
    email = (u.get("email") or "").strip().lower()
    secre_list = os.environ.get("COE_SECRETARIA_EMAILS", "").strip()
    if secre_list:
        emails = [item.strip().lower() for item in secre_list.split(",") if item.strip()]
        if email in emails:
            return "secretaria"
    return "comum"


def destino_pos_login(u):
    return "/pages/admin.html" if nivel_acesso_do_usuario(u) in ("admin", "secretaria") else "/pages/home.html"


def usuario_publico(u):
    """Tira a senha antes de mandar JSON pro navegador."""
    if u is None:
        return None
    return {
        "id": u["id"],
        "nome": u["nome"],
        "email": u["email"],
        "telefone": u.get("telefone", ""),
        "is_admin": bool(u.get("is_admin", False)),
        "nivel_acesso": nivel_acesso_do_usuario(u),
    }


def token_bearer():
    """Lê o token do header Authorization: Bearer ... (app mobile)."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    return auth[7:].strip()


def _normaliza_id_usuario(uid):
    """IDs numéricos (JSON local) ou UUID string (Supabase)."""
    if uid is None:
        return None
    if isinstance(uid, int):
        return uid
    s = str(uid).strip()
    try:
        return int(s)
    except ValueError:
        return s


def id_usuario_logado():
    """
    Quem está logado: cookie de sessão (navegador) OU token Bearer (mobile).
    """
    uid = session.get("user_id")
    if uid is not None:
        return _normaliza_id_usuario(uid)
    tok = token_bearer()
    if tok:
        u = storage.user_id_do_token_mobile(tok)
        if u is not None:
            return _normaliza_id_usuario(u)
    return None


def usuario_eh_admin():
    """Sabe se o usuário atual é admin (funciona para web e mobile)."""
    uid = id_usuario_logado()
    if uid is None:
        return False
    u = storage.buscar_usuario_por_id(uid)
    if u is None:
        return False
    return bool(u.get("is_admin", False))


def usuario_tem_acesso_admin():
    """Permissão de gestão: admin e secretaria."""
    uid = id_usuario_logado()
    if uid is None:
        return False
    u = storage.buscar_usuario_por_id(uid)
    if u is None:
        return False
    return nivel_acesso_do_usuario(u) in ("admin", "secretaria")


# ---------- páginas estáticas / redirecionamento ----------


@app.route("/")
def raiz():
    return redirect("/pages/login.html")


@app.route("/health")
def health():
    return {"status": "ok"}


# ---------- API: cadastro, login, sessão (RF01, RF02, RF03) ----------


@app.route("/api/auth/register", methods=["POST"])
def api_register():
    """RF01 — cadastro."""
    body = request.get_json(silent=True) or {}
    nome = (body.get("nome") or "").strip()
    email = (body.get("email") or "").strip()
    senha = body.get("senha") or ""
    telefone = (body.get("telefone") or "").strip()

    if len(nome) < 3:
        return jsonify({"ok": False, "error": "Nome deve ter ao menos 3 caracteres."}), 400
    if "@" not in email:
        return jsonify({"ok": False, "error": "E-mail inválido."}), 400
    if len(senha) < 6:
        return jsonify({"ok": False, "error": "Senha deve ter ao menos 6 caracteres."}), 400

    try:
        h = generate_password_hash(senha)
        user = storage.criar_usuario(nome, email, h, telefone)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 409

    session.clear()
    session["user_id"] = user["id"]
    session["user_email"] = user["email"]
    session["is_admin"] = user.get("is_admin", False)
    mobile_token = storage.criar_token_mobile(user["id"])
    return jsonify(
        {
            "ok": True,
            "user": usuario_publico(user),
            "mobile_token": mobile_token,
            "redirect_to": destino_pos_login(user),
        }
    )


@app.route("/api/auth/login", methods=["POST"])
def api_login():
    """RF02 — login."""
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    senha = body.get("senha") or ""

    user = storage.buscar_usuario_por_email(email)
    if user is None:
        return jsonify({"ok": False, "error": "E-mail ou senha incorretos."}), 401
    if not check_password_hash(user["password_hash"], senha):
        return jsonify({"ok": False, "error": "E-mail ou senha incorretos."}), 401

    session.clear()
    session["user_id"] = user["id"]
    session["user_email"] = user["email"]
    session["is_admin"] = user.get("is_admin", False)
    mobile_token = storage.criar_token_mobile(user["id"])
    return jsonify(
        {
            "ok": True,
            "user": usuario_publico(user),
            "mobile_token": mobile_token,
            "redirect_to": destino_pos_login(user),
        }
    )


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    tok = token_bearer()
    if tok:
        storage.apagar_token_mobile(tok)
    session.clear()
    return jsonify({"ok": True})


@app.route("/api/auth/me", methods=["GET"])
def api_me():
    """Diz se ainda tem alguém logado (útil depois de dar F5 na página)."""
    uid = id_usuario_logado()
    if uid is None:
        return jsonify({"ok": False, "user": None})

    user = storage.buscar_usuario_por_id(uid)
    if user is None:
        session.clear()
        tok = token_bearer()
        if tok:
            storage.apagar_token_mobile(tok)
        return jsonify({"ok": False, "user": None})

    return jsonify({"ok": True, "user": usuario_publico(user)})


@app.route("/api/auth/redirect", methods=["GET"])
def api_auth_redirect():
    uid = id_usuario_logado()
    if uid is None:
        return jsonify({"ok": False, "redirect_to": "/pages/login.html"}), 401
    user = storage.buscar_usuario_por_id(uid)
    if user is None:
        return jsonify({"ok": False, "redirect_to": "/pages/login.html"}), 401
    return jsonify({"ok": True, "redirect_to": destino_pos_login(user)})


@app.route("/api/auth/forgot-password", methods=["POST"])
def api_forgot():
    """
    RF03 — pede reset. Em demo devolve o token no JSON (em produção iria por e-mail).
    """
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    if not email:
        return jsonify({"ok": False, "error": "Informe o e-mail."}), 400

    user = storage.buscar_usuario_por_email(email)
    msg_ok = {
        "ok": True,
        "message": "Se o e-mail estiver cadastrado, conclua a redefinição na próxima etapa.",
    }

    if user is None:
        return jsonify(msg_ok)

    token = storage.salvar_token_reset(email)
    demo = os.environ.get("COE_DEMO_RESET_TOKEN", "1") == "1"

    resposta = dict(msg_ok)
    if demo:
        resposta["demo_token"] = token
        resposta["message"] = (
            "Modo demo: copie o token abaixo (em produção viria no e-mail)."
        )
    return jsonify(resposta)


@app.route("/api/auth/reset-password", methods=["POST"])
def api_reset():
    """RF03 — troca a senha com e-mail + token."""
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    token = (body.get("token") or "").strip()
    nova = body.get("nova_senha") or ""

    if not email or not token or len(nova) < 6:
        return jsonify({"ok": False, "error": "Dados inválidos."}), 400

    esperado = storage.pegar_token_reset(email)
    if esperado is None or esperado != token:
        return jsonify({"ok": False, "error": "Token inválido."}), 400

    storage.atualizar_senha_por_email(email, generate_password_hash(nova))
    storage.limpar_token_reset(email)
    return jsonify({"ok": True, "message": "Senha atualizada. Faça login."})


# ---------- API: triagem (RF04 em diante) ----------


@app.route("/api/triagem", methods=["POST"])
def api_triagem_nova():
    """Salva triagem do usuário logado."""
    uid = id_usuario_logado()
    if uid is None:
        return jsonify({"ok": False, "error": "Faça login."}), 401

    body = request.get_json(silent=True) or {}
    nome = (body.get("nome") or "").strip()
    telefone = (body.get("telefone") or "").strip()
    servico = (body.get("servico") or "").strip()
    periodo = (body.get("periodo") or "").strip()
    sintomas = (body.get("sintomas") or "").strip()

    if len(nome) < 3:
        return jsonify({"ok": False, "error": "Informe o nome completo."}), 400
    if not telefone_valido_rn09(telefone):
        return jsonify({"ok": False, "error": "Formato de telefone inválido. Use (DD) 99999-9999."}), 400
    if servico not in SERVICOS_OK:
        return jsonify({"ok": False, "error": "Serviço inválido."}), 400
    if periodo not in PERIODOS_OK:
        return jsonify({"ok": False, "error": "Período inválido."}), 400

    t = storage.insert_triagem(uid, nome, telefone, servico, periodo, sintomas)

    # Para o paciente não precisamos mostrar user_id na resposta
    safe = {}
    for chave, valor in t.items():
        if chave != "user_id":
            safe[chave] = valor
    return jsonify({"ok": True, "triagem": safe})


@app.route("/api/triagem/minhas", methods=["GET"])
def api_triagem_minhas():
    uid = id_usuario_logado()
    if uid is None:
        return jsonify({"ok": False, "error": "Não autenticado."}), 401

    lista = storage.listar_triagens_do_usuario(uid)
    saida = []
    for t in lista:
        item = {}
        for chave, valor in t.items():
            if chave != "user_id":
                item[chave] = valor
        saida.append(item)
    return jsonify({"ok": True, "triagens": saida})


@app.route("/api/triagem/admin/todas", methods=["GET"])
def api_triagem_admin():
    """Só administrador."""
    uid = id_usuario_logado()
    if uid is None:
        return jsonify({"ok": False, "error": "Não autenticado."}), 401
    if not usuario_tem_acesso_admin():
        return jsonify({"ok": False, "error": "Acesso restrito."}), 403

    lista = storage.listar_todas_triagens()
    return jsonify({"ok": True, "triagens": lista})


@app.route("/api/triagem/admin/atualizar-status", methods=["POST"])
def api_triagem_admin_atualizar_status():
    uid = id_usuario_logado()
    if uid is None:
        return jsonify({"ok": False, "error": "Não autenticado."}), 401
    if not usuario_tem_acesso_admin():
        return jsonify({"ok": False, "error": "Acesso restrito."}), 403

    body = request.get_json(silent=True) or {}
    protocolo = (body.get("protocolo") or "").strip()
    novo_status = (body.get("status") or "").strip()
    if not protocolo:
        return jsonify({"ok": False, "error": "Protocolo obrigatório."}), 400
    if novo_status not in STATUS_TRIAGEM_OK:
        return jsonify({"ok": False, "error": "Status inválido."}), 400

    ok = storage.atualizar_status_triagem(protocolo, novo_status)
    if not ok:
        return jsonify({"ok": False, "error": "Triagem não encontrada."}), 404
    return jsonify({"ok": True, "message": "Status atualizado."})


# Compatibilidade com nomes de rotas do relatório/painel legado
@app.route("/get_triagens", methods=["GET"])
def api_get_triagens_compat():
    return api_triagem_admin()


@app.route("/atualizar_status", methods=["POST"])
def api_atualizar_status_compat():
    return api_triagem_admin_atualizar_status()


# ---------- inicia o servidor ----------


if __name__ == "__main__":
    storage.init_storage()
    porta = int(os.environ.get("PORT", "5000"))
    # 0.0.0.0 = celular na mesma rede Wi‑Fi consegue acessar (use o IP do PC na URL do app)
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    app.run(host=host, port=porta, debug=True)
