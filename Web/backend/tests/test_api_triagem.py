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
    @patch.object(app_module.storage, "insert_triagem")
    def test_telefone_invalido_nao_persiste(self, mock_insert, _uid):
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
        mock_insert.assert_not_called()

    @patch.object(app_module, "id_usuario_logado", return_value=1)
    @patch.object(app_module.storage, "insert_triagem")
    def test_telefone_valido_200(self, mock_insert, _uid):
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
        mock_insert.return_value = dict(retorno)
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
        mock_insert.assert_called_once()

    @patch.object(app_module, "id_usuario_logado", return_value=1)
    @patch.object(app_module.storage, "insert_triagem")
    def test_servico_invalido_400(self, mock_insert, _uid):
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
        mock_insert.assert_not_called()


class AuthAndAdminCompatTest(unittest.TestCase):
    def setUp(self):
        app_module.app.config["TESTING"] = True
        self.client = app_module.app.test_client()

    @patch.object(app_module.storage, "buscar_usuario_por_email")
    @patch.object(app_module.storage, "criar_token_mobile", return_value="tok-1")
    def test_login_retorna_nivel_e_redirect(self, _tok, mock_user):
        mock_user.return_value = {
            "id": 1,
            "nome": "Admin COE",
            "email": "admin@coe.unievangelica.edu.br",
            "password_hash": app_module.generate_password_hash("Senha@123"),
            "telefone": "",
            "is_admin": True,
        }
        r = self.client.post(
            "/api/auth/login",
            data=json.dumps({"email": "admin@coe.unievangelica.edu.br", "senha": "Senha@123"}),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200, r.get_json())
        body = r.get_json()
        self.assertEqual(body["user"]["nivel_acesso"], "admin")
        self.assertEqual(body["redirect_to"], "/pages/admin.html")

    @patch.object(app_module, "id_usuario_logado", return_value=1)
    @patch.object(app_module, "usuario_tem_acesso_admin", return_value=True)
    @patch.object(app_module.storage, "listar_todas_triagens", return_value=[])
    def test_get_triagens_compat(self, _list, _priv, _uid):
        r = self.client.get("/get_triagens")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.get_json()["ok"])

    @patch.object(app_module, "id_usuario_logado", return_value=1)
    @patch.object(app_module, "usuario_tem_acesso_admin", return_value=True)
    @patch.object(app_module.storage, "atualizar_status_triagem", return_value=True)
    def test_atualizar_status_compat(self, _up, _priv, _uid):
        r = self.client.post(
            "/atualizar_status",
            data=json.dumps({"protocolo": "TRG-2026-000001", "status": "Finalizado"}),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertTrue(r.get_json()["ok"])

    @patch.object(app_module, "id_usuario_logado", return_value=1)
    @patch.object(app_module.storage, "buscar_usuario_por_id")
    def test_secretaria_tem_acesso_admin(self, mock_user, _uid):
        mock_user.return_value = {
            "id": 1,
            "nome": "Sec",
            "email": "sec@coe.local",
            "password_hash": "x",
            "telefone": "",
            "is_admin": False,
        }
        with patch.dict(os.environ, {"COE_SECRETARIA_EMAILS": "sec@coe.local"}, clear=False):
            self.assertTrue(app_module.usuario_tem_acesso_admin())


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
