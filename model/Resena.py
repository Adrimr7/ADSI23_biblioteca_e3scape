from .Connection import Connection
from .Author import Author

db = Connection()

class Resena:
	def __init__(self, emailUser, idLibro, resena, valoracion):
		self.emailUser = emailUser
		self.idLibro = idLibro
		self.resena = resena
		self.valoracion = valoracion

