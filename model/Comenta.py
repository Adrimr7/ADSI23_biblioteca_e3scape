from .Connection import Connection

db = Connection()


class Comenta:
    def __init__(self, emailUser, tituloTema, mensaje):
        self.emailUser = emailUser
        self.tituloTema = tituloTema
        self.mensaje = mensaje
