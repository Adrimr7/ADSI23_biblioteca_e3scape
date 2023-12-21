from . import BaseTestClass
from bs4 import BeautifulSoup

class TestRecomendaciones(BaseTestClass):

	def test_sinLibrosLeidos(self):
		res = self.client.get('/forum')
		self.assertEqual(200, res.status_code)

	def test_sinRecomendaciones(self):
		self.login('jhon@gmail.com', '123')
		res = self.client.get('/forum')
		self.assertEqual(200, res.status_code)

	def test_conRecomendaciones(self):
		params = {
			'id': "id"
		}
		res = self.client.get('/tema', query_string = params)
		self.assertEqual(200, res.status_code)

	def test_conRecomendacionesRepetidas(self):
		None

	#...



