"""Card 3.5 na base real: derruba a conexão DEPOIS do insert gravar e confere no Supabase. Usuário: sintetico.latencia@example.com."""
import os, sys
sys.path.insert(0, "Web/backend")
for l in open("Web/backend/.env"):
    if "=" in l:
        k, v = l.strip().split("=", 1)
        os.environ[k] = v
import httpx
import storage_supabase as st

EMAIL = "sintetico.latencia@example.com"
u = st.buscar_usuario_por_email(EMAIL) or st.criar_usuario("Sintetico Latencia", EMAIL, "hash-falso", "(00) 90000-0000")
uid = u["id"]
dados = ("Sintetico Latencia", "(00) 90000-0000", "Triagem", "Manhã", "LATENCIA queda pos-envio")


def linhas():
    r = st._tabela("triagens").select("*").eq("usuario_id", uid).execute()
    return r.data or []


# 1) queda de conexão logo depois do insert gravar (a resposta se perde)
orig = st._Consulta._montar
estado = {"quedas": 0}


def montar_com_queda(self):
    q = orig(self)
    if self._insert and self._nome == "triagens":
        real = q.execute

        def execute():
            r = real()
            if estado["quedas"] < 1:
                estado["quedas"] += 1
                raise httpx.RemoteProtocolError("Server disconnected (simulado após o insert)")
            return r

        q.execute = execute
    return q


st._Consulta._montar = montar_com_queda
t1 = st.criar_triagem(uid, *dados)
st._Consulta._montar = orig
a = linhas()
print("1) queda simulada após o insert: quedas=%d, linhas no banco=%d, protocolo=%s, id=%s" % (estado["quedas"], len(a), t1["protocolo"], t1["id"]))
assert estado["quedas"] == 1 and len(a) == 1 and a[0]["id_triagem"] == t1["id"], "duplicou ou perdeu"
assert "__TEMP__" not in a[0]["solicitacao_dados"] and a[0]["solicitacao_dados"].count("TRG-") == 1

# 2) paciente reenvia o formulário (mesmos dados)
t2 = st.criar_triagem(uid, *dados)
b = linhas()
print("2) reenvio idêntico: linhas=%d, mesmo id=%s, mesmo protocolo=%s" % (len(b), t2["id"] == t1["id"], t2["protocolo"] == t1["protocolo"]))
assert len(b) == 1 and t2["id"] == t1["id"]

# 3) dados diferentes = outra triagem, protocolo próprio
t3 = st.criar_triagem(uid, dados[0], dados[1], dados[2], dados[3], "LATENCIA outra")
c = linhas()
print("3) dados diferentes: linhas=%d, protocolos distintos=%s" % (len(c), len({r["solicitacao_dados"] for r in c}) == 2 and t3["protocolo"] != t1["protocolo"]))
assert len(c) == 2
print("órfãos/__TEMP__ no banco:", sum("__TEMP__" in r["solicitacao_dados"] for r in c))
print("OK")
