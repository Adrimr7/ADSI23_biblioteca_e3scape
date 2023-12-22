import os
import sqlite3
from . import BaseTestClass
from bs4 import BeautifulSoup


#Connection
salt = "library"
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, '..', 'datos.db')

con = sqlite3.connect(db_path)
cur = con.cursor()
class TestCatalogo(BaseTestClass):
	
	def test_resenasNoLogged(self):
		#Intento de acceder a reseñas sin estar loggeado
		res = self.client.get('/resenas')
		#Redirecciona a home
		self.assertEqual(302, res.status_code)

	def test_resenasLogged(self):
		#Intento de acceder a reseñas estando ya loggeado
		self.login('jhon@gmail.com','123')
		res = self.client.get('/resenas')
		#Se accede a la página correctamente
		self.assertEqual(200, res.status_code)

	def test_noResenas(self):
		self.login('jhon@gmail.com', '123')
		res = self.client.get('/resenas')
		self.assertEqual(200, res.status_code)
		#Comprobar que no tiene reseñas escritas
		cur.execute(f"""DELETE FROM Reseña""")
		con.commit()
		res = self.db.select(f"SELECT * FROM Reseña WHERE emailUser='jhon@gmail.com'")
		self.assertEqual(0, len(res))
		# Mirar con el BeautifulSoup para ver cuantas reseñas hay en el html
		res = self.client.get('/resenas')
		page = BeautifulSoup(res.data, features="html.parser")
		self.assertEqual(0, len(page.find('div', class_='row').find_all('div', class_='card')))

	def test_conResenas(self):
		self.login('jhon@gmail.com', '123')
		res = self.client.get('/resenas')
		self.assertEqual(200, res.status_code)
		# Comprobar que tiene reseñas escritas
		cur.execute(f"""DELETE FROM Reseña""")
		con.commit()
		cur.execute(f"""INSERT INTO Reseña VALUES ('jhon@gmail.com', '6', 'muy recomendable para fans de la fantasia', '8.85')""")
		con.commit()
		cur.execute(f"""INSERT INTO Reseña VALUES ('jhon@gmail.com', '5', 'es un libro vomitivo', '1.1')""")
		con.commit()
		res = self.db.select(f"SELECT * FROM Reseña WHERE emailUser='jhon@gmail.com'")
		self.assertEqual(2, len(res))
		#Mirar con el BeautifulSoup para ver cuantas reseñas hay en el html
		res = self.client.get('/resenas')
		page = BeautifulSoup(res.data, features="html.parser")
		self.assertEqual(2, len(page.find('div', class_='row').find_all('div', class_='card')))


	def test_anadirResena(self):
		self.login('jhon@gmail.com', '123')
		res = self.client.get('/resenas')
		self.assertEqual(200, res.status_code)
		cur.execute(f"""DELETE FROM Reseña""")
		con.commit()
		cur.execute(f"""INSERT INTO Reseña VALUES ('jhon@gmail.com', '6', 'muy recomendable para fans de la fantasia', '8.85')""")
		con.commit()
		cur.execute(f"""INSERT INTO Reseña VALUES ('jhon@gmail.com', '5', 'es un libro vomitivo', '1.1')""")
		con.commit()
		res = self.db.select(f"SELECT * FROM Reseña WHERE emailUser='jhon@gmail.com'")
		self.assertEqual(2, len(res))
		#Anadimos una reseña extra
		cur.execute(f"""INSERT INTO Reseña VALUES ('jhon@gmail.com', '10', 'ok', '5.0')""")
		con.commit()
		res = self.db.select(f"SELECT * FROM Reseña WHERE emailUser='jhon@gmail.com'")
		self.assertEqual(3, len(res))
		cur.execute(f"""INSERT INTO Reseña VALUES ('jhon@gmail.com', '11', 'not ok', '2.0')""")
		con.commit()
		cur.execute(f"""INSERT INTO Reseña VALUES ('jhon@gmail.com', '12', 'okkk', '9.0')""")
		con.commit()
		res = self.db.select(f"SELECT * FROM Reseña WHERE emailUser='jhon@gmail.com'")
		self.assertEqual(5, len(res))

	def test_eliminarResena(self):
		self.login('jhon@gmail.com', '123')
		res = self.client.get('/resenas')
		self.assertEqual(200, res.status_code)
		# Comprobar que tiene reseñas escritas
		cur.execute(f"""DELETE FROM Reseña""")
		con.commit()
		cur.execute(f"""INSERT INTO Reseña VALUES ('jhon@gmail.com', '6', 'muy recomendable para fans de la fantasia', '8.85')""")
		con.commit()
		cur.execute(f"""INSERT INTO Reseña VALUES ('jhon@gmail.com', '5', 'es un libro vomitivo', '1.1')""")
		con.commit()
		res = self.db.select(f"SELECT * FROM Reseña WHERE emailUser='jhon@gmail.com'")
		self.assertEqual(2, len(res))
		cur.execute(f"""DELETE FROM Reseña WHERE idLibro = '5' """)
		con.commit()
		res = self.db.select(f"SELECT * FROM Reseña WHERE emailUser='jhon@gmail.com'")
		self.assertEqual(1, len(res))
	def test_verResenaEnConcreto(self):
		self.login('jhon@gmail.com', '123')
		res = self.client.get('/resenas')
		self.assertEqual(200, res.status_code)
		cur.execute(f"""DELETE FROM Reseña""")
		con.commit()
		cur.execute(f"""INSERT INTO Reseña VALUES ('jhon@gmail.com', '5', 'es un libro vomitivo', '1.1')""")
		con.commit()
		params = {
			'resena': "vomitivo"
		}
		params2 = {
			'valoracion': "1.1"
		}
		res = self.client.get('/resenas', query_string=params)
		page = BeautifulSoup(res.data, features="html.parser")
		self.assertEqual(1, len(page.find('div', class_='row').find_all('div', class_='card')))
		for card in page.find('div', class_='row').find_all('div', class_='card'):
			self.assertIn(params['resena'].lower(), card.find(class_='card-text').get_text().lower())
			self.assertIn(params2['valoracion'].lower(), card.find(class_='card-text2').get_text().lower())


	def test_editarResena(self):
		self.login('jhon@gmail.com', '123')
		res = self.client.get('/resenas')
		self.assertEqual(200, res.status_code)
		cur.execute(f"""DELETE FROM Reseña""")
		con.commit()
		cur.execute(f"""INSERT INTO Reseña VALUES ('jhon@gmail.com', '5', 'es un libro vomitivo', '1.1')""")
		con.commit()
		res = self.db.select(f"SELECT * FROM Reseña WHERE emailUser='jhon@gmail.com'")
		self.assertEqual(1, len(res))
		res = self.client.get('/editarResena')
		self.assertEqual(200, res.status_code)
		page = BeautifulSoup(res.data, features="html.parser")
		self.assertIsNotNone(page.find('form').find('input', type='text'))
		self.assertIsNotNone(page.find('form').find('input', type='number'))
		self.assertIsNotNone(page.find('form').find('button', type='submit'))
		cur.execute(f"""UPDATE Reseña SET resena = 'no tan malo' WHERE idLibro = '5' AND emailUser = 'jhon@gmail.com'""")
		con.commit()
		#Ahora pasamos a mirar que la resena haya cambiado en el html con el BeautifulSoup
		res = self.client.get('/resenas')
		self.assertEqual(200, res.status_code)
		params = {
			'resena': "no tan malo"
		}
		page = BeautifulSoup(res.data, features="html.parser")
		self.assertEqual(1, len(page.find('div', class_='row').find_all('div', class_='card')))
		for card in page.find('div', class_='row').find_all('div', class_='card'):
			self.assertIn(params['resena'].lower(), card.find(class_='card-text').get_text().lower())





