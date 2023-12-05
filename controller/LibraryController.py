from model import Connection, Book, User
from model.tools import hash_password

db = Connection()

class LibraryController:
	__instance = None

	def __new__(cls):
		if cls.__instance is None:
			cls.__instance = super(LibraryController, cls).__new__(cls)
			cls.__instance.__initialized = False
		return cls.__instance


	def search_books(self, title="", author="", limit=6, page=0):
		count = db.select("""
				SELECT count() 
				FROM Book b, Author a 
				WHERE b.author=a.id 
					AND b.title LIKE ? 
					AND a.name LIKE ? 
		""", (f"%{title}%", f"%{author}%"))[0][0]
		res = db.select("""
				SELECT b.* 
				FROM Book b, Author a 
				WHERE b.author=a.id 
					AND b.title LIKE ? 
					AND a.name LIKE ? 
				LIMIT ? OFFSET ?
		""", (f"%{title}%", f"%{author}%", limit, limit*page))
		books = [
			Book(b[0],b[1],b[2],b[3],b[4])
			for b in res
		]
		return books, count

	def get_user(self, email, password):
		user = db.select("SELECT * from User WHERE email = ? AND password = ?", (email, hash_password(password)))
		if len(user) > 0:
			return User(user[0][0], user[0][1], user[0][2])
		else:
			return None

	def get_user_cookies(self, token, time):
		user = db.select("SELECT u.* from User u, Session s WHERE u.id = s.user_id AND s.last_login = ? AND s.session_hash = ?", (time, token))
		if len(user) > 0:
			return User(user[0][0], user[0][1], user[0][2])
		else:
			return None
		
	def get_book(self, id):
		book = db.select("SELECT * from Book WHERE id = ?", (id,))
		print(len(book))
		print(book)
		if len(book) > 0:
			return Book(book[0][0],book[0][1],book[0][2],book[0][3],book[0][4])
		else:
			return None
		
	def obtenerRecomendaciones(self, user):
		leidos = self.__getLibrosLeidos(user)
		if leidos == None:
			sugeridos = self.__getLibrosRandom()
			return sugeridos
		else:
			users = self.__getUsuariosHaLeido(leidos)
			if len(users) <= 0:
				sugeridos = self.__getLibrosRandom()
				return sugeridos
			else:
				sugeridos = []
				for u in users:
					sugeridos.extend(self.__getLibrosLeidos(u))
				return sugeridos
			
	
	def __getLibrosLeidos(self, email):
		res = db.select("SELECT * from Prestar WHERE emailUser = ?", (email,))

		if len(res) > 0:
			books = [
			Book(res[0],res[1],res[2],res[3],res[4])
			for b in res
		]
			return books
		else:
			return None
		
	def __getUsuariosHaLeido(self, books):
		users = []
		i = 0
		for b in books:
			res = db.select("SELECT emailUser from Prestar WHERE idLibro = ?", (b.id,))
			if len(res)>0:
				users.append(res[0][i])
			i += 1
		
		return users
	
	"""
	Este método se pensó para hacer inmersion respecto a uno supeior.
	El superior recibe un único usuario.
	Este recibo una lista de usuario.
	Debido a que no se especifica en la cabecera el tipo, se ha descartado el desarrollo.
	Solución: por cada usuario se llama al método de arriba
	
	def __getLibrosLeidos(self, users):
		leidos = []
		i = 0
		for u in users:
			res = db.select("SELECT * from Prestar WHERE emailUser = ?", (u[i].email,))

			if len(res) > 0:
				for b in res:
					leidos.append(Book(res[0],res[1],res[2],res[3],res[4]))
			i += 1
		return leidos
	"""
		
	
	def __getLibrosRandom(self):
		return None
		
