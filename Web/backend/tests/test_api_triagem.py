# -*- coding: utf-8 -*-
"""Testes da API de triagem (RN09, auth, validações)."""

import json
import os
import unittest
from unittest.mock import patch

os.environ.setdefault("COE_STORAGE", "json")
os.environ.setdefault("FLASK_SECRET_KEY", "test-secret-ci")

import app as app_module


class TelefoneRN09Test(unittest.TestCase):
    def test_formato_valido(self):
        self.assertTrue(app_module.telefone_valido_rn09("(62) 99999-9999"))
        self.assertTrue(app_module.telefone_valido_rn09("(11) 98888-7777"))

    def test_formato_invalido(self):
        self.assertFalse(app_module.telefone_valido_rn09("62999999999"))
        self.assertFalse(app_module.telefone_valido_rn09("(62)99999-9999"))  # sem espaço
        self.assertFalse(app_module.telefone_valido_rn09("(62) 9999-9999"))  # só 4 no meio
        self.assertFalse(app_module.telefone_valido_rn09(""))
        self.assertFalse(app_module.telefone_valido_rn09("123456789012345"))


class TriagemPostTest(unittest.TestCase):
    def setUp(self):
        app_module.app.config["TESTING"] = True
        self.client = app_module.app.test_client()

    def test_sem_login_retorna_401(self):
        r = self.client.post(
            "/api/triagem",
            data=json.dumps(
                {
                    "nome": "Fulano Teste",
                    "telefone": "(62) 99999-9999",
                    "servico": "tratamento_geral",
                    "periodo": "matutino",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 401)

    @patch.object(app_module, "id_usuario_logado", return_value=1)
    @patch.object(app_module.storage, "criar_triagem")
    def test_telefone_invalido_nao_persiste(self, mock_criar, _uid):
        r = self.client.post(
            "/api/triagem",
            data=json.dumps(
                {
                    "nome": "Fulano Teste",
                    "telefone": "62 99999-9999",
                    "servico": "tratamento_geral",
                    "periodo": "matutino",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 400)
        self.assertFalse(r.get_json()["ok"])
        mock_criar.assert_not_called()

    @patch.object(app_module, "id_usuario_logado", return_value=1)
    @patch.object(app_module.storage, "criar_triagem")
    def test_telefone_valido_200(self, mock_criar, _uid):
        retorno = {
            "id": "t1",
            "user_id": 1,
            "nome": "Fulano Teste",
            "telefone": "(62) 99999-9999",
            "servico": "tratamento_geral",
            "periodo": "matutino",
            "sintomas": "",
            "status": "Pendente",
            "data_solicitacao": "2026-04-26T12:00:00",
            "protocolo": "TRG-2026-00000001",
        }
        mock_criar.return_value = dict(retorno)
        r = self.client.post(
            "/api/triagem",
            data=json.dumps(
                {
                    "nome": "Fulano Teste",
                    "telefone": "(62) 99999-9999",
                    "servico": "tratamento_geral",
                    "periodo": "matutino",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200, r.get_json())
        body = r.get_json()
        self.assertTrue(body["ok"])
        self.assertEqual(body["triagem"]["telefone"], "(62) 99999-9999")
        mock_criar.assert_called_once()

    @patch.object(app_module, "id_usuario_logado", return_value=1)
    @patch.object(app_module.storage, "criar_triagem")
    def test_servico_invalido_400(self, mock_criar, _uid):
        r = self.client.post(
            "/api/triagem",
            data=json.dumps(
                {
                    "nome": "Fulano Teste",
                    "telefone": "(62) 99999-9999",
                    "servico": "inexistente",
                    "periodo": "matutino",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 400)
        mock_criar.assert_not_called()


class HealthTest(unittest.TestCase):
    def setUp(self):
        app_module.app.config["TESTING"] = True
        self.client = app_module.app.test_client()

    def test_health(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json().get("status"), "ok")


if __name__ == "__main__":
    unittest.main()
