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

        # si ahora añadimos un amigo a admin, deberia de tener 1, asi que se comprueba

        cur.execute(f"""INSERT INTO SonAmigos VALUES ('admin@gmail.com','juan@gmail.com')""")
        con.commit()
        res = self.client.get('/verAmigos')
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(1, len(page.find_all('h5', class_='card-title')))

        # añadimos otro amigo, en la posicion contraria de la BD

        cur.execute(f"""INSERT INTO SonAmigos VALUES ('jhon@gmail.com','admin@gmail.com')""")
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

        # Para JUAN tienen que haber TRES libros que haya leido (3)

        res = self.client.post('/verAmigos', data=dict(emailUsuario='juan@gmail.com'), follow_redirects=True)
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(3, len(page.find_all('h5', class_='card-title')))

    #def testSolicitarAmigo(self):
        #Hacer una solicitud a un amigo

    #def testGestionarSolicitudes(self):
        #Aceptar o rechazar las solicitudes

