# -*- coding: utf-8 -*-
"""
Card 1.3 [T03/MQ03] — Geração e carga de massa sintética (LGPD).

Gera usuários (pacientes) e triagens FICTÍCIOS e grava no Supabase usando o mesmo
formato que o backend (Web/backend/storage_supabase.py) usa.

Garantias de anonimização:
- nomes vêm do Faker (pt_BR), nunca de arquivo real;
- e-mails sempre em @example.com (domínio reservado, RFC 2606 — não pertence a ninguém);
- telefones no formato RN09 "(DD) 9XXXX-XXXX" com DDD fictício e número sorteado;
- CPF NÃO é gravado (o banco não tem coluna de CPF);
- todo registro é marcado (e-mail sintetico.NNNN@example.com e "origem": "massa_sintetica"),
  o que permite apagar só a massa com --limpar.

Uso (a partir da raiz do repositório):
    pip install -r scripts/requirements-dev.txt
    python scripts/gerar_massa.py --dry-run             # gera e audita, sem gravar
    python scripts/gerar_massa.py                       # grava 100 usuários + triagens
    python scripts/gerar_massa.py --usuarios 200 --seed 7
    python scripts/gerar_massa.py --limpar              # remove só a massa sintética

Credenciais: lê SUPABASE_URL e SUPABASE_KEY de Web/backend/.env (nunca commitar).
"""

import argparse
import json
import logging
import os
import random
import re
import sys
from datetime import datetime, timedelta, timezone

from faker import Faker

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(RAIZ, "Web", "backend", ".env")
LOG_DIR = os.path.join(RAIZ, "scripts", "logs")

# Mesmas listas de Web/backend/app.py
SERVICOS = ["tratamento_geral", "protese", "pediatria", "emergencia"]
PERIODOS = ["matutino", "vespertino", "noturno"]
STATUS = ["Pendente", "Em Atendimento", "Finalizado", "Cancelado"]

DOMINIO_SINTETICO = "example.com"
PREFIXO_EMAIL = "sintetico."
ORIGEM = "massa_sintetica"
# Senha única de teste (não é senha real de ninguém); o hash é gerado na carga.
SENHA_TESTE = "Teste@2026"

SINTOMAS = [
    "Dor de dente ao mastigar",
    "Sensibilidade a frio e calor",
    "Gengiva sangrando ao escovar",
    "Dente quebrado",
    "Necessidade de prótese dentária",
    "Dor intensa e inchaço no rosto",
    "Avaliação para criança de 6 anos",
    "Cárie visível no molar",
    "",
]

RE_TELEFONE_RN09 = re.compile(r"^\(\d{2}\) \d{5}-\d{4}$")
RE_EMAIL_SINTETICO = re.compile(r"^sintetico\.\d{4,}@example\.com$")

log = logging.getLogger("gerar_massa")


def configurar_log():
    os.makedirs(LOG_DIR, exist_ok=True)
    arq = os.path.join(LOG_DIR, "carga_%s.log" % datetime.now().strftime("%Y%m%d_%H%M%S"))
    fmt = logging.Formatter("[LOG] %(message)s")
    log.setLevel(logging.INFO)
    for h in (logging.StreamHandler(sys.stdout), logging.FileHandler(arq, encoding="utf-8")):
        h.setFormatter(fmt)
        log.addHandler(h)
    return arq


def gerar_usuarios(fake, n, rng):
    usuarios = []
    for i in range(1, n + 1):
        ddd = rng.choice(["62", "61", "64", "11", "21"])
        tel = "(%s) 9%04d-%04d" % (ddd, rng.randint(0, 9999), rng.randint(0, 9999))
        usuarios.append(
            {
                "nome": fake.name(),
                "email": "%s%04d@%s" % (PREFIXO_EMAIL, i, DOMINIO_SINTETICO),
                "telefone": tel,
            }
        )
    return usuarios


def gerar_triagem(fake, usuario, rng, agora):
    # data aleatória nos últimos 30 dias
    quando = agora - timedelta(seconds=rng.randint(0, 30 * 24 * 3600))
    extra = {
        "nome": usuario["nome"],
        "telefone": usuario["telefone"],
        "sintomas": rng.choice(SINTOMAS),
        "status": rng.choice(STATUS),
        "origem": ORIGEM,
    }
    return {
        "servico": rng.choice(SERVICOS),
        "periodo": rng.choice(PERIODOS),
        "extra": extra,
        "data_triagem": quando.isoformat(),
    }


def auditar_pii(usuarios, triagens_por_usuario):
    """Falha (AssertionError) se qualquer registro não parecer 100% sintético."""
    emails = set()
    for u in usuarios:
        assert RE_EMAIL_SINTETICO.match(u["email"]), "e-mail fora do padrão sintético: %s" % u["email"]
        assert RE_TELEFONE_RN09.match(u["telefone"]), "telefone fora do RN09: %s" % u["telefone"]
        assert u["email"] not in emails, "e-mail duplicado: %s" % u["email"]
        emails.add(u["email"])
    for lista in triagens_por_usuario:
        for t in lista:
            assert t["servico"] in SERVICOS and t["periodo"] in PERIODOS
            assert t["extra"]["origem"] == ORIGEM
            assert "cpf" not in json.dumps(t["extra"]).lower(), "CPF não deve ser gravado"
    # nenhuma chave/URL do Supabase pode ter vazado para os dados
    for var in ("SUPABASE_KEY", "SUPABASE_URL"):
        val = os.environ.get(var, "")
        if val:
            blob = json.dumps(usuarios) + json.dumps(triagens_por_usuario)
            assert val not in blob, "%s apareceu nos dados gerados" % var


def conectar():
    from dotenv import load_dotenv
    from supabase import create_client

    load_dotenv(ENV_PATH)
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_KEY", "").strip()
    if not url or not key:
        sys.exit("Defina SUPABASE_URL e SUPABASE_KEY em Web/backend/.env (veja .env.example).")
    return create_client(url, key)


def carregar(sb, usuarios, triagens_por_usuario):
    from werkzeug.security import generate_password_hash

    senha_hash = generate_password_hash(SENHA_TESTE)
    total = len(usuarios)
    ok_u = ok_t = dup = falhas = 0
    for i, (u, triagens) in enumerate(zip(usuarios, triagens_por_usuario), start=1):
        try:
            res = sb.table("usuarios").insert({**u, "senha": senha_hash}).execute()
            uid = res.data[0]["id_usuario"]
        except Exception as e:  # duplicidade não interrompe o lote
            msg = str(e).lower()
            if "duplicate" in msg or "unique" in msg or "23505" in msg:
                dup += 1
                log.info("Paciente %d/%d já existe (%s) — ignorado", i, total, u["email"])
            else:
                falhas += 1
                log.info("ERRO paciente %d/%d (%s): %s", i, total, u["email"], e)
            continue
        ok_u += 1
        log.info("Inserido paciente %d/%d - UUID: %s", i, total, uid)
        for t in triagens:
            try:
                extra = dict(t["extra"])
                r = (
                    sb.table("triagens")
                    .insert(
                        {
                            "usuario_id": uid,
                            "servico": t["servico"],
                            "periodo": t["periodo"],
                            "solicitacao_dados": json.dumps(extra),
                            "data_triagem": t["data_triagem"],
                        }
                    )
                    .execute()
                )
                id_t = r.data[0]["id_triagem"]
                ano = t["data_triagem"][:4]
                extra["protocolo"] = "TRG-%s-%s" % (ano, str(id_t).replace("-", "")[:8])
                sb.table("triagens").update({"solicitacao_dados": json.dumps(extra)}).eq(
                    "id_triagem", id_t
                ).execute()
                ok_t += 1
                log.info("  Inserida triagem %s - UUID: %s", extra["protocolo"], id_t)
            except Exception as e:
                falhas += 1
                log.info("  ERRO triagem do paciente %d: %s", i, e)
    log.info("RESUMO: %d usuários, %d triagens inseridos; %d duplicados; %d falhas", ok_u, ok_t, dup, falhas)
    return falhas


def limpar(sb):
    # triagens têm ON DELETE CASCADE, então apagar o usuário apaga as triagens dele
    r = (
        sb.table("usuarios")
        .delete()
        .like("email", "%s%%@%s" % (PREFIXO_EMAIL, DOMINIO_SINTETICO))
        .execute()
    )
    log.info("Removidos %d usuários sintéticos (e triagens em cascata)", len(r.data or []))


def main(argv=None):
    p = argparse.ArgumentParser(description="Massa sintética (LGPD) para o Supabase — Card 1.3")
    p.add_argument("--usuarios", type=int, default=100, help="quantidade de pacientes (mín. 100 p/ critério de aceite)")
    p.add_argument("--max-triagens", type=int, default=3, help="máx. de triagens por paciente (1..N)")
    p.add_argument("--seed", type=int, default=None, help="semente p/ resultado reprodutível")
    p.add_argument("--dry-run", action="store_true", help="gera e audita sem gravar no banco")
    p.add_argument("--limpar", action="store_true", help="apaga apenas a massa sintética")
    args = p.parse_args(argv)

    arq_log = configurar_log()
    log.info("Log em %s", arq_log)

    if args.limpar:
        limpar(conectar())
        return 0

    rng = random.Random(args.seed)
    Faker.seed(args.seed)
    fake = Faker("pt_BR")
    agora = datetime.now(timezone.utc)

    usuarios = gerar_usuarios(fake, args.usuarios, rng)
    triagens = [
        [gerar_triagem(fake, u, rng, agora) for _ in range(rng.randint(1, args.max_triagens))]
        for u in usuarios
    ]
    auditar_pii(usuarios, triagens)
    log.info(
        "Auditoria de PII OK: %d usuários e %d triagens, todos sintéticos",
        len(usuarios),
        sum(len(t) for t in triagens),
    )

    if args.dry_run:
        log.info("DRY-RUN: nada foi gravado. Exemplo: %s", json.dumps(usuarios[0], ensure_ascii=False))
        return 0
    return 1 if carregar(conectar(), usuarios, triagens) else 0


if __name__ == "__main__":
    sys.exit(main())
