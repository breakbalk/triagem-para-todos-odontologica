# -*- coding: utf-8 -*-
"""Card 3.4 — cliente Supabase isolado por thread e retry em httpx.RemoteProtocolError (sem rede, sem banco)."""

import os
import threading
import unittest
from unittest.mock import MagicMock, patch

import httpx

os.environ.setdefault("COE_STORAGE", "json")
os.environ.setdefault("FLASK_SECRET_KEY", "test-secret-ci")
os.environ.setdefault("SUPABASE_URL", "https://exemplo.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "chave-falsa")

import storage_supabase as st


class _Tabela:
    """Imita table().x().y().execute(): falha as primeiras `falhas` vezes com RemoteProtocolError."""

    def __init__(self, falhas, dados):
        self.falhas = falhas
        self.dados = dados
        self.chamadas = 0

    def __getattr__(self, _nome):
        return lambda *a, **k: self

    def execute(self):
        self.chamadas += 1
        if self.chamadas <= self.falhas:
            raise httpx.RemoteProtocolError("Server disconnected")
        return MagicMock(data=self.dados)


def _cliente(tabela):
    cli = MagicMock()
    cli.table.return_value = tabela
    return cli


class ClientePorThreadTest(unittest.TestCase):
    def setUp(self):
        st._local.cliente = None

    def test_mesma_thread_reaproveita_o_cliente(self):
        with patch("supabase.create_client", side_effect=lambda u, k: object()) as cc:
            self.assertIs(st._sb(), st._sb())
            self.assertEqual(cc.call_count, 1)

    def test_threads_diferentes_nao_compartilham_o_cliente(self):
        vistos = []
        barreira = threading.Barrier(5)

        def trabalho():
            vistos.append(st._sb())
            barreira.wait(timeout=5)  # todas vivas ao mesmo tempo, como no Flask com várias requisições

        with patch("supabase.create_client", side_effect=lambda u, k: object()):
            ts = [threading.Thread(target=trabalho) for _ in range(5)]
            [t.start() for t in ts]
            [t.join() for t in ts]
        self.assertEqual(len({id(c) for c in vistos}), 5)


class RetryTest(unittest.TestCase):
    def setUp(self):
        st._local.cliente = None

    def _rodar(self, tabela, fn):
        with patch.object(st, "_sb", return_value=_cliente(tabela)), patch.object(st.time, "sleep"):
            return fn()

    def test_leitura_repete_e_funciona_na_segunda(self):
        t = _Tabela(falhas=1, dados=[{"id_usuario": "u1", "nome": "Ana", "email": "a@x.com", "senha": "h"}])
        u = self._rodar(t, lambda: st.buscar_usuario_por_email("a@x.com"))
        self.assertEqual(u["id"], "u1")
        self.assertEqual(t.chamadas, 2)

    def test_desiste_depois_de_3_tentativas(self):
        t = _Tabela(falhas=99, dados=[])
        with self.assertRaises(httpx.RemoteProtocolError):
            self._rodar(t, lambda: st.buscar_usuario_por_email("a@x.com"))
        self.assertEqual(t.chamadas, 3)

    def test_insert_nao_repete_sozinho(self):
        t = _Tabela(falhas=1, dados=[])
        with self.assertRaises(httpx.RemoteProtocolError):
            self._rodar(t, lambda: st.criar_token_mobile("u1"))
        self.assertEqual(t.chamadas, 1)

    def test_outro_erro_nao_repete(self):
        class _Quebra(_Tabela):
            def execute(self):
                self.chamadas += 1
                raise ValueError("outro erro")

        t = _Quebra(falhas=0, dados=[])
        with self.assertRaises(ValueError):
            self._rodar(t, lambda: st.buscar_usuario_por_email("a@x.com"))
        self.assertEqual(t.chamadas, 1)

    def test_cliente_e_descartado_ao_repetir(self):
        t = _Tabela(falhas=1, dados=[])
        st._local.cliente = object()
        with patch.object(st, "_sb", return_value=_cliente(t)), patch.object(st.time, "sleep"):
            st.buscar_usuario_por_email("a@x.com")
        self.assertIsNone(st._local.cliente)


if __name__ == "__main__":
    unittest.main()
