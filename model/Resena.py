from .Connection import Connection
from .Author import Author

db = Connection()

class Resena:
	def __init__(self, emailUser, idLibro, reseña, valoracion):
		self.emailUser = emailUser
		self.idLibro = idLibro
		self.reseña = reseña
		self.valoracion = valoracion

