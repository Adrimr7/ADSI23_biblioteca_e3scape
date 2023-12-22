from . import BaseTestClass
from bs4 import BeautifulSoup
import sqlite3
import os


#Connection
salt = "library"
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, '..', 'datos.db')

con = sqlite3.connect(db_path)
cur = con.cursor()

class TestForo(BaseTestClass):

	def test_foroSinRegistro(self):
		res = self.client.get('/forum')
		self.assertEqual(200, res.status_code)

	def test_foroConRegistro(self):
		self.login('jhon@gmail.com', '123')
		res = self.client.get('/forum')
		self.assertEqual(200, res.status_code)

	def test_temaInexistente(self):
		cur.execute(f"""DELETE FROM Tema""")
		con.commit()
		cur.execute(f"""DELETE FROM Comenta""")
		con.commit()

		params = {
			'id': "id"
		}
		res = self.client.get('/tema', query_string = params)
		#print("test_temaInexistente status code : " + str(res.status_code))
		self.assertEqual(302, res.status_code)
		self.assertEqual('/', res.location)

		params = {
			'id': "30"
		}
		res = self.client.get('/tema', query_string=params)
		# print("test_temaInexistente status code : " + str(res.status_code))
		self.assertEqual(302, res.status_code)
		self.assertEqual('/', res.location)

	def test_temaExiste(self):
		cur.execute(f"""DELETE FROM Tema""")
		con.commit()
		cur.execute(f"""DELETE FROM Comenta""")
		con.commit()

		cur.execute(f"""INSERT INTO Tema VALUES ('10', 'TemaTest', 'jhon@gmail.com', 'En efecto, esto es un test')""")
		con.commit()
		cur.execute(f"""INSERT INTO Comenta VALUES ('jhon@gmail.com', '10', 'Comentario', '2023-12-09 10:30:24')""")
		con.commit()

		params = {
			'id': "10"
		}
		res = self.client.get('/tema', query_string = params)
		self.assertEqual(200, res.status_code)

		page = BeautifulSoup(res.data, features="html.parser")
		#Solo deberia haber un comentario
		self.assertEqual(1, len(page.find('div', class_='row').find_all('div', class_='card')))

	def test_crearTemaEstandoLogeado(self):
		cur.execute(f"""DELETE FROM Tema""")
		con.commit()
		cur.execute(f"""DELETE FROM Comenta""")
		con.commit()

		#Entramos a crear tema
		self.login('jhon@gmail.com', '123')
		res = self.client.get('/nuevoTema')
		self.assertEqual(200, res.status_code)

		#Creamos el tema
		cur.execute(f"""INSERT INTO Tema VALUES ('9', 'TemaTest', 'jhon@gmail.com', 'En efecto, esto es un test')""")
		con.commit()

		#Vamos a ver la pagina del tema que acabamos de crear
		res = self.client.get('/forum')
		self.assertEqual(200, res.status_code)

		page = BeautifulSoup(res.data, features="html.parser")

		print("Hacemos el test : " + str(len(page.find_all('a', class_='card-title'))))
		self.assertEqual(1, len(page.find_all('a', class_='card-title')))

		self.assertEqual('TemaTest', page.find('div', class_='card-deck').find('div', class_="card").get_text())


		#params = {
		#	'id': "2"
		#}
		#res = self.client.get('/tema', query_string=params)
		#self.assertEqual(200, res.status_code)
#
		#page = BeautifulSoup(res.data, features="html.parser")
		#self.assertEqual('Jhon Doe', page.find('header').find('ul').find_all('li')[-2].get_text())

	def test_crearTemaSinLogear(self):
		# entrar a crear foro -> redirige a /
		res = self.client.get('/nuevoTema')
		self.assertEqual(302, res.status_code)
		self.assertEqual('/', res.location)



	def test_crearComentarioEstandoLogeado(self):
		#logear -> entrar a comentar en un tema -> comentar -> comprobar en el tema
		pass

	def test_crearComentarioSinLogear(self):
		#entrar a comentar en un tema -> redirige a /
		pass