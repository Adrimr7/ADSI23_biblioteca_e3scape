from .LibraryController import LibraryController
from flask import Flask, render_template, request, make_response, redirect, url_for

app = Flask(__name__, static_url_path='', static_folder='../view/static', template_folder='../view/')

library = LibraryController()


@app.before_request
def get_logged_user():
    # Comprobado que funciona
    if '/css' not in request.path and '/js' not in request.path:
        token = request.cookies.get('token')
        time = request.cookies.get('time')
        if token and time:
            request.user = library.get_user_cookies(token, float(time))
            if request.user:
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
        return render_template('index.html', recomendaciones=recomendaciones)
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


@app.route('/book', methods=['GET','POST'])
def book():
    id = request.values.get("id", "")
    book = library.get_book(id)
    prestado = None
    recien = False
    if 'user' in dir(request) and request.user and request.user.token:
        prestado = library.isOnLoan(request.user.email, id)
        if 'reservar' in request.form:
            library.reservarLibro(request.user.email, id)
            prestado=True
        if 'devolver' in request.form or library.seHaAcabadoElTiempo(request.user.email, id):
            library.devolverLibro(request.user.email, id)
            recien = True
            prestado=False
    return render_template('book.html', book=book, prestado=prestado, recien=recien)


@app.route('/forum')
def forum():
    temas = library.get_temas()
    return render_template('forum.html', temas=temas)


@app.route('/tema')
def tema():
    id = request.values.get("id", "")
    # print(id)
    if id != "":
        tema = library.get_tema(id)

        if tema == 0:
            return redirect('/')
        comentarios = library.get_comentarios(id)

        return render_template('tema.html', comentarios=comentarios, tema=tema)
    return redirect('/forum')


@app.route('/nuevoTema', methods=['GET', 'POST'])
def nuevoTema():
    if 'user' in dir(request) and request.user and request.user.token:
        if request.method == 'POST':
            titulo = request.form['titulo']
            descripcion = request.form['descripcion']
            if titulo == "":
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
            if comentario == "":
                return redirect('/')

            library.nuevoComentario(comentario, request.user.email, id)
            return redirect('/forum')
        return render_template('nuevoComentario.html', )
    return redirect('/')


@app.route('/editarResena', methods=['GET', 'POST'])
def editarResena():
    if 'user' in dir(request) and request.user and request.user.token:
        if request.method == 'POST':
            id = request.values.get("id", "")
            resena = request.form['resena']
            if resena == "":
                resena = library.getResena(id, request.user.email).resena
            valoracion = request.form['valoracion']
            try:
                float(valoracion)
            except (ValueError, TypeError):
                valoracion = -1

            if valoracion == -1:
                valoracion = library.getResena(id, request.user.email).valoracion
            if valoracion < 0:
                valoracion = 0
            if valoracion > 10:
                valoracion = 10
            if resena == "":
                return redirect('/resenas')

            library.editarResena(resena, request.user.email, id, valoracion)
            return redirect('/resenas')
        return render_template('editarResena.html', )
    return redirect('/')


# @app.route('/login', methods=['GET', 'POST'])
# def login():
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
    if 'user' in dir(request) and request.user and request.user.token:
        id = request.values.get("idLibro", "")
        resena = library.getResena(id, request.user.email)
        return render_template('resena.html', resena=resena)
    return redirect("/")


@app.route('/resenas')
def resenas():
    if 'user' in dir(request) and request.user and request.user.token:
        email = request.user.email
        resenas = library.get_resenas(email)
        return render_template('resenas.html', resenas=resenas)
    return redirect("/")


@app.route('/amigos', methods=['GET', 'POST'])
def amigos():
    if 'user' in dir(request) and request.user and request.user.token:
        if request.method == 'POST':
            emailUsuario = request.user.email
            emailSolicitud = request.form['solicitarAmigo']
            estaBien = library.enviarSolicitud(emailUsuario, emailSolicitud)
            if estaBien:
                return redirect('/amigos')
        return render_template('amigos.html')
    return redirect('/')


@app.route('/solicitudes', methods=['GET', 'POST'])
def solicitudes():
    if 'user' in dir(request) and request.user and request.user.token:
        email = request.user.email
        if request.method == 'POST':
            emailSolicitud = request.form.get('EmailSolicitud')
            if 'aceptar' in request.form:
                library.aceptarSolicitud(email, emailSolicitud)
            elif 'rechazar' in request.form:
                library.rechazarSolicitud(email, emailSolicitud)
        solicitudes = library.getSolicitudes(email)
        return render_template('solicitudes.html', solicitudes=solicitudes)
    return redirect('/')


@app.route('/verAmigos', methods=['GET', 'POST'])
def verAmigos():
    if 'user' in dir(request) and request.user and request.user.token:
        if request.method == 'POST':
            return redirect(url_for('verPerfil', emailUsuario=request.form.get('emailUsuario')))
        else:
            email = request.user.email
            amigos = library.get_amigos(email)
            usuario = request.user.username
            return render_template('verAmigos.html', amigos=amigos, usuario=usuario)
    return redirect('/')


@app.route('/verPerfil', methods=['GET', 'POST'])
def verPerfil():
    if 'user' in dir(request) and request.user and request.user.token:
        emailUsuario = request.args.get('emailUsuario')
        print(emailUsuario)
        datos = library.obtenerDatosPerfil(emailUsuario)
        return render_template('verPerfil.html', nomUsuario=datos[0], emailUsuario=datos[1], libros=datos[2])
    return redirect('/')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Comprobamos si el usuario ha iniciado sesion
    if 'user' in dir(request) and request.user and request.user.token:
        if request.method == 'POST':
            # Comprobamos que formulario se ha activado
            accion1 = request.form.get('accion1')  # Registrar usuario
            accion2 = request.form.get('accion2')  # Eliminar usuario
            accion3 = request.form.get('accion3')  # Anadir Libro
            if accion1 is not None:
                email = request.form.get('email')
                nombre = request.form.get('nombre')
                contrasena = request.form.get('contrasena')
                admin = request.form.get("admin")
                completado = library.nuevo_usuario(email, nombre, contrasena, admin)
            elif accion2 is not None:
                emaile = request.form.get('emaile')
                emailpropio = request.user.email
                completado = library.eliminar_usuario(emaile,emailpropio)

            elif accion3 is not None:
                titulo = request.form.get('titulo')
                autor = request.form.get('autor')
                ncop = request.form.get('ncop')
                desc = request.form.get('desc')
                url_portada = request.form.get('portada')
                completado = library.nuevo_libro(titulo, autor, ncop, desc, url_portada)
        email = request.user.email
        admin = library.esAdmin(email)
        if admin:
            return render_template('admin.html')
    return redirect("/")

@app.route('/reserva')
def reserva():
    datos = library.getReserva(request.user.email)

    return render_template('reserva.html', reservas=datos)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in dir(request) and request.user and request.user.token:
        return redirect('/')
    email = request.values.get("email", "")
    # print(email)
    password = request.values.get("password", "")
    # print(password)
    user = library.get_user(email, password)
    # print(user)
    if user:
        # print(user.email)
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
