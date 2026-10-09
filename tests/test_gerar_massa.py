# -*- coding: utf-8 -*-
"""Testes offline do gerador de massa sintética (não acessa o Supabase)."""

import os
import random
import sys
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from faker import Faker

import gerar_massa as g


class GeradorTest(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(1)
        Faker.seed(1)
        self.fake = Faker("pt_BR")
        self.usuarios = g.gerar_usuarios(self.fake, 100, self.rng)
        agora = datetime.now(timezone.utc)
        self.triagens = [[g.gerar_triagem(self.fake, u, self.rng, agora)] for u in self.usuarios]

    def test_minimo_100_registros_unicos(self):
        self.assertGreaterEqual(len(self.usuarios), 100)
        self.assertEqual(len({u["email"] for u in self.usuarios}), 100)

    def test_auditoria_passa(self):
        g.auditar_pii(self.usuarios, self.triagens)

    def test_auditoria_rejeita_email_real(self):
        self.usuarios[0]["email"] = "pessoa.real@gmail.com"
        with self.assertRaises(ValueError):
            g.auditar_pii(self.usuarios, self.triagens)

    def test_auditoria_rejeita_cpf(self):
        self.triagens[0][0]["extra"]["cpf"] = "123"
        with self.assertRaises(ValueError):
            g.auditar_pii(self.usuarios, self.triagens)

    def test_telefone_cabe_em_varchar15(self):
        self.assertTrue(all(len(u["telefone"]) == 15 for u in self.usuarios))

    def test_telefone_usa_ddd_inexistente(self):
        self.assertTrue(all(u["telefone"].startswith("(00) 9") for u in self.usuarios))

    def test_auditoria_rejeita_ddd_real(self):
        self.usuarios[0]["telefone"] = "(62) 99999-9999"
        with self.assertRaises(ValueError):
            g.auditar_pii(self.usuarios, self.triagens)

    def test_nao_ha_senha_fixa_no_codigo(self):
        self.assertFalse(hasattr(g, "SENHA_TESTE"))


if __name__ == "__main__":
    unittest.main()
