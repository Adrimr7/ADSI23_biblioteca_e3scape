from .LibraryController import LibraryController
from flask import Flask, render_template, request, make_response, redirect

app = Flask(__name__, static_url_path='', static_folder='../view/static', template_folder='../view/')


library = LibraryController()


@app.before_request
def get_logged_user():
	if '/css' not in request.path and '/js' not in request.path:
		print("Entra a get_loggedUser")
		token = request.cookies.get('token')
		time = request.cookies.get('time')
		if token and time:
			print("Entra a get_loggedUser, IF1")
			request.user = library.get_user_cookies(token, float(time))
			if request.user:
				print("Entra a get_loggedUser, IF2")
				request.user.token = token


@app.after_request
def add_cookies(response):
	if 'user' in dir(request) and request.user and request.user.token:
		session = request.user.validate_session(request.user.token)
		response.set_cookie('token', session.hash)
		response.set_cookie('time', str(session.time))
	return response


@app.route('/')
def index():
	if 'user' in dir(request) and request.user and request.user.token:
		recomendaciones = library.obtenerRecomendaciones(request.user.email)
		booksRec = []
		if recomendaciones != None:
			for book in recomendaciones:
				booksRec.append(library.get_book(book))
		return render_template('index.html', recomendaciones=booksRec)
	else:
		return render_template('index.html')


@app.route('/catalogue')
def catalogue():
	title = request.values.get("title", "")
	author = request.values.get("author", "")
	page = int(request.values.get("page", 1))
	books, nb_books = library.search_books(title=title, author=author, page=page - 1)
	total_pages = (nb_books // 6) + 1
	return render_template('catalogue.html', books=books, title=title, author=author, current_page=page,
	                       total_pages=total_pages, max=max, min=min)

@app.route('/book')
def book():
	id = request.values.get("id", "")
	book = library.get_book(id)
	return render_template('book.html', book=book)

@app.route('/forum')
def forum():
	temas = library.get_temas()
	return render_template('forum.html', temas=temas)

@app.route('/tema')
def tema():
	id = request.values.get("id", "")
	#print(id)
	if id != "":
		comentarios = library.get_comentarios(id)

		return render_template('tema.html', comentarios=comentarios, id = id)
	return redirect('/forum')

@app.route('/nuevoTema', methods=['GET', 'POST'])
def nuevoTema():
	if 'user' in dir(request) and request.user and request.user.token:
		if request.method == 'POST':
			titulo = request.form['titulo']
			descripcion = request.form['descripcion']
			if titulo == "" :
				return redirect('/')

			library.nuevoTema(titulo, descripcion, request.user.email)
			return redirect('/forum')
		return render_template('nuevoTema.html', )
	return redirect('/')

@app.route('/nuevoComentario', methods=['GET', 'POST'])
def nuevoComentario():
	if 'user' in dir(request) and request.user and request.user.token:
		if request.method == 'POST':
			comentario = request.form['comentario']
			id = request.values.get("id", "")
			print("id en nuevoComentario " + str(id))
			if comentario == "" :
				return redirect('/')

			library.nuevoComentario(comentario, request.user.email, id)
			return redirect('/forum')
		return render_template('nuevoComentario.html', )
	return redirect('/')


#@app.route('/login', methods=['GET', 'POST'])
#def login():
#	if 'user' in dir(request) and request.user and request.user.token:
#		return redirect('/')
#	email = request.values.get("email", "")
#	print(email)
#	password = request.values.get("password", "")
#	print(password)
#	user = library.get_user(email, password)
#	print(user)
#	if user:
#		print(user.email)
#		print("MailLogin")
#		session = user.new_session()
#		resp = redirect("/")
#		resp.set_cookie('token', session.hash)
#		resp.set_cookie('time', str(session.time))
#	else:
#		if request.method == 'POST':
#			return redirect('/login')
#		else:
#			resp = render_template('login.html')
#	return resp

@app.route('/resena')
def resena():
	id = request.values.get("id", "")
	resena, libro = library.getResena(id, request.user.email)
	return render_template('resena.html', book = libro, resena = resena)

@app.route('/resenas')
def resenas():
	email = request.user.email
	resenas = library.get_resenas(email)
	return render_template('resenas.html', resenas=resenas)

@app.route('/amigos')
def amigos():
	email = request.values.get("email", "")
	amigos = library.get_amigos(email)
	return render_template('amigos.html', amigos=amigos)

@app.route('/admin')
def admin():
	#Comprobamos si el usuario ha iniciado sesion
	if 'user' in dir(request) and request.user and request.user.token:
		email = request.user.email
		print("-----")
		print(email)
		admin = library.esAdmin(email)
		if admin:
				return render_template('admin.html')
	return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
	if 'user' in dir(request) and request.user and request.user.token:
		return redirect('/')
	email = request.values.get("email", "")
	print(email)
	password = request.values.get("password", "")
	print(password)
	user = library.get_user(email, password)
	print(user)
	if user:
		print(user.email)
		print("MailLogin")
		session = user.new_session()
		resp = redirect("/")
		resp.set_cookie('token', session.hash)
		resp.set_cookie('time', str(session.time))
	else:
		if request.method == 'POST':
			return redirect('/login')
		else:
			resp = render_template('login.html')
	return resp


@app.route('/logout')
def logout():
	path = request.values.get("path", "/")
	resp = redirect(path)
	resp.delete_cookie('token')
	resp.delete_cookie('time')
	if 'user' in dir(request) and request.user and request.user.token:
		request.user.delete_session(request.user.token)
		request.user = None
	return resp
