from model import Connection, Book, User, Tema, Resena, Comenta
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
		""", (f"%{title}%", f"%{author}%", limit, limit * page))
        books = [
            Book(b[0], b[1], b[2], b[3], b[4])
            for b in res
        ]
        return books, count

    def get_temas(self):

        res = db.select("""
				SELECT t.* 
				FROM Tema t
		""")
        temas = []
        for t in res:
            temas.append(Tema(t[0], t[1], t[2], t[3]))
        return temas

    def nuevoTema(self, titulo, descripcion, email):
        db.insert("INSERT INTO Tema (titulo, emailUser, descTema) VALUES (?, ?, ?)", (titulo, email, descripcion))

    def nuevoComentario(self, comentario, email, idTema):
        print("id en Libray " + str(idTema))
        db.insert("INSERT INTO Comenta (mensaje, emailUser, idTema, fechaHora) VALUES (?, ?, ?, datetime('now'))", (comentario, email, idTema))


    def get_comentarios(self, idTema):

        res = db.select("SELECT * FROM Comenta WHERE idTema = ? ORDER BY fechaHora", (idTema,))

        comentarios = []
        print(comentarios)
        for t in res:
            comentarios.append(Comenta(t[0], t[1], t[2], t[3]))
        return comentarios

    def get_user(self, email, password):
        user = db.select("SELECT * from User WHERE email = ? AND password = ?", (email, hash_password(password)))
        if len(user) > 0:
            return User(user[0][0], user[0][1], user[0][3])
        else:
            return None

    def get_user_cookies(self, token, time):
        user = db.select(
            "SELECT u.* from User u, Session s WHERE s.last_login = ? AND s.session_hash = ? AND u.email = s.user_email",
            (time, token,))
        if len(user) > 0:
            return User(user[0][0], user[0][1], user[0][3])
        else:
            return None

    def get_book(self, id):
        book = db.select("SELECT * from Book WHERE id = ?", (id,))
        if len(book) > 0:
            return Book(book[0][0], book[0][1], book[0][2], book[0][3], book[0][4])
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
                    sugeridos.extend(self.__getLibrosLeidos(u[0]))
                return sugeridos

    def __getLibrosLeidos(self, email):
        print(email)
        res = db.select("SELECT * from Prestar WHERE emailUser LIKE ?", (email,))
        
        if len(res) > 0:
            books = []
            for i in res:
                books.append(i[1])
            return books
        else:
            return None

    def get_resenas(self, email):

        res = db.select("SELECT * from Reseña WHERE emailUser = ?", (email,))
        resenas = []
        for r in res:
            resenas.append(Resena(r[0], r[1], r[2], r[3]))
        return resenas

    def getResena(self, idLibro, email):
        res = db.select("SELECT * from Reseña WHERE idLibro = ? AND emailUser = ?", (idLibro, email))
        lib = db.select("SELECT * from Book WHERE id = ?", (idLibro,))

        if len(res) > 0 and len(lib) > 0:
            resena = Resena(res[0][0], res[0][1], res[0][2], res[0][3])
            libro = Book(lib[0][0], lib[0][1], lib[0][2], lib[0][3], lib[0][4])
            return (resena, libro)

        else:
            return None

    def __getUsuariosHaLeido(self, books):
        users = []
        i = 0
        for b in books:
            res = db.select("SELECT emailUser from Prestar WHERE idLibro = ?", (b,))
            if len(res) > 0:
                for userRead in res:
                    users.append(userRead)
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

    def get_amigos(self, email):
        selectAmigos = db.select("SELECT * from SonAmigos WHERE emailUser1 = ? OR emailuser2 = ?", (email, email))
        amigos = []
        for amistad in selectAmigos:
            if amistad[0] == email:
                amigos.append(amistad[1])
            else:
                amigos.append(amistad[0])
        return amigos

    def get_nombreuser(self, email):
        selectNombre = db.select("SELECT name from User WHERE emailUser = ?", (email))
        return selectNombre


    def esAdmin(self, email):
        es = db.select("SELECT admin from USER WHERE email = ?", (email,))
        if es[0][0] == 0:
            return False
        else:
            return True