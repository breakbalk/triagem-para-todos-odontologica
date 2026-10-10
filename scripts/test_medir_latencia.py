# -*- coding: utf-8 -*-
"""Testes offline do medidor de latência (sobe o backend em JSON numa thread; não acessa o Supabase)."""

import os
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

AQUI = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(os.path.dirname(AQUI), "Web", "backend")
sys.path.insert(0, AQUI)
sys.path.insert(0, BACKEND)

os.environ.setdefault("COE_STORAGE", "json")
os.environ.setdefault("FLASK_SECRET_KEY", "test-secret-ci")

import medir_latencia as m


def amostra(endpoint, segundos, status=200, fase="uso normal"):
    return {"fase": fase, "endpoint": endpoint, "status": status, "segundos": segundos}


class EstatisticaTest(unittest.TestCase):
    def test_percentil_posto_mais_proximo(self):
        valores = [float(i) for i in range(1, 21)]  # 1..20
        self.assertEqual(m.percentil(valores, 95), 19.0)
        self.assertEqual(m.percentil(valores, 50), 10.0)
        self.assertEqual(m.percentil([3.0], 95), 3.0)
        self.assertIsNone(m.percentil([], 95))

    def test_resumo_ignora_erros_nas_medias(self):
        resumo = m.resumir(
            [amostra(m.SALVAR, 0.2), amostra(m.SALVAR, 0.4), amostra(m.SALVAR, 9.0, status=500)]
        )
        r = resumo[0]
        self.assertEqual((r["n"], r["erros"]), (3, 1))
        self.assertAlmostEqual(r["media"], 0.3)
        self.assertEqual(r["dentro_limite"], 2)

    def test_resumo_ordena_fase_e_endpoint(self):
        resumo = m.resumir(
            [
                amostra(m.FILA, 0.1, fase="concorrência"),
                amostra(m.FILA, 0.1),
                amostra(m.SALVAR, 0.1),
            ]
        )
        self.assertEqual(
            [(r["fase"], r["endpoint"]) for r in resumo],
            [("uso normal", m.SALVAR), ("uso normal", m.FILA), ("concorrência", m.FILA)],
        )


class CriterioTest(unittest.TestCase):
    def test_aprova_media_ate_2s(self):
        resumo = m.resumir([amostra(m.SALVAR, 2.0), amostra(m.FILA, 1.0), amostra(m.FILA, 3.0)])
        self.assertTrue(m.aprovado(resumo))

    def test_reprova_media_acima_de_2s(self):
        resumo = m.resumir([amostra(m.SALVAR, 0.5), amostra(m.FILA, 2.5)])
        self.assertFalse(m.aprovado(resumo))

    def test_reprova_com_erro(self):
        resumo = m.resumir([amostra(m.SALVAR, 0.5), amostra(m.FILA, 0.5), amostra(m.FILA, 0.5, status=403)])
        self.assertFalse(m.aprovado(resumo))

    def test_minhas_nao_entra_no_criterio(self):
        resumo = m.resumir([amostra(m.SALVAR, 0.5), amostra(m.FILA, 0.5), amostra(m.MINHAS, 5.0)])
        self.assertTrue(m.aprovado(resumo))

    def test_sem_amostra_reprova(self):
        self.assertFalse(m.aprovado([]))

    def test_relatorio_mostra_resultado(self):
        resumo = m.resumir([amostra(m.SALVAR, 0.25), amostra(m.FILA, 0.5)])
        info = {"data": "01/01/2026 10:00", "base_url": "http://x", "rodadas": 1, "usuarios": 1, "lote": 1, "fila": 7}
        md = m.relatorio_markdown(resumo, info)
        self.assertIn("**Resultado: APROVADO**", md)
        self.assertIn("| uso normal | `POST /api/triagem` | 1 | 0 | 250 ms |", md)
        self.assertIn("7 triagens", md)


class MedicaoContraBackendLocalTest(unittest.TestCase):
    """Ponta a ponta: backend real (storage JSON em memória) numa porta livre."""

    @classmethod
    def setUpClass(cls):
        import logging

        from werkzeug.serving import make_server

        import app as app_module
        import storage_json

        cls._patches = [
            patch.object(storage_json, "dados", storage_json._estado_vazio()),
            patch.object(storage_json, "_salvar"),
            patch.dict(os.environ, {"COE_SECRETARIA_EMAILS": m.EMAIL_TESTE}),
        ]
        for p in cls._patches:
            p.start()
        logging.getLogger("werkzeug").setLevel(logging.ERROR)  # sem uma linha por pedido
        cls.storage = storage_json
        cls.servidor = make_server("127.0.0.1", 0, app_module.app, threaded=True)
        cls.url = "http://127.0.0.1:%d" % cls.servidor.server_port
        threading.Thread(target=cls.servidor.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        for p in reversed(cls._patches):
            p.stop()

    def test_mede_as_duas_fases_e_aprova(self):
        with tempfile.TemporaryDirectory() as pasta, patch.object(m, "apagar_usuario_teste") as apagar:
            codigo = m.main(
                ["--url", self.url, "--rodadas", "3", "--usuarios", "4", "--lote", "2", "--saida", pasta]
            )
            arquivos = sorted(os.listdir(pasta))
            with open(os.path.join(pasta, arquivos[1]), encoding="utf-8") as f:
                md = f.read()

        self.assertEqual(codigo, 0, md)
        apagar.assert_called_once()  # limpa no fim
        self.assertEqual([a.rsplit(".", 1)[1] for a in arquivos], ["csv", "md"])
        self.assertIn("**Resultado: APROVADO**", md)
        # 3 rodadas + 4 usuários x 2 = 11 triagens salvas, todas na fila
        self.assertIn("| uso normal | `POST /api/triagem` | 3 | 0 |", md)
        self.assertIn("| concorrência | `GET /api/triagem/admin/todas` | 8 | 0 |", md)
        triagens = [t for t in self.storage.dados["triagens"] if "LATENCIA" in t.get("sintomas", "")]
        self.assertEqual(len(triagens), 11)


if __name__ == "__main__":
    unittest.main()
