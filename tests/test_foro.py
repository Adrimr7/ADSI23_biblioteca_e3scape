from . import BaseTestClass
from bs4 import BeautifulSoup

class TestForo(BaseTestClass):

	def test_foroSinRegistro(self):
		res = self.client.get('/forum')
		self.assertEqual(200, res.status_code)

	def test_foroConRegistro(self):
		self.login('jhon@gmail.com', '123')
		res = self.client.get('/forum')
		self.assertEqual(200, res.status_code)

	def test_temaInexistente(self):
		params = {
			'id': "id"
		}
		res = self.client.get('/tema', query_string = params)
		self.assertEqual(200, res.status_code)



