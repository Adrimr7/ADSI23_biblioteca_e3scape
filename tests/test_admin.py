import hashlib
import sqlite3
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
class TestAdmin(BaseTestClass):
    def testAccederSinLogear(self):
        #Pre: Tratamos de acceder a la pestaña de administrador sin habernos loggeado
        #Post: No nos deja acceder y redirije a "/"
        res = self.client.get('/admin')
        #Redirige a la pagina de inicio
        self.assertEqual('/',res.location)

    def testAccederSinAdmin(self):
        #Pre: Tratamos de acceder con una cuenta sin ser admin
        #Post: No nos deja acceder y redirije a "/"
        self.login('jhon@gmail.com', '123')
        res = self.client.get('/admin')
        #Redirige a la pagina de inicio
        self.assertEqual('/',res.location)

    def testAnadirUsuario(self):
        #Pre:Intentaremos añadir un usuario sin introducir datos erroneos o "raros"
        #Post: Añade al usuario
        self.login('admin@gmail.com', 'admin')
        self.client.get('/admin')
        cur.execute(f"""DELETE FROM User WHERE email = 'test@test.com' """)
        con.commit()
        cur.execute(f"""SELECT * FROM User WHERE email = 'test@test.com' """)

        #Comprobamos que no esta el usuario creado
        res = cur.fetchall()
        self.assertEqual(len(res), 0)

        #Creamos la cuenta
        self.client.post('/admin', data=dict(accion1=1, email='test@test.com', nombre='test', contrasena='123', admin='off'), follow_redirects=True)
        cur.execute(f"""SELECT * FROM User WHERE email = 'test@test.com' """)
        res = cur.fetchall()

        #Vemos que los campos coinciden
        self.assertEqual(res[0][0], 'test@test.com')
        self.assertEqual(res[0][1], 'test')
        self.assertEqual(res[0][2], '8afc382a91e7bc1703abe0dd0d560b2a') #Clave hasheada
        self.assertEqual(res[0][3], 0)

    def testAnadirUsuarioConCorreoYaExistente(self):
        #Pre: Intentaremos añadir un usuario que ya existe.
        #Post: No lo añade
        self.login('admin@gmail.com', 'admin')
        self.client.get('/admin')
        cur.execute(f"""DELETE FROM User WHERE email = 'test@test.com' """)
        con.commit()

        self.client.post('/admin', data=dict(accion1=1, email='test@test.com', nombre='test', contrasena='123', admin='off'), follow_redirects=True)
        self.client.post('/admin', data=dict(accion1=1, email='test@test.com', nombre='test2', contrasena='1234', admin='on'), follow_redirects=True)
        cur.execute(f"""SELECT * FROM User WHERE email = 'test@test.com' """)
        res = cur.fetchall()
        #Solo hay una cuenta
        self.assertEqual(len(res), 1)
        #y es la primera
        self.assertEqual(res[0][1], 'test')

    def testAnadirUsuarioConCorreoFalso(self):
        #Pre: Intentaremos añadir un usuario con un correo erroneo/falso
        #Post: crea la cuenta
        self.login('admin@gmail.com', 'admin')
        self.client.get('/admin')
        cur.execute(f"""DELETE FROM User WHERE email = 'test@test.com' """)
        con.commit()
        cur.execute(f"""DELETE FROM User WHERE email = 'testcorreofalso' """)
        con.commit()

        self.client.post('/admin', data=dict(accion1=1, email='testcorreofalso', nombre='test', contrasena='123', admin='off'), follow_redirects=True)
        cur.execute(f"""SELECT * FROM User WHERE email = 'testcorreofalso' """)
        res = cur.fetchall()
        #La cuenta no se añade porque el correo no cumple el estandar (Falta el @ y el .com,.es...)
        self.assertEqual(len(res), 0)

    def testAnadirLibroConAutorInexistente(self):
        #Pre: Intentaremos añadir un libro con un nombre de autor que no existe
        #Post: Añade el libro y el autor
        self.login('admin@gmail.com', 'admin')
        self.client.get('/admin')
        cur.execute(f"""DELETE FROM Book WHERE title = 'LibroTestAdmin' """)
        con.commit()
        cur.execute(f"""DELETE FROM Author WHERE name = 'AutorTest' """)
        con.commit()

        #EL LIBRO NO EXISTE
        cur.execute(f"""SELECT * FROM Book WHERE title = 'LibroTestAdmin' """)
        res = cur.fetchall()
        self.assertEqual(len(res), 0)

        #EL AUTOR NO EXISTE
        cur.execute(f"""SELECT * FROM Author WHERE name = 'AutorTest' """)
        res = cur.fetchall()
        self.assertEqual(len(res), 0)
        #Creamos un libro con el nombre

        self.client.post('/admin', data=dict(accion3=3, titulo='LibroTestAdmin', autor='AutorTest',ncop=2, desc='descTest', portada='url'), follow_redirects=True)

        #Comprobamos la creacion del libro y del autor
        cur.execute(f"""SELECT * FROM Book WHERE title = 'LibroTestAdmin' """)
        res = cur.fetchall()
        cur.execute(f"""SELECT * FROM Author WHERE name = 'AutorTest' """)
        res2 = cur.fetchall()
        self.assertEqual(res[0][1], 'LibroTestAdmin')
        self.assertEqual(res[0][2], res2[0][0])
        self.assertEqual(res[0][3], 'url')
        self.assertEqual(res[0][4], 'descTest')

    def testAnadirLibroConAutorExistente(self):
        #Pre: Intentaremos añadir un libro a un autor ya existente
        #Post: Añade un libro y le pone la id del autor sin volver a crear el autor
        self.login('admin@gmail.com', 'admin')
        self.client.get('/admin')
        #Borramos para que no este trampeado
        cur.execute(f"""DELETE FROM Book WHERE title = 'LibroTestAdmin' """)
        con.commit()
        cur.execute(f"""DELETE FROM Author WHERE name = 'AutorExistente' """)
        con.commit()

        #EL LIBRO NO EXISTE
        cur.execute(f"""SELECT * FROM Book WHERE title = 'LibroTestAdmin' """)
        res = cur.fetchall()
        self.assertEqual(len(res), 0)

        #Añadimos a la base de datos el autor
        cur.execute(f"""INSERT INTO AUTHOR (name) VALUES ('AutorExistente')""")
        con.commit()
        cur.execute(f"""SELECT * FROM Author WHERE name = 'AutorExistente' """)
        res = cur.fetchall()
        self.assertEqual(res[0][1], 'AutorExistente')
        #Guardamos su id
        id_autor=res[0][0]

        self.client.post('/admin', data=dict(accion3=3, titulo='LibroTestAdmin', autor='AutorExistente',ncop=2, desc='descTest', portada='url'), follow_redirects=True)

        #Comprobamos que la id del autor del libro es la del autor existente
        cur.execute(f"""SELECT * FROM Book WHERE title = 'LibroTestAdmin' """)
        res = cur.fetchall()
        self.assertEqual(res[0][2], id_autor)

        #Comprobamos que NO se ha vuelto a añadir el autor
        cur.execute(f"""SELECT * FROM Author WHERE name = 'AutorExistente' """)
        res = cur.fetchall()
        self.assertEqual(len(res), 1)

    def testAnadirLibroRellenandoNumeroCopiasMal(self):
        #Pre: Introducimos letras por ejemplo en el campo de numero de copias
        #Post: No se añade el libro
        self.login('admin@gmail.com', 'admin')
        self.client.get('/admin')
        cur.execute(f"""DELETE FROM Book WHERE title = 'LibroTestAdmin' """)
        con.commit()

        self.client.post('/admin',data=dict(accion3=3, titulo='LibroTestAdmin', autor='AutorExistente', ncop='Letras', desc='descTest',portada='url'), follow_redirects=True)

        #Vemos que el libro no se añade
        cur.execute(f"""SELECT * FROM Book WHERE title = 'LibroTestAdmin' """)
        res = cur.fetchall()
        self.assertEqual(len(res), 0)



    def testAnadirLibroYaExistente(self):
        #Pre: Añadimos un libro a un autor, pero ese mismo autor ya tiene ese mismo libro asociado
        #Post: No se añade el libro porque ya existe
        cur.execute(f"""DELETE FROM Book WHERE title = 'LibroTestAdmin' """)
        con.commit()
        cur.execute(f"""DELETE FROM Author WHERE name = 'AutorExistente' """)
        con.commit()
        cur.execute(f"""INSERT INTO AUTHOR (name) VALUES ('AutorExistente')""")
        con.commit()
        cur.execute(f"""SELECT id FROM Author WHERE name = 'AutorExistente' """)
        id_autor = cur.fetchall()[0][0]
        cur.execute("INSERT INTO Book (title,author,cover,description) VALUES (?,?,?,?)",('LibroTestAdmin',id_autor,'url','descLibroExistente'))
        con.commit()
        cur.execute(f"""SELECT * FROM Book WHERE title = 'LibroTestAdmin' """)
        res = cur.fetchall()
        #Solo hay 1 libro
        self.assertEqual(len(res), 1)

        self.client.post('/admin', data=dict(accion3=3, titulo='LibroTestAdmin', autor='AutorExistente',ncop=2, desc='descTest', portada='url'), follow_redirects=True)

        cur.execute(f"""SELECT * FROM Book WHERE title = 'LibroTestAdmin' """)
        res = cur.fetchall()
        #Sigue habiendo solo 1 libro
        self.assertEqual(len(res), 1)
        #Y ese libro es el que ya existia de antes
        #Solo hay 1 libro
        self.assertEqual(res[0][4], 'descLibroExistente')