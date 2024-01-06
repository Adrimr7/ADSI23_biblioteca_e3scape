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

class TestReserva(BaseTestClass):

	def test_entrarAHistorialReservas(self):
		self.login('jhon@gmail.com', '123')
		res = self.client.get('/reserva')
		self.assertEqual(200, res.status_code)


	def test_IntentarReservarSinRegistrarse(self):
		res = self.client.get('/book?id=2')
		page = BeautifulSoup(res.data, features="html.parser")
		self.assertEqual(2, len(page.find_all('button', attrs={"type": "submit", "class": "btn btn-primary"})))


	def test_ReservarLibro(self):
		cur.execute(f"""DELETE FROM Prestar""")
		con.commit()
		self.login('jhon@gmail.com', '123')
		#Vamos a reservar el libro con id 2
		res = self.client.get('/book?id=2')
		page = BeautifulSoup(res.data, features="html.parser")
		self.assertEqual(1, len(page.find_all('button', attrs={"name": "reservar"})))
		#Simulamos que hemos reservado el libro
		cur.execute(f"""INSERT INTO Prestar (emailUser, idLibro, fechaHora, fechaFin) VALUES ('jhon@gmail.com', '2', '2024-01-06 15:45:30', NULL)""")
		con.commit()
		res2 = self.client.get('/reserva')
		reserva = BeautifulSoup(res2.data, features="html.parser")
		self.assertEqual(3,len(reserva.find_all(class_='card-text')))

	def test_DevolverLibro(self):
		cur.execute(f"""DELETE FROM Prestar""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('jhon@gmail.com', '4', '2027-04-13 15:00:57', NULL)""")
		con.commit()
		self.login('jhon@gmail.com', '123')
		res = self.client.get('/book?id=4')
		page = BeautifulSoup(res.data, features="html.parser")
		self.assertEqual(1, len(page.find_all('button', attrs={"name": "devolver"})))
		cur.execute("""UPDATE Prestar SET fechaFin = '2027-05-14' WHERE idLibro = 4 AND emailUser ='jhon@gmail.com' AND fechaHora = '2027-04-13 15:00:57'""")
		con.commit()
		res2 = self.client.get('/reserva')
		reserva = BeautifulSoup(res2.data, features="html.parser")
		self.assertEqual(1,len(reserva.find_all(class_='card-title')))

	def test_LibroSeDevuelveTrasPasarPlazo(self):
		cur.execute(f"""DELETE FROM Prestar""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('jhon@gmail.com', '4', '2022-04-13 15:00:57', NULL)""")
		con.commit()
		self.login('jhon@gmail.com', '123')
		res = self.client.get('/book?id=4')
		page = BeautifulSoup(res.data, features="html.parser")
		#Debería de haberse devuelto al haber comparado las fechas
		self.assertEqual(1, len(page.find_all('button', attrs={"name": "reservar"})))
		resultados = self.db.select(f"""SELECT * FROM Prestar WHERE idLibro = '4' AND emailUser = 'jhon@gmail.com' AND fechaHora = '2022-04-13 15:00:57' AND fechaFin IS NOT NULL""")
		self.assertEqual(4, len(resultados[0]))

	def test_IntentarHacerOEditarReseñaTrasDevolverLibro(self):
		cur.execute(f"""DELETE FROM Prestar""")
		con.commit()
		cur.execute(f"""INSERT INTO Prestar VALUES ('jhon@gmail.com', '4', '2022-04-13 15:00:57', NULL)""")
		con.commit()
		self.login('jhon@gmail.com', '123')
		res = self.client.get('/book?id=4')
		page = BeautifulSoup(res.data, features="html.parser")
		#Debería de haberse devuelto al haber comparado las fechas
		self.assertEqual(1, len(page.find_all('button', attrs={"id": "editResena"})))


