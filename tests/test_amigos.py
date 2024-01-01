import os
import sqlite3

from . import BaseTestClass
from bs4 import BeautifulSoup

salt = "library"
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, '..', 'datos.db')

con = sqlite3.connect(db_path)
cur = con.cursor()


class TestAmigos(BaseTestClass):
    def testVerListaAmigos(self):
        # Acceder a Lista de Amigos
        cur.execute(f"""DELETE FROM SonAmigos""")
        con.commit()
        # Logearse (admin por ejemplo) y comprobar en /verAmigos si admin no tiene amigos.
        res = self.login('admin@gmail.com', 'admin')
        res = self.client.get('/verAmigos')
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(0, len(page.find_all('h5', class_='card-title')))

        # Si ahora añadimos un amigo a admin, deberia de tener 1, asi que se comprueba

        cur.execute(f"""INSERT INTO SonAmigos VALUES ('admin@gmail.com','juan@gmail.com')""")
        con.commit()
        res = self.client.get('/verAmigos')
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(1, len(page.find_all('h5', class_='card-title')))

        # Añadimos otro amigo, en la posicion contraria de la BD

        cur.execute(f"""INSERT INTO SonAmigos VALUES ('jhon@gmail.com','admin@gmail.com')""")
        con.commit()
        res = self.client.get('/verAmigos')
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(2, len(page.find_all('h5', class_='card-title')))

        # Si se añade un amigo que no existe, no se deberia de añadir
        cur.execute(f"""INSERT INTO SonAmigos VALUES ('jhon@gmail.com','usuarioinventado@gmail.com')""")
        con.commit()
        res = self.client.get('/verAmigos')
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(2, len(page.find_all('h5', class_='card-title')))

    def testVerPerfil(self):
        # Ver el perfil de un amigo
        # Primero se añaden los datos
        cur.execute(f"""DELETE FROM SonAmigos""")
        con.commit()
        cur.execute(f"""INSERT INTO SonAmigos VALUES ('admin@gmail.com','juan@gmail.com')""")
        con.commit()
        cur.execute(f"""INSERT INTO SonAmigos VALUES ('jhon@gmail.com','admin@gmail.com')""")
        con.commit()
        cur.execute(f"""INSERT INTO SonAmigos VALUES ('amigojhon@gmail.com','admin@gmail.com')""")
        con.commit()
        cur.execute(f"""DELETE FROM Prestar""")
        con.commit()
        cur.execute(f"""INSERT INTO Prestar VALUES ('jhon@gmail.com', '2', '2023-11-23 12:00:57', '')""")
        con.commit()
        cur.execute(f"""INSERT INTO Prestar VALUES ('juan@gmail.com', '2', '2023-11-27 19:32:57', '')""")
        con.commit()
        cur.execute(f"""INSERT INTO Prestar VALUES ('juan@gmail.com', '5', '2023-11-27 19:32:57', '')""")
        con.commit()
        cur.execute(f"""INSERT INTO Prestar VALUES ('juan@gmail.com', '7', '2023-11-27 19:32:57', '')""")
        con.commit()
        cur.execute(f"""INSERT INTO Prestar VALUES ('admin@gmail.com', '5', '2023-11-27 19:32:57', '')""")
        con.commit()
        cur.execute(f"""INSERT INTO Prestar VALUES ('admin@gmail.com', '2', '2023-11-27 19:32:57', '')""")
        con.commit()
        res = self.login('admin@gmail.com', 'admin')

        # Para JHON tiene que haber UN libro que haya leido (1)

        res = self.client.post('/verAmigos', data=dict(emailUsuario='jhon@gmail.com'), follow_redirects=True)
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(1, len(page.find_all('h5', class_='card-title')))
        # Aqui comprobamos que efectivamente el usuario es el que dice ser, en este caso Jhon
        nombre_usuario = page.find_all('h3')[0].text.strip()
        self.assertEqual('Perfil de Jhon Doe', nombre_usuario)

        # Para JUAN tienen que haber TRES libros que haya leido (3)

        res = self.client.post('/verAmigos', data=dict(emailUsuario='juan@gmail.com'), follow_redirects=True)
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(3, len(page.find_all('h5', class_='card-title')))
        # Aqui comprobamos que efectivamente el usuario es el que dice ser, en este caso Juan
        nombre_usuario = page.find_all('h3')[0].text.strip()
        self.assertEqual('Perfil de Juan Ejemplo', nombre_usuario)

        # Para AMIGOJHON no tiene que haber ningún libro (0)

        res = self.client.post('/verAmigos', data=dict(emailUsuario='amigojhon@gmail.com'), follow_redirects=True)
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(0, len(page.find_all('h5', class_='card-title')))
        # Aqui comprobamos que efectivamente el usuario es el que dice ser, en este caso AmigoJhon
        nombre_usuario = page.find_all('h3')[0].text.strip()
        self.assertEqual('Perfil de Amigo Jhon', nombre_usuario)

    def testSolicitarAmigo(self):
        # Primero se añaden los datos
        cur.execute(f"""DELETE FROM SonAmigos""")
        con.commit()
        cur.execute(f"""INSERT INTO SonAmigos VALUES ('admin@gmail.com','juan@gmail.com')""")
        con.commit()
        cur.execute(f"""DELETE FROM Solicita""")
        con.commit()

        # Ahora mismo JHON y ADMIN no son amigos. Por tanto, si ADMIN solicita a JHON de amigo, veremos que tiene uno.
        res = self.login('admin@gmail.com', 'admin')
        res = self.client.post('/amigos', data=dict(solicitarAmigo='jhon@gmail.com'), follow_redirects=True)

        self.client.get('/logout', follow_redirects=True)

        res = self.client.post('/login', data=dict(email='jhon@gmail.com', password='123'), follow_redirects=True)
        res = self.client.get('/solicitudes')

        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(1, len(page.find_all('h5', class_='card-title')))

        # Si se borran las solicitudes, no habra ninguna
        cur.execute(f"""DELETE FROM Solicita""")
        con.commit()

        res = self.client.get('/solicitudes')
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(0, len(page.find_all('h5', class_='card-title')))

    def testGestionarSolicitudes(self):
        # Aceptar o rechazar las solicitudes
        # Para ello primero se añaden los datos correspondientes
        cur.execute(f"""DELETE FROM SonAmigos""")
        con.commit()
        cur.execute(f"""DELETE FROM Solicita""")
        con.commit()
        cur.execute(f"""INSERT INTO Solicita VALUES ('admin@gmail.com','jhon@gmail.com')""")
        con.commit()
        cur.execute(f"""INSERT INTO Solicita VALUES ('amigojhon@gmail.com','jhon@gmail.com')""")
        con.commit()
        # Ahora tiene que haber 2 solicitudes para JHON, por tanto si entramos en solicitudes tiene que haber dos
        # cajas para poder gestionar la solicitud
        res = self.login('jhon@gmail.com', '123')
        res = self.client.get('/solicitudes')
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(2, len(page.find_all('h5', class_='card-title')))
        # Lo siguiente es comprobar que al rechazar una solicitud, esos dos usuarios no son amigos, utilizando la misma
        # lógica que en el primer test

        res = self.client.post('/solicitudes', data=dict(EmailSolicitud='admin@gmail.com', rechazar=''), follow_redirects=True)
        res = self.client.get('/verAmigos')
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(0, len(page.find_all('h5', class_='card-title')))

        # Ademas de comprobar que no se ha añadido, hay que ver que en solicita se haya rechazado, esto es,
        # ver si no está en solicitudes, como en el paso anterior.
        res = self.client.get('/solicitudes')
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(1, len(page.find_all('h5', class_='card-title')))

        # Ahora comprobamos aceptando una solicitud, y despues se comprueba tambien que se haya quitado de las
        # solicitudes
        res = self.client.post('/solicitudes', data=dict(EmailSolicitud='amigojhon@gmail.com', aceptar=''), follow_redirects=True)
        res = self.client.get('/verAmigos')
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(1, len(page.find_all('h5', class_='card-title')))

        # Ademas de comprobar que no se ha añadido, hay que ver que en solicita se haya aceptado, esto es,
        # ver si no está en solicitudes, como en el paso anterior.
        res = self.client.get('/solicitudes')
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(0, len(page.find_all('h5', class_='card-title')))
