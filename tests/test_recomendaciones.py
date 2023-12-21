import hashlib
import sqlite3
import json
import os
from . import BaseTestClass
from bs4 import BeautifulSoup

#Connection
salt = "library"
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, '..', 'datos.db')

con = sqlite3.connect(db_path)
cur = con.cursor()

#Tests
class TestRecomendaciones(BaseTestClass):

	def test_sinLogin(self):
		cur.execute(f"""DELETE FROM Prestar""")
		con.commit()

		#Obtenemos el renderizado de la página.
		res = self.client.get('/')
		self.assertEqual(200, res.status_code)
		page = BeautifulSoup(res.data, features="html.parser")
		#Comprobamos que no se muestre ni el texto de "Libros recomendados" (no se ha iniciado sesión).
		self.assertIsNone(page.find('h5', class_='card-title'))


	def test_sinLibrosLeidos(self):
		cur.execute(f"""DELETE FROM Prestar""")
		con.commit()
		#Iniciamos sesión para poder llegar al renderizado de recomendaciones.
		#No se comprueba aquí el inicio de sesión puesto que pertenece a otro módulo (test_login.py)
		res = self.login('jhon@gmail.com', '123')
		#Obtenemos el renderizado de la página.
		res = self.client.get('/')
		page = BeautifulSoup(res.data, features="html.parser")
		#Comprobamos que, con los datos insertados a la BD, no haya sugerencias.
		self.assertEqual(0,len(page.find_all('h5', class_='card-title')))


	def test_sinRecomendaciones(self):
		cur.execute(f"""DELETE FROM Prestar""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('jhon@gmail.com', '2', '2023-11-23 12:00:57', '')""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('juan@gmail.com', '6', '2023-11-27 19:32:57', '')""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('juan@gmail.com', '5', '2023-11-27 19:32:57', '')""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('juan@gmail.com', '7', '2023-11-27 19:32:57', '')""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('admin@gmail.com', '8', '2023-11-27 19:32:57', '')""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('admin@gmail.com', '19', '2023-11-27 19:32:57', '')""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('admin@gmail.com', '5', '2023-11-27 19:32:57', '')""")
		con.commit()

		#Comprobamos que se han leido libros
		res = self.db.select(f"SELECT idLibro FROM Prestar WHERE emailUser='jhon@gmail.com'")
		self.assertEqual(1, len(res))

		#Iniciamos sesión para poder llegar al renderizado de recomendaciones.
		#No se comprueba aquí el inicio de sesión puesto que pertenece a otro módulo (test_login.py)
		res = self.login('jhon@gmail.com', '123')
		#Obtenemos el renderizado de la página.
		res = self.client.get('/')
		page = BeautifulSoup(res.data, features="html.parser")
		#Comprobamos que, con los datos insertados a la BD, no haya sugerencias.
		self.assertEqual(0,len(page.find_all('h5', class_='card-title')))


	def test_conRecomendaciones(self):
		#Insertamos datos para que haya recomendaciones
		cur.execute(f"""DELETE FROM Prestar""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('jhon@gmail.com', '2', '2023-11-23 12:00:57', '')""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('juan@gmail.com', '2', '2023-11-27 19:32:57', '')""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('juan@gmail.com', '5', '2023-11-27 19:32:57', '')""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('juan@gmail.com', '7', '2023-11-27 19:32:57', '')""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('admin@gmail.com', '8', '2023-11-27 19:32:57', '')""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('admin@gmail.com', '19', '2023-11-27 19:32:57', '')""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('admin@gmail.com', '2', '2023-11-27 19:32:57', '')""")
		con.commit()

		#Iniciamos sesión para poder llegar al renderizado de recomendaciones.
		#No se comprueba aquí el inicio de sesión puesto que pertenece a otro módulo (test_login.py)
		res = self.login('jhon@gmail.com', '123')
		#Obtenemos el renderizado de la página.
		res = self.client.get('/')
		page = BeautifulSoup(res.data, features="html.parser")
		#Comprobamos que, con los datos insertados a la BD, sean 5 las sugerencias.
		self.assertEqual(5,len(page.find_all('h5', class_='card-title')))


	def test_conRecomendacionesRepetidas(self):
		#El resultado deberían de ser todas las sugerencias sin repetir ninguna, es decir, 3.
		cur.execute(f"""DELETE FROM Prestar""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('jhon@gmail.com', '2', '2023-11-23 12:00:57', '')""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('juan@gmail.com', '2', '2023-11-27 19:32:57', '')""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('juan@gmail.com', '5', '2023-11-27 19:32:57', '')""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('juan@gmail.com', '7', '2023-11-27 19:32:57', '')""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('admin@gmail.com', '5', '2023-11-27 19:32:57', '')""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('admin@gmail.com', '19', '2023-11-27 19:32:57', '')""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('admin@gmail.com', '2', '2023-11-27 19:32:57', '')""")
		con.commit()

		#Iniciamos sesión para poder llegar al renderizado de recomendaciones.
		#No se comprueba aquí el inicio de sesión puesto que pertenece a otro módulo (test_login.py)
		res = self.login('jhon@gmail.com', '123')
		#Obtenemos el renderizado de la página.
		res = self.client.get('/')
		page = BeautifulSoup(res.data, features="html.parser")
		#Comprobamos que, con los datos insertados a la BD, sean 5 las sugerencias.
		self.assertEqual(3,len(page.find_all('h5', class_='card-title')))
	#...



