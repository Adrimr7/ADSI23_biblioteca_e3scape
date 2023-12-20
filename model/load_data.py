import hashlib
import sqlite3
import json
import os

salt = "library"
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, '..', 'datos.db')

usuarios_path = os.path.join(script_dir, '..', 'usuarios.json')
temas_path = os.path.join(script_dir, '..', 'temas.json')
comentarios_path = os.path.join(script_dir, '..', 'comentarios.json')
amigos_path = os.path.join(script_dir, '..', 'amigos.json')
libros_path = os.path.join(script_dir, '..', 'libros.tsv')
resenas_path = os.path.join(script_dir, '..', 'resenas.json')

con = sqlite3.connect(db_path)
cur = con.cursor()


### Create tables
cur.execute("""
	CREATE TABLE Author(
		id integer primary key AUTOINCREMENT,
		name varchar(40)
	)
""")

cur.execute("""
	CREATE TABLE Book(
		id integer primary key AUTOINCREMENT,
		title varchar(50),
		author integer,
		cover varchar(50),
		description TEXT,
		FOREIGN KEY(author) REFERENCES Author(id)
	)
""")

#cur.execute("""
#	CREATE TABLE User(
#		id integer primary key AUTOINCREMENT,
#		name varchar(20),
#		email varchar(30),
#		password varchar(32)
#	)
#""")

cur.execute("""
	CREATE TABLE User(
		email varchar(30) primary key,
		name varchar(20),
		password varchar(32),
		admin boolean
		
	)
""")

cur.execute("""
	CREATE TABLE Session(
		session_hash varchar(32) primary key,
		user_email varchar(30),
		last_login float,
		FOREIGN KEY(user_email) REFERENCES User(email)
	)
""")

cur.execute("""
	CREATE TABLE Prestar(
		emailUser varchar(30),
		idLibro integer,
		fechaHora datetime,
		fechaFin date,
		PRIMARY KEY(emailUser, idLibro, fechaHora),
		FOREIGN KEY(emailUser) REFERENCES User(email),
		FOREIGN KEY(idLibro) REFERENCES Book(id)
	)
""")

#cur.execute("""
#	CREATE TABLE Tema(
#		titulo varchar(50),
#		emailUser varchar(30),
#		fechaHora datetime,
#		descTema varchar(300),
#		PRIMARY KEY(titulo),
#		FOREIGN KEY(emailUser) REFERENCES User(email)
#	)
#""")

cur.execute("""
	CREATE TABLE Tema(
	    id integer primary key AUTOINCREMENT,
		titulo varchar(50),
		emailUser varchar(30),
		descTema varchar(300),
		FOREIGN KEY(emailUser) REFERENCES User(email)
	)
""")

cur.execute("""
	CREATE TABLE Comenta(
		emailUser varchar(30),
		idTema integer,
		mensaje varchar(300),
		fechaHora datetime,
		PRIMARY KEY(fechaHora, idTema),
		FOREIGN KEY(emailUser) REFERENCES User(email),
		FOREIGN KEY(idTema) REFERENCES Tema(id)
	)
""")

#cur.execute("""
#	CREATE TABLE Comenta(
#		emailUser varchar(30),
#		tituloTema varchar(50),
#		fechaHora datetime,
#		mensaje varchar(300),
#		PRIMARY KEY(emailUser, tituloTema),
#		FOREIGN KEY(emailUser) REFERENCES User(email),
#		FOREIGN KEY(tituloTema) REFERENCES Tema(titulo)
#	)
#""")

cur.execute("""
	CREATE TABLE SonAmigos(
		emailUser1 varchar(30),
		emailUser2 varchar(30),
		PRIMARY KEY(emailUser1, emailUser2),
		FOREIGN KEY(emailUser1) REFERENCES User(email),
		FOREIGN KEY(emailUser1) REFERENCES User(email)
	)
""")

cur.execute("""
	CREATE TABLE Solicita(
		emailUser1 varchar(30),
		emailUser2 varchar(30),
		PRIMARY KEY(emailUser1, emailUser2),
		FOREIGN KEY(emailUser1) REFERENCES User(email),
		FOREIGN KEY(emailUser1) REFERENCES User(email)
	)
""")

cur.execute("""
	CREATE TABLE Reseña(
		emailUser varchar(30),
		idLibro integer,
		resena text,
		valoracion float,
		PRIMARY KEY(emailUser, idLibro),
		FOREIGN KEY(emailUser) REFERENCES User(email),
		FOREIGN KEY(idLibro) REFERENCES Book(id)
	)
""")

### Insert users

with open(usuarios_path, 'r', encoding='utf-8') as f:
	usuarios = json.load(f)['usuarios']

with open(temas_path, 'r', encoding='utf-8') as f:
	temas = json.load(f)['temas']

with open(comentarios_path, 'r', encoding='utf-8') as f:
	comentarios = json.load(f)['comentarios']

with open(amigos_path, 'r', encoding='utf-8') as f:
	amigos = json.load(f)['amigos']

with open(resenas_path, 'r', encoding='utf-8') as f:
	resenas = json.load(f)['resenas']

for user in usuarios:
	dataBase_password = user['password'] + salt
	hashed = hashlib.md5(dataBase_password.encode())
	dataBase_password = hashed.hexdigest()
	cur.execute(f"""INSERT INTO User VALUES ('{user['email']}', '{user['nombres']}', '{dataBase_password}', {user['admin']})""")
	con.commit()

for resena in resenas:
	cur.execute(f"""INSERT INTO Reseña VALUES ('{resena['emailUser']}', '{resena['idLibro']}', '{resena['resena']}', '{resena['valoracion']}')""")
	con.commit()

for tema in temas:
	cur.execute(f"""INSERT INTO Tema VALUES (null, '{tema['titulo']}', '{tema['emailUser']}', '{tema['descTema']}')""")
	con.commit()

for comentario in comentarios:
	cur.execute(f"""INSERT INTO Comenta VALUES ('{comentario['emailUser']}', '{comentario['idTema']}', '{comentario['mensaje']}', '{comentario['fechaHora']}')""")
	con.commit()

#Para cada línea de amigos es necesario primero definir el path, que se define en la línea 13.
for amigo in amigos:
	cur.execute(f"""INSERT INTO SonAmigos VALUES ('{amigo['emailUser1']}', '{amigo['emailUser2']}')""")
	con.commit()


#### Insert books
with open(libros_path, 'r', encoding='utf-8') as f:
	libros = [x.split("\t") for x in f.readlines()]

for author, title, cover, description in libros:
	res = cur.execute(f"SELECT id FROM Author WHERE name=\"{author}\"")
	if res.rowcount == -1:
		cur.execute(f"""INSERT INTO Author VALUES (NULL, \"{author}\")""")
		con.commit()
		res = cur.execute(f"SELECT id FROM Author WHERE name=\"{author}\"")
	author_id = res.fetchone()[0]

	cur.execute("INSERT INTO Book VALUES (NULL, ?, ?, ?, ?)",
		            (title, author_id, cover, description.strip()))

	con.commit()



