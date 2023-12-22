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

	def test_editarResena(self):
		self.login('jhon@gmail.com', '123')
		res = self.client.get('/resenas')
		self.assertEqual(200, res.status_code)
		cur.execute(f"""DELETE FROM Reseña""")
		con.commit()
		cur.execute(f"""INSERT INTO Reseña VALUES ('jhon@gmail.com', '6', 'muy recomendable para fans de la fantasia', '8.85')""")
		con.commit()


	def test_cancelarEditResena(self):
		pass



