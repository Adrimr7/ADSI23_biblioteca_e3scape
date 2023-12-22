from . import BaseTestClass
from bs4 import BeautifulSoup

class TestCatalogo(BaseTestClass):
	
	def test_resenasNoLogged(self):
		res = self.client.get('/resenas')
		self.assertEqual(302, res.status_code)



	def test_resenasLogged(self):
		self.login('jhon@gmail.com','123')
		res = self.client.get('/resenas')
		self.assertEqual(200, res.status_code)

	def test_noResenas(self):
		pass


	def test_conResenas(self):
		pass

	def test_editarResena(self):
		pass

	def test_cancelarEditResena(self):
		pass



