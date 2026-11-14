# -*- coding: utf-8 -*-
"""Card 3.5 — triagem gravada com um insert só (UUID e protocolo gerados no app) e reenvio idempotente."""

import os
import re
import unittest
from unittest.mock import MagicMock, patch

import httpx

os.environ.setdefault("COE_STORAGE", "json")
os.environ.setdefault("FLASK_SECRET_KEY", "test-secret-ci")

import storage_supabase as st

PROTOCOLO = re.compile(r"^TRG-\d{4}-[0-9a-f]{8}$")


class _Banco:
    """Mini-Supabase em memória: insert/select com eq e gte. `quedas` = inserts que gravam e depois perdem a conexão."""

    def __init__(self, quedas=0):
        self.linhas = []
        self.quedas = quedas
        self.inserts = 0
        self.updates = 0

    def table(self, _nome):
        return _Consulta(self)


class _Consulta:
    def __init__(self, banco):
        self.b = banco
        self.filtros = []
        self.acao = None
        self.linha = None

    def select(self, *_a):
        self.acao = "select"
        return self

    def insert(self, linha):
        self.acao, self.linha = "insert", dict(linha)
        return self

    def update(self, *_a):
        self.b.updates += 1
        return self

    def eq(self, col, val):
        self.filtros.append(("eq", col, str(val)))
        return self

    def gte(self, col, val):
        self.filtros.append(("gte", col, str(val)))
        return self

    def limit(self, _n):
        return self

    def execute(self):
        if self.acao == "insert":
            self.b.inserts += 1
            if any(r["id_triagem"] == self.linha["id_triagem"] for r in self.b.linhas):
                raise Exception("duplicate key value violates unique constraint (23505)")
            # Card 3.6: protocolo é NOT NULL + UNIQUE no banco real
            if not self.linha.get("protocolo"):
                raise Exception('null value in column "protocolo" violates not-null constraint (23502)')
            if any(r["protocolo"] == self.linha["protocolo"] for r in self.b.linhas):
                raise Exception('duplicate key value violates unique constraint "triagens_protocolo_key" (23505)')
            self.b.linhas.append(self.linha)
            if self.b.quedas > 0:
                self.b.quedas -= 1
                raise httpx.RemoteProtocolError("Server disconnected")
            return MagicMock(data=[self.linha])
        achadas = []
        for r in self.b.linhas:
            ok = True
            for op, col, val in self.filtros:
                v = str(r.get(col))
                ok = ok and (v == val if op == "eq" else v >= val)
            if ok:
                achadas.append(r)
        return MagicMock(data=achadas)


class CriarTriagemTest(unittest.TestCase):
    def _criar(self, banco, **kw):
        dados = dict(nome="Ana", telefone="(62) 99999-9999", servico="Triagem", periodo="Manhã", sintomas="dor")
        dados.update(kw)
        with patch.object(st, "_sb", return_value=banco), patch.object(st.time, "sleep"):
            return st.criar_triagem("11111111-1111-4111-8111-111111111111", **dados)

    def test_um_insert_sem_temp_e_sem_update(self):
        b = _Banco()
        t = self._criar(b)
        self.assertEqual((b.inserts, b.updates), (1, 0))
        self.assertRegex(t["protocolo"], PROTOCOLO)
        self.assertNotIn("__TEMP__", b.linhas[0]["solicitacao_dados"])
        self.assertEqual(t["protocolo"][-8:], t["id"].replace("-", "")[:8])

    def test_queda_depois_do_insert_nao_duplica(self):
        # o banco gravou, a resposta se perdeu: o retry bate na chave primária e devolve a mesma triagem
        b = _Banco(quedas=1)
        t = self._criar(b)
        self.assertEqual(len(b.linhas), 1)
        self.assertEqual(t["id"], b.linhas[0]["id_triagem"])
        self.assertRegex(t["protocolo"], PROTOCOLO)

    def test_reenvio_identico_devolve_a_mesma_triagem(self):
        b = _Banco()
        a = self._criar(b)
        c = self._criar(b)
        self.assertEqual(len(b.linhas), 1)
        self.assertEqual((a["id"], a["protocolo"]), (c["id"], c["protocolo"]))

    def test_dados_diferentes_geram_outra_triagem(self):
        b = _Banco()
        a = self._criar(b)
        c = self._criar(b, sintomas="febre")
        self.assertEqual(len(b.linhas), 2)
        self.assertNotEqual(a["protocolo"], c["protocolo"])

    def test_outro_usuario_nao_reaproveita(self):
        b = _Banco()
        self._criar(b)
        with patch.object(st, "_sb", return_value=b):
            st.criar_triagem("22222222-2222-4222-8222-222222222222", "Ana", "(62) 99999-9999", "Triagem", "Manhã", "dor")
        self.assertEqual(len(b.linhas), 2)

    def test_protocolo_vai_na_coluna_e_igual_ao_do_json(self):
        b = _Banco()
        t = self._criar(b)
        self.assertEqual(b.linhas[0]["protocolo"], t["protocolo"])
        self.assertIn(t["protocolo"], b.linhas[0]["solicitacao_dados"])

    def test_colisao_de_protocolo_gera_novo_uuid(self):
        b = _Banco()
        b.linhas.append({"id_triagem": "x", "usuario_id": "outro", "servico": "s", "periodo": "p",
                         "solicitacao_dados": "{}", "protocolo": "TRG-%d-aaaaaaaa" % st.datetime.now().year})
        ids = ["aaaaaaaa-0000-4000-8000-000000000001", "bbbbbbbb-0000-4000-8000-000000000002"]
        with patch.object(st.uuid, "uuid4", side_effect=[__import__("uuid").UUID(i) for i in ids]):
            t = self._criar(b)
        self.assertEqual(len(b.linhas), 2)
        self.assertEqual(t["id"], ids[1])
        self.assertTrue(t["protocolo"].endswith("bbbbbbbb"))

    def test_colisao_em_todas_as_tentativas_levanta_erro(self):
        b = _Banco()
        b.linhas.append({"id_triagem": "x", "usuario_id": "outro", "servico": "s", "periodo": "p",
                         "solicitacao_dados": "{}", "protocolo": "TRG-%d-aaaaaaaa" % st.datetime.now().year})
        u = __import__("uuid").UUID("aaaaaaaa-0000-4000-8000-000000000001")
        with patch.object(st.uuid, "uuid4", side_effect=[u] * 5), self.assertRaises(RuntimeError):
            self._criar(b)

    def test_erro_que_nao_e_de_rede_sobe(self):
        class _Quebra(_Banco):
            def table(self, n):
                c = super().table(n)
                c.execute = MagicMock(side_effect=ValueError("falhou"))
                return c

        with patch.object(st, "_sb", return_value=_Quebra()), self.assertRaises(ValueError):
            st.criar_triagem("u", "Ana", "(62) 99999-9999", "Triagem", "Manhã", "dor")


if __name__ == "__main__":
    unittest.main()
