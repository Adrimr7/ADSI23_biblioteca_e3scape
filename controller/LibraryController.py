import hashlib

from model import Connection, Book, User, Tema, Resena, Comenta
from model.tools import hash_password
import re

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

    def get_tema(self, id):

        try:
            id = int(id)
        except (ValueError, TypeError):
            id = -1

        if (id == -1):
            return 0

        id = str(id)

        t = db.select(" SELECT * FROM Tema WHERE id = ?", (id,))

        tema = 0
        if (len(t) > 0):
            tema = Tema(t[0][0], t[0][1], t[0][2], t[0][3])

        return tema

    def nuevoTema(self, titulo, descripcion, email):
        db.insert("INSERT INTO Tema (titulo, emailUser, descTema) VALUES (?, ?, ?)", (titulo, email, descripcion))

    def nuevoComentario(self, comentario, email, idTema):
        db.insert("INSERT INTO Comenta (mensaje, emailUser, idTema, fechaHora) VALUES (?, ?, ?, datetime('now'))",
                  (comentario, email, idTema))

    def editarResena(self, resena, email, idLibro, valoracion):
        db.update("UPDATE Reseña SET valoracion = ?, resena = ? WHERE idLibro = ? AND emailUser = ?",
                  (valoracion, resena, idLibro, email))

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
        print(type(id))
        book = db.select("SELECT * from Book WHERE id = ?", (id,))
        if len(book) > 0:
            return Book(book[0][0], book[0][1], book[0][2], book[0][3], book[0][4])
        else:
            return None

    def obtenerRecomendaciones(self, user):
        leidos = self.__getLibrosLeidos(user)
        if leidos == None:
            sugeridos = self.__getLibrosRandom(user)
            return sugeridos
        else:
            users = self.__getUsuariosHaLeido(leidos, user)
            if len(users) <= 0:
                sugeridos = self.__getLibrosRandom(user)
                return sugeridos
            else:
                sugeridos = []
                for u in users:
                    sugeridos.extend(self.__getLibrosLeidos(u.email))
                sugeridosNoR = self.__deleteRepeated(leidos, sugeridos)

                """
                Si hay pocas sugerencias, se puede añadir las top 10

                if len(sugeridosNoR)<10:
                    sugeridosNoR.extend(self.__getLibrosRandom(user))
                sugeridosCom = self.__deleteRepeated(leidos,sugeridosNoR)
                return sugeridosCom
                
                """

                return sugeridosNoR

    def __getLibrosLeidos(self, email):
        res = db.select("SELECT * from Prestar WHERE emailUser LIKE ?", (email,))
        if len(res) > 0:
            books = []
            for i in res:
                res2 = db.select("SELECT * from Book WHERE id = ?", (i[1],))
                books.append(Book(res2[0][0], res2[0][1], res2[0][2], res2[0][3], res2[0][4]))
            return books
        else:
            return None

    def __deleteRepeated(self, leidos, sugeridos):
        if len(leidos) > 0 and len(sugeridos) > 0:
            res = []
            for i in sugeridos:
                if not self.__isRead(leidos, i.id) and not self.__isRead(res, i.id):
                    res.append(i)

            return res
        else:
            return None

    def __isRead(self, leidos, id):
        found = False
        i = 0
        while not found and i < len(leidos):
            if leidos[i].id == id:
                found = True
            else:
                i += 1
        return found

    def get_resenas(self, email):

        res = db.select("SELECT * from Reseña WHERE emailUser = ?", (email,))
        resenas = []
        for r in res:
            resenas.append(Resena(r[0], r[1], r[2], r[3]))
        return resenas

    def getResena(self, idLibro, email):
        res = db.select("SELECT * from Reseña WHERE idLibro = ? AND emailUser = ?", (idLibro, email))

        if len(res) > 0:
            resena = Resena(res[0][0], res[0][1], res[0][2], res[0][3])
            return resena
        else:
            return None

    def __getUsuariosHaLeido(self, books, email):
        users = []
        i = 0
        for b in books:
            res = db.select("SELECT emailUser from Prestar WHERE idLibro = ? AND emailUser NOT LIKE ?", (b.id, email,))
            if len(res) > 0:
                for userRead in res:
                    res2 = db.select("SELECT * from User WHERE email = ?", (userRead[0],))
                    users.append(User(userRead[0], res2[0][1], res2[0][3]))
            i += 1
        return users

    def isOnLoan(self, email, id):
        res = db.select("SELECT * FROM Prestar WHERE emailUser LIKE ? AND idLibro = ? AND fechaFin =''", (email, id,))
        if len(res) > 0:
            return True
        else:
            return False

    def __getLibrosRandom(self, user):
        res = db.select("SELECT idLibro,COUNT(idLibro) FROM Prestar GROUP BY idLibro ORDER BY COUNT(idLibro) DESC")
        if len(res) > 0:
            books = []
            count = 0
            while count < 10 and count < len(res):
                res2 = db.select("SELECT * from Book WHERE id = ?", (res[count][0],))
                if not self.isOnLoan(user, res[count][0]):
                    books.append(Book(res2[0][0], res2[0][1], res2[0][2], res2[0][3], res2[0][4]))
                count += 1
            return books
        else:
            return None

    def get_amigos(self, email):
        selectAmigos = db.select("SELECT * from SonAmigos WHERE emailUser1 = ? OR emailuser2 = ?", (email, email))
        amigos = []
        for amistad in selectAmigos:
            if amistad[1] is not None:
                if amistad[0] == email:
                    amigos.append(amistad[1])
                else:
                    amigos.append(amistad[0])
        return amigos

    def get_nombreuser(self, email):
        selectNombre = db.select("SELECT name from User WHERE email = ?", (email,))
        mail = selectNombre[0][0]
        return mail

    def getSolicitudes(self, email):
        selectSolicitudes = db.select("SELECT * from solicita WHERE emailUser2 = ?", (email,))
        listaSolic = []
        for solicitud in selectSolicitudes:
            listaSolic.append(solicitud[0])
        return listaSolic

    def enviarSolicitud(self, emailUsuario, emailObjetivo):
        patronEmail = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{1,3}$'
        bien = False
        if re.match(patronEmail, emailObjetivo):
            solicitudes = db.select("SELECT emailUser1 from solicita WHERE emailUser2= ?", (emailObjetivo,))
            if not solicitudes:
                db.insert("INSERT INTO solicita VALUES (?,?)", (emailUsuario, emailObjetivo))
                bien = True
        return bien

    def rechazarSolicitud(self, emailUsuario, emailSolicitud):
        db.delete("DELETE FROM solicita WHERE emailUser1 = ? AND emailUser2 = ?", (emailSolicitud, emailUsuario))

    def aceptarSolicitud(self, emailUsuario, emailSolicitud):
        db.insert("INSERT INTO SonAmigos VALUES (?,?)", (emailUsuario, emailSolicitud))
        self.rechazarSolicitud(emailUsuario, emailSolicitud)

    def obtenerDatosPerfil(self, emailUsuario):
        libros = self.__getLibrosLeidos(emailUsuario)
        if libros is None:
            libros = []
        print(self.get_nombreuser(emailUsuario), emailUsuario, libros)
        return [self.get_nombreuser(emailUsuario), emailUsuario, libros]

    def esAdmin(self, email):
        es = db.select("SELECT admin from USER WHERE email = ?", (email,))
        if es[0][0] == 0:
            return False
        else:
            return True

    def validar_email(self, email):
        patron_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        regex = re.compile(patron_email)
        if regex.match(email):
            return True
        else:
            return False

    def es_numero(self,num):
        patron_numero = re.compile(r'^[-+]?\d*\.?\d+$')
        return bool(patron_numero.match(num))

    def nuevo_usuario(self, email, nombre, contrasena, admin):
        #Comprobamos que los campos esten rellenados y el regex del email
        if admin == 'on':
            esUnAdmin = 1
        else:
            esUnAdmin = 0
        if self.validar_email(email):
            if nombre is not None:
                if contrasena is not None:
                    #Comprobar que no hay una persona registrada con ese correo
                    existe = db.select("SELECT * from USER WHERE email = ?", (email,))
                    if len(existe) == 0:
                        #Se añade un nuevo usuario a la bd
                        salt = "library"
                        claveSalteada = contrasena + salt
                        hashed = hashlib.md5(claveSalteada.encode())
                        claveSalteada = hashed.hexdigest()
                        db.insert("INSERT INTO USER VALUES (?,?,?,?)", (email,nombre,claveSalteada,esUnAdmin))
                        return True
        return False

    def nuevo_libro(self,titulo,autor,ncop,desc,portada):
        #comproinamos que los campos esten rellenados
        if self.es_numero(ncop):
            if desc is not None:
                #comprobaciones de autor
                existe_au = db.select("SELECT id from AUTHOR WHERE name = ?", (autor,))
                if len(existe_au) > 0:
                    #Comprobamos que el mismo autor no tenga ya un libro con ese nombre
                    idAutor = existe_au[0][0]
                    existe_lib = db.select("SELECT * from BOOK WHERE title = ? AND author = ?", (titulo,idAutor,))
                    #Si ya existe el libro se devuelve false y no se añade nada
                    if len(existe_lib) > 0:
                        #El autor ya tiene un libro con ese nombre -> El libro ya esta en el catalogo
                        return False
                else:
                    db.insert("INSERT INTO AUTHOR (name) VALUES (?)", (autor,))
                    Autor = db.select("SELECT id from AUTHOR WHERE name = ?", (autor,))
                    idAutor = Autor[0][0]
                #Se añade el libro
                #AÑADIENDO LIBRO CON LOS CAMPOS ACTUALES (Falta la parte de Sergio)
                db.insert("INSERT INTO BOOK (title,author,cover,description) VALUES (?,?,?,?)", (titulo,idAutor,portada,desc,))
                return False
            return False
        return False

    def eliminar_usuario(self,emailElim,emailProp):
        #Comprobamos que un admin no se este eliminando a si mismo
        if emailElim == emailProp:
            print("coincide")
            return False
        else:
            print("no coincide")
            print(emailElim)
            #Comprobamos que existe la persona que se va a eliminar
            existe = db.select("SELECT * FROM User WHERE email = ?", (emailElim,))
            print(existe[0][0])
            if len(existe) > 0:
                print("existe")
                #Se procede a eliminar tod.o lo relacionado con el usuario en la base de datos
                #Primero los temas y comentarios
                db.update("UPDATE Tema SET emailUser = 'deleted@user.com' WHERE emailUser = ?", (emailElim,))
                db.update("UPDATE Comenta SET emailUser = 'deleted@user.com' WHERE emailUser = ?", (emailElim,))
                #Eliminamos reseñas
                db.update("UPDATE Reseña SET emailUser = 'deleted@user.com' WHERE emailUser = ?", (emailElim,))
                #Eliminamos amigos
                db.delete("DELETE FROM SonAmigos WHERE emailUser1 = ? OR emailUser2 = ?", (emailElim,emailElim))
                #eliminamos libros prestados
                db.delete("DELETE FROM Prestar WHERE emailUser = ?", (emailElim,))
                #Eliminamos al usuario
                db.delete("DELETE FROM user WHERE email = ?", (emailElim,))
                return True
            return False