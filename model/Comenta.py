from .Connection import Connection
from .Tema import Tema
from .User import User

db = Connection()


class Comenta:
    def __init__(self, emailUser, idTema, mensaje, fechaHora):
        self.user = emailUser
        self.tema = idTema
        self.mensaje = mensaje
        self.fechaHora = fechaHora

    @property
    def tema(self):
        if type(self._tema) == int:
            t = db.select("SELECT * FROM Tema WHERE id = ?", (self._tema,))[0]
            self._tema = Tema(t[0], t[1], t[2], t[3])
        return self._tema

    @tema.setter
    def tema(self, value):
        self._tema = value

    @property
    def user(self):
        if type(self._user) == str:
            t = db.select("SELECT * FROM User WHERE email = ?", (self._user,))[0]
            self._user = User(t[0], t[1], t[3])
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    def __str__(self):
        return f"{self.tema.title} ({self.mensaje})"
