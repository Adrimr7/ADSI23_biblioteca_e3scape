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
		#print("test_temaInexistente status code : " + str(res.status_code))
		self.assertEqual(302, res.status_code)

	def test_temaExiste(self):
		params = {
			'id': "2"
		}
		res = self.client.get('/tema', query_string = params)
		self.assertEqual(200, res.status_code)

		page = BeautifulSoup(res.data, features="html.parser")
		#Solo deberia haber un comentario
		self.assertEqual(1, len(page.find('div', class_='row').find_all('div', class_='card')))

	def test_crearTemaEstandoLogeado(self):
		self.login('jhon@gmail.com', '123')
		pass

	def test_crearTemaSinLogear(self):
		# entrar a crear foro -> redirige a /
		pass

	def test_crearComentarioEstandoLogeado(self):
		#logear -> entrar a comentar en un tema -> comentar -> comprobar en el tema
		pass

	def test_crearComentarioSinLogear(self):
		#entrar a comentar en un tema -> redirige a /
		pass