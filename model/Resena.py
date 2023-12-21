from .Connection import Connection
from .Book import Book

db = Connection()

class Resena:
	def __init__(self, emailUser, idLibro, resena, valoracion):
		self.emailUser = emailUser
		self.libro = idLibro
		self.resena = resena
		self.valoracion = valoracion

	@property
	def libro(self):
		if type(self._libro) == int:
			b = db.select("SELECT * from Book WHERE id=?", (self._libro,))[0]
			self._libro = Book(b[0], b[1], b[2], b[3], b[4])
		return self._libro

	@libro.setter
	def libro(self, value):
		self._libro = value


