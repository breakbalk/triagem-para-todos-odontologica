# -*- coding: utf-8 -*-
"""
Card 2.1 [T04/MQ04] — Validação do RLS no Supabase (anon e usuário comum).

Faz chamadas à API REST do Supabase SEM login (chave anon/publishable) e à API do Flask sem login e
com um paciente comum, e confere se a fila geral e as tabelas ficam bloqueadas (401/403).
Grava o resultado em docs/Evidencias/EVIDENCIA CARD 2.1/rls_AAAAMMDD_HHMMSS.md.

Segurança: todas as chamadas que alteram dados usam um filtro que não casa com nenhuma linha
(id_triagem = 00000000-0000-0000-0000-000000000000), então nada real é alterado nem apagado,
mesmo que o RLS esteja desligado.

Pré-requisitos no Web/backend/.env: SUPABASE_URL, SUPABASE_KEY (secret) e SUPABASE_ANON_KEY
(publishable). O backend precisa estar rodando (python Web/backend/app.py).

Uso (raiz do repositório):
    python scripts/validar_rls.py
    python scripts/validar_rls.py --backend http://127.0.0.1:5000
"""

import argparse
import os
import secrets
import sys
import uuid
from datetime import datetime

import httpx
from dotenv import load_dotenv

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(RAIZ, "Web", "backend", ".env")
SAIDA = os.path.join(RAIZ, "docs", "Evidencias", "EVIDENCIA CARD 2.1")
EMAIL_TESTE = "sintetico.rls@example.com"
UUID_ZERO = "00000000-0000-0000-0000-000000000000"

resultados = []


def registrar(nome, esperado, obtido, detalhe=""):
    ok = obtido in esperado
    resultados.append((nome, "/".join(str(e) for e in esperado), obtido, "PASSOU" if ok else "FALHOU", detalhe))
    print("[RLS] %-62s esperado %-8s obtido %s  %s" % (nome, "/".join(str(e) for e in esperado), obtido, "OK" if ok else "FALHOU"))
    return ok


def resumo_corpo(r):
    # Resposta de sucesso pode conter dados reais (se o RLS falhar): nunca grava o conteúdo, só o tamanho.
    if r.status_code < 300:
        return "corpo omitido (%d bytes)" % len(r.content)
    t = (r.text or "").strip().replace("\n", " ")
    return t[:110]


def main():
    p = argparse.ArgumentParser(description="Valida o RLS do Supabase (Card 2.1)")
    p.add_argument("--backend", default="http://127.0.0.1:5000")
    args = p.parse_args()

    load_dotenv(ENV_PATH)
    url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    secret = os.environ.get("SUPABASE_KEY", "").strip()
    anon = os.environ.get("SUPABASE_ANON_KEY", "").strip()
    if not (url and secret and anon):
        sys.exit("Defina SUPABASE_URL, SUPABASE_KEY e SUPABASE_ANON_KEY em Web/backend/.env (veja .env.example).")

    rest = url + "/rest/v1"
    h_anon = {"apikey": anon, "Content-Type": "application/json"}  # sem Authorization: é um visitante sem login
    cli = httpx.Client(timeout=30)

    # ---------------- 1) anon direto na API do Supabase ----------------
    for tabela, col in (("usuarios", "id_usuario"), ("triagens", "id_triagem"),
                        ("mobile_token", "token"), ("password_reset", "email")):
        r = cli.get("%s/%s?select=%s&limit=1" % (rest, tabela, col), headers=h_anon)
        registrar("anon  GET  /%s (listar)" % tabela, (401, 403), r.status_code, resumo_corpo(r))
    r = cli.post(rest + "/triagens", headers=h_anon,
                 json={"usuario_id": str(uuid.uuid4()), "servico": "protese", "periodo": "noturno"})
    registrar("anon  POST /triagens (criar)", (401, 403), r.status_code, resumo_corpo(r))
    r = cli.patch("%s/triagens?id_triagem=eq.%s" % (rest, UUID_ZERO), headers=h_anon, json={"servico": "x"})
    registrar("anon  PATCH /triagens (editar)", (401, 403), r.status_code, resumo_corpo(r))
    r = cli.delete("%s/triagens?id_triagem=eq.%s" % (rest, UUID_ZERO), headers=h_anon)
    registrar("anon  DELETE /triagens (apagar)", (401, 403), r.status_code, resumo_corpo(r))

    # ---------------- 2) o backend (secret) continua funcionando ----------------
    h_sec = {"apikey": secret, "Authorization": "Bearer " + secret}
    r = cli.get("%s/usuarios?select=id_usuario&limit=1" % rest, headers=h_sec)
    registrar("backend (secret) GET /usuarios continua liberado", (200,), r.status_code)

    # ---------------- 3) Flask: sem login e com paciente comum ----------------
    b = args.backend.rstrip("/")
    try:
        cli.get(b + "/health")
    except Exception as e:  # noqa: BLE001
        sys.exit("Backend fora do ar em %s (%s). Rode: python Web/backend/app.py" % (b, e))

    r = cli.get(b + "/api/triagem/admin/todas")
    registrar("Flask sem login   GET  /api/triagem/admin/todas", (401,), r.status_code, resumo_corpo(r))
    r = cli.post(b + "/api/triagem/admin/atualizar-status", json={"protocolo": "X", "status": "Finalizado"})
    registrar("Flask sem login   POST /api/triagem/admin/atualizar-status", (401,), r.status_code, resumo_corpo(r))

    from supabase import create_client
    from werkzeug.security import generate_password_hash

    sb = create_client(url, secret)
    senha = secrets.token_urlsafe(18)
    try:
        sb.table("usuarios").delete().eq("email", EMAIL_TESTE).execute()  # sobra de execução anterior
        sb.table("usuarios").insert({"nome": "Paciente RLS Sintetico", "email": EMAIL_TESTE,
                                     "senha": generate_password_hash(senha), "telefone": "(00) 90000-0000"}).execute()
        r = cli.post(b + "/api/auth/login", json={"email": EMAIL_TESTE, "senha": senha})
        tok = (r.json() or {}).get("mobile_token") if r.status_code == 200 else None
        registrar("Flask paciente    POST /api/auth/login", (200,), r.status_code)
        h_pac = {"Authorization": "Bearer %s" % tok} if tok else {}
        r = cli.get(b + "/api/triagem/admin/todas", headers=h_pac)
        registrar("Flask paciente    GET  /api/triagem/admin/todas", (403,), r.status_code, resumo_corpo(r))
        r = cli.post(b + "/api/triagem/admin/atualizar-status", headers=h_pac,
                     json={"protocolo": "X", "status": "Finalizado"})
        registrar("Flask paciente    POST /api/triagem/admin/atualizar-status", (403,), r.status_code, resumo_corpo(r))
        r = cli.get(b + "/api/triagem/minhas", headers=h_pac)
        registrar("Flask paciente    GET  /api/triagem/minhas (fluxo legítimo)", (200,), r.status_code)
    finally:
        sb.table("usuarios").delete().eq("email", EMAIL_TESTE).execute()  # limpeza: tokens saem em cascata
        print("[RLS] Paciente de teste apagado.")

    # ---------------- relatório ----------------
    os.makedirs(SAIDA, exist_ok=True)
    agora = datetime.now()
    arq = os.path.join(SAIDA, "rls_%s.md" % agora.strftime("%Y%m%d_%H%M%S"))
    falhas = [x for x in resultados if x[3] != "PASSOU"]
    with open(arq, "w", encoding="utf-8") as f:
        f.write("# Card 2.1 [T04/MQ04] — Validação do RLS\n\n")
        f.write("- Data: %s\n- Supabase: projeto Triagem para Todos (chave anon/publishable, sem login)\n" % agora.strftime("%d/%m/%Y %H:%M"))
        f.write("- Backend: %s\n- Dados de teste: 1 paciente (`%s`), apagado no fim; nenhuma linha real foi alterada.\n\n" % (b, EMAIL_TESTE))
        f.write("| Chamada | Esperado | Obtido | Resultado | Resposta |\n|---|---|---|---|---|\n")
        for n, e, o, res, d in resultados:
            f.write("| %s | %s | %s | %s | `%s` |\n" % (n, e, o, res, d.replace("|", "/")))
        f.write("\n**%s**: %d de %d verificações passaram.\n" % ("APROVADO" if not falhas else "REPROVADO",
                                                                 len(resultados) - len(falhas), len(resultados)))
    print("[RLS] Relatório: %s" % arq)
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
