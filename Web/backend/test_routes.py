import unittest
import sys
import os

# Garante que o Python encontre o arquivo app.py na pasta atual
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app 

class TestBackendCOE(unittest.TestCase):

    def setUp(self):
        # Cria um cliente de teste do Flask/FastAPI
        app.testing = True
        self.client = app.test_client()

    def test_status_servidor_online(self):
        # Faz uma requisição simulada para a raiz do backend
        response = self.client.get('/')
        # O teste passa se o servidor responder (status 200, 302 ou 404 caso não tenha rota na raiz)
        # O importante é o backend processar a requisição sem dar erro de código 500
        self.assertIn(response.status_code, [200, 302, 404])

if __name__ == '__main__':
    unittest.main()