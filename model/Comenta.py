from .Connection import Connection

db = Connection()


class Comenta:
    def __init__(self, emailUser, tituloTema, mensaje):
        self.emailUser = emailUser
        self.tituloTema = tituloTema
        self.mensaje = mensaje

    def __str__(self):
        return f"{self.tituloTema} ({self.mensaje})"
