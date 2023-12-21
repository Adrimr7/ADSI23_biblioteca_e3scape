from .Connection import Connection
from .Author import Author

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
			em = db.select("SELECT * from Author WHERE id=?", (self._author,))[0]
			self._author = Author(em[0], em[1])
		return self._author

	@libro.setter
	def libro(self, value):
		self._libro = value


