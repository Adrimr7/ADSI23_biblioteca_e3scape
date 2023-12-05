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
		leidos = None #self.__getLibrosLeidos(user)
		if leidos == None:
			return None
		else:
			return None
	
	def __getLibrosLeidos(self, email):
		res = db.select("SELECT * from Prestar WHERE emailUser = ?", (email))

		if len(books) > 0:
			books = [
			Book(res[0],res[1],res[2],res[3],res[4])
			for b in res
		]
			return books
		else:
			return None
		
	def __getUsuariosHaLeido(idLibro):
		return None
		
