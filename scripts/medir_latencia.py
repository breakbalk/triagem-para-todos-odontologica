# -*- coding: utf-8 -*-
"""
Card 2.2 [T05/MQ05] — Medição de latência das APIs do COE.

Mede o tempo de resposta (do envio do pedido até o fim da resposta) de:
- POST /api/triagem              salvar triagem
- GET  /api/triagem/minhas       paciente consulta as próprias triagens
- GET  /api/triagem/admin/todas  recepção consulta a fila

Em duas fases:
1. Uso normal: uma requisição por vez (--rodadas de cada endpoint).
2. Concorrência moderada: --usuarios clientes ao mesmo tempo, cada um com a
   própria sessão (cookie, como o navegador), mandando --lote requisições de cada.

Critério de aceite do card: tempo médio <= 2,0 s para salvar triagem e consultar a fila.

Pré-requisitos (no Web/backend/.env do backend que vai ser medido):
- COE_STORAGE=supabase, SUPABASE_URL e SUPABASE_KEY;
- COE_SECRETARIA_EMAILS=sintetico.latencia@example.com (a fila é restrita a
  admin/secretaria; assim o teste não precisa da senha do admin).

Uso (a partir da raiz do repositório, com o backend rodando):
    python scripts/medir_latencia.py
    python scripts/medir_latencia.py --rodadas 50 --usuarios 20 --lote 5
    python scripts/medir_latencia.py --limpar     # só apaga o usuário de teste

Dados de teste: o usuário é sintetico.latencia@example.com (domínio reservado,
RFC 2606), com senha aleatória que não é gravada em lugar nenhum; telefone com
DDD 00 e "LATENCIA" no sintoma. No fim, o usuário é apagado e as triagens dele
saem junto (ON DELETE CASCADE). Use --manter para não apagar.
"""

import argparse
import csv
import http.cookiejar
import json
import math
import os
import secrets
import statistics
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(RAIZ, "Web", "backend", ".env")
SAIDA_PADRAO = os.path.join(RAIZ, "docs", "Evidencias", "EVIDENCIA CARD 2.2")

EMAIL_TESTE = "sintetico.latencia@example.com"
LIMITE_S = 2.0

SALVAR = "POST /api/triagem"
MINHAS = "GET /api/triagem/minhas"
FILA = "GET /api/triagem/admin/todas"
ENDPOINTS = [SALVAR, MINHAS, FILA]
# os dois que o critério de aceite cobra
CRITERIO = [SALVAR, FILA]

TRIAGEM = {
    "nome": "Paciente Sintetico Latencia",
    "telefone": "(00) 90000-0000",
    "servico": "tratamento_geral",
    "periodo": "matutino",
    "sintomas": "LATENCIA - teste de desempenho (Card 2.2)",
}


class Cliente:
    """Uma sessão HTTP (cookie próprio), como uma aba do navegador."""

    def __init__(self, base_url, timeout=30):
        self.base = base_url.rstrip("/")
        self.timeout = timeout
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
        )

    def pedir(self, metodo, caminho, corpo=None):
        """Faz o pedido e devolve (status, segundos, json ou None)."""
        dados = None
        headers = {"Accept": "application/json"}
        if corpo is not None:
            dados = json.dumps(corpo).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(self.base + caminho, data=dados, headers=headers, method=metodo)
        inicio = time.perf_counter()
        try:
            with self.opener.open(req, timeout=self.timeout) as r:
                bruto = r.read()
                status = r.status
        except urllib.error.HTTPError as e:
            bruto = e.read()
            status = e.code
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            return 0, time.perf_counter() - inicio, {"erro": str(e)}
        segundos = time.perf_counter() - inicio
        try:
            return status, segundos, json.loads(bruto.decode("utf-8") or "null")
        except ValueError:
            return status, segundos, None

    def entrar(self, email, senha):
        status, _, body = self.pedir("POST", "/api/auth/login", {"email": email, "senha": senha})
        if status != 200:
            raise RuntimeError("login falhou (%s): %s" % (status, body))
        return body

    def chamar(self, endpoint):
        """Chama um dos ENDPOINTS e devolve (status, segundos, tamanho_da_fila)."""
        if endpoint == SALVAR:
            status, s, _ = self.pedir("POST", "/api/triagem", TRIAGEM)
            return status, s, None
        if endpoint == MINHAS:
            status, s, _ = self.pedir("GET", "/api/triagem/minhas")
            return status, s, None
        status, s, body = self.pedir("GET", "/api/triagem/admin/todas")
        fila = len(body.get("triagens") or []) if isinstance(body, dict) else None
        return status, s, fila


def percentil(valores, p):
    """Percentil pelo método do posto mais próximo (p entre 0 e 100)."""
    if not valores:
        return None
    ordenados = sorted(valores)
    k = max(1, math.ceil(p / 100.0 * len(ordenados)))
    return ordenados[k - 1]


def resumir(amostras):
    """amostras: lista de dicts {fase, endpoint, status, segundos}. Agrupa por fase/endpoint."""
    grupos = {}
    for a in amostras:
        grupos.setdefault((a["fase"], a["endpoint"]), []).append(a)
    resumo = []
    for (fase, endpoint), itens in grupos.items():
        ok = [a["segundos"] for a in itens if a["status"] == 200]
        resumo.append(
            {
                "fase": fase,
                "endpoint": endpoint,
                "n": len(itens),
                "erros": len(itens) - len(ok),
                "media": statistics.mean(ok) if ok else None,
                "mediana": statistics.median(ok) if ok else None,
                "p95": percentil(ok, 95),
                "max": max(ok) if ok else None,
                "dentro_limite": sum(1 for s in ok if s <= LIMITE_S),
            }
        )
    ordem_fase = {"uso normal": 0, "concorrência": 1}
    resumo.sort(key=lambda r: (ordem_fase.get(r["fase"], 9), ENDPOINTS.index(r["endpoint"])))
    return resumo


def aprovado(resumo):
    """Critério do card: média <= 2,0 s, sem erro, para salvar triagem e consultar a fila."""
    cobrados = [r for r in resumo if r["endpoint"] in CRITERIO]
    return bool(cobrados) and all(
        r["erros"] == 0 and r["media"] is not None and r["media"] <= LIMITE_S for r in cobrados
    )


def _ms(s):
    return "—" if s is None else "%d ms" % round(s * 1000)


def relatorio_markdown(resumo, info):
    linhas = [
        "# Card 2.2 [T05/MQ05] — Latência das APIs",
        "",
        "- Data: %s" % info["data"],
        "- Backend medido: %s" % info["base_url"],
        "- Uso normal: %d rodadas de cada endpoint, uma por vez" % info["rodadas"],
        "- Concorrência: %d usuários ao mesmo tempo, %d requisições de cada endpoint por usuário"
        % (info["usuarios"], info["lote"]),
        "- Tamanho da fila no fim: %s triagens" % info.get("fila", "—"),
        "- Critério de aceite: tempo médio <= 2,0 s para salvar triagem e consultar a fila",
        "",
        "| Fase | Endpoint | Pedidos | Erros | Média | Mediana | p95 | Máximo | <= 2,0 s |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in resumo:
        ok = r["n"] - r["erros"]
        pct = "%d%%" % round(100.0 * r["dentro_limite"] / ok) if ok else "—"
        linhas.append(
            "| %s | `%s` | %d | %d | %s | %s | %s | %s | %s |"
            % (r["fase"], r["endpoint"], r["n"], r["erros"], _ms(r["media"]), _ms(r["mediana"]),
               _ms(r["p95"]), _ms(r["max"]), pct)
        )
    linhas += ["", "**Resultado: %s**" % ("APROVADO" if aprovado(resumo) else "REPROVADO"), ""]
    return "\n".join(linhas)


def medir(base_url, senha, rodadas, usuarios, lote):
    """Roda as duas fases e devolve (amostras, tamanho_da_fila)."""
    amostras = []
    trava = threading.Lock()
    fila = {"n": None}

    def anotar(fase, endpoint, status, segundos, n_fila):
        with trava:
            amostras.append({"fase": fase, "endpoint": endpoint, "status": status, "segundos": segundos})
            if n_fila is not None:
                fila["n"] = n_fila

    # Fase 1 — uso normal
    c = Cliente(base_url)
    c.entrar(EMAIL_TESTE, senha)
    for _ in range(rodadas):
        for ep in ENDPOINTS:
            status, s, n_fila = c.chamar(ep)
            anotar("uso normal", ep, status, s, n_fila)

    # Fase 2 — concorrência moderada: todos começam juntos
    largada = threading.Barrier(usuarios)

    def trabalhador(_):
        cli = Cliente(base_url)
        cli.entrar(EMAIL_TESTE, senha)
        largada.wait()
        for _ in range(lote):
            for ep in ENDPOINTS:
                status, s, n_fila = cli.chamar(ep)
                anotar("concorrência", ep, status, s, n_fila)

    with ThreadPoolExecutor(max_workers=usuarios) as pool:
        list(pool.map(trabalhador, range(usuarios)))
    return amostras, fila["n"]


def apagar_usuario_teste():
    """Apaga o usuário de teste direto no Supabase (as triagens e tokens saem em cascata)."""
    from dotenv import load_dotenv

    load_dotenv(ENV_PATH)
    if os.environ.get("COE_STORAGE", "json").strip().lower() != "supabase":
        print("[LATENCIA] COE_STORAGE não é supabase: nada a apagar no banco.")
        return 0
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"].strip(), os.environ["SUPABASE_KEY"].strip())
    r = sb.table("usuarios").delete().eq("email", EMAIL_TESTE).execute()
    n = len(r.data or [])
    print("[LATENCIA] Usuário de teste apagado: %d (triagens e tokens dele em cascata)" % n)
    return n


def salvar(amostras, resumo, info, pasta):
    os.makedirs(pasta, exist_ok=True)
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    md = os.path.join(pasta, "latencia_%s.md" % carimbo)
    with open(md, "w", encoding="utf-8") as f:
        f.write(relatorio_markdown(resumo, info))
    bruto = os.path.join(pasta, "latencia_%s.csv" % carimbo)
    with open(bruto, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["fase", "endpoint", "status", "segundos"])
        w.writeheader()
        w.writerows(amostras)
    return md, bruto


def main(argv=None):
    p = argparse.ArgumentParser(description="Mede a latência das APIs do COE — Card 2.2")
    p.add_argument("--url", default="http://127.0.0.1:5000", help="endereço do backend")
    p.add_argument("--rodadas", type=int, default=30, help="uso normal: pedidos de cada endpoint")
    p.add_argument("--usuarios", type=int, default=10, help="concorrência: clientes ao mesmo tempo")
    p.add_argument("--lote", type=int, default=5, help="concorrência: pedidos de cada endpoint por cliente")
    p.add_argument("--saida", default=SAIDA_PADRAO, help="pasta do relatório")
    p.add_argument("--manter", action="store_true", help="não apaga o usuário de teste no fim")
    p.add_argument("--limpar", action="store_true", help="só apaga o usuário de teste e sai")
    args = p.parse_args(argv)

    if args.limpar:
        apagar_usuario_teste()
        return 0

    base = Cliente(args.url)
    status, _, _ = base.pedir("GET", "/health")
    if status != 200:
        sys.exit("Backend fora do ar em %s (rode: cd Web/backend && python app.py)." % args.url)

    senha = secrets.token_urlsafe(18)  # vale só para esta execução
    status, _, body = base.pedir(
        "POST", "/api/auth/register",
        {"nome": "Paciente Sintetico Latencia", "email": EMAIL_TESTE, "senha": senha, "telefone": TRIAGEM["telefone"]},
    )
    if status != 200:
        sys.exit("Não consegui criar o usuário de teste (%s): %s\n"
                 "Se sobrou de uma execução anterior, rode: python scripts/medir_latencia.py --limpar"
                 % (status, (body or {}).get("error")))
    nivel = ((body or {}).get("user") or {}).get("nivel_acesso")
    if nivel not in ("admin", "secretaria"):
        print("[LATENCIA] AVISO: %s não tem acesso à fila (nivel_acesso=%s). Ponha o e-mail em "
              "COE_SECRETARIA_EMAILS no .env do backend; a fila vai aparecer como erro (403)."
              % (EMAIL_TESTE, nivel))

    try:
        print("[LATENCIA] Medindo %s ..." % args.url)
        amostras, n_fila = medir(args.url, senha, args.rodadas, args.usuarios, args.lote)
    finally:
        if not args.manter:
            apagar_usuario_teste()

    resumo = resumir(amostras)
    info = {
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "base_url": args.url,
        "rodadas": args.rodadas,
        "usuarios": args.usuarios,
        "lote": args.lote,
        "fila": n_fila,
    }
    md, bruto = salvar(amostras, resumo, info, args.saida)
    print(relatorio_markdown(resumo, info))
    print("[LATENCIA] Relatório: %s\n[LATENCIA] Dados brutos: %s" % (md, bruto))
    return 0 if aprovado(resumo) else 1


if __name__ == "__main__":
    for saida in (sys.stdout, sys.stderr):  # acentos no console do Windows
        if hasattr(saida, "reconfigure"):
            saida.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
