"""
Card 4.3 — item 2: inspeção de logs (PII).
Envia ao Flask LOCAL (porta 5001, COE_STORAGE=json, sem tocar no Supabase) as operações
que carregam dados sensíveis: cadastro com CPF, login certo e errado, pedido de reset de senha,
reset com token e criação de triagem. Depois procura esses valores no arquivo de log do Flask.

Uso:  python teste_logs_pii.py <caminho-do-log-do-flask>
Os dados abaixo são fictícios (CPF de teste público, e-mail inexistente).
"""
import http.cookiejar
import json
import sys
import time
import urllib.request

BASE = "http://127.0.0.1:5001"
EMAIL = "pii.teste.card43@example.com"
SENHA = "SenhaSecreta#4321"
SENHA_NOVA = "OutraSenha#8765"
CPF = "52998224725"            # CPF fictício válido usado em testes
CPF_MASCARA = "529.982.247-25"
TELEFONE = "(62) 98888-7777"

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def post(caminho, corpo):
    req = urllib.request.Request(
        BASE + caminho,
        data=json.dumps(corpo).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with opener.open(req) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def get(caminho):
    with opener.open(BASE + caminho) as r:
        return r.status, json.loads(r.read() or b"{}")


passos = []
passos.append(("cadastro", post("/api/auth/register", {
    "nome": "Paciente PII Teste", "email": EMAIL, "senha": SENHA,
    "telefone": TELEFONE, "cpf": CPF_MASCARA})))
passos.append(("login senha errada", post("/api/auth/login", {"email": EMAIL, "senha": "errada123"})))
passos.append(("login correto", post("/api/auth/login", {"email": EMAIL, "senha": SENHA})))
passos.append(("triagem", post("/api/triagem", {
    "nome": "Paciente PII Teste", "telefone": TELEFONE, "servico": "tratamento_geral",
    "periodo": "vespertino", "sintomas": "dor leve"})))
passos.append(("minhas triagens", get("/api/triagem/minhas")))
st, corpo = post("/api/auth/forgot-password", {"email": EMAIL})
passos.append(("pedido de reset", (st, {"ok": corpo.get("ok")})))
token = corpo.get("demo_token") or ""
passos.append(("reset de senha", post("/api/auth/reset-password", {
    "email": EMAIL, "token": token, "nova_senha": SENHA_NOVA})))

print("=== Respostas da API (status HTTP) ===")
for nome, (st, _) in passos:
    print(f"{nome:20s} -> {st}")

time.sleep(1)
log = open(sys.argv[1], encoding="utf-8", errors="replace").read()
procurar = {
    "CPF (só números)": CPF,
    "CPF (com máscara)": CPF_MASCARA,
    "senha": SENHA,
    "senha nova": SENHA_NOVA,
    "e-mail": EMAIL,
    "telefone": TELEFONE,
    "token de reset": token or "<sem token>",
}
print("\n=== Dados sensíveis encontrados no log do Flask ===")
achou = False
for rotulo, valor in procurar.items():
    n = log.count(valor) if valor else 0
    print(f"{rotulo:20s}: {'ENCONTRADO ' + str(n) + 'x' if n else 'não aparece'}")
    achou = achou or bool(n)
print("\nRESULTADO:", "FALHOU — há dado sensível no log" if achou else "OK — nenhum dado sensível no log")
