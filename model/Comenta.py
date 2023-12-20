from .Connection import Connection

db = Connection()


class Comenta:
    def __init__(self, emailUser, tituloTema, mensaje, fechaHora):
        self.emailUser = emailUser
        self.tituloTema = tituloTema
        self.mensaje = mensaje
        self.fechaHora = fechaHora

    def __str__(self):
        return f"{self.tituloTema} ({self.mensaje})"
