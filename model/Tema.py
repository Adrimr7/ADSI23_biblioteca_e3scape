from .Connection import Connection
from .User import User

db = Connection()


class Tema:
    def __init__(self, id, title, user_email, description):
        self.id = id
        self.title = title
        self.user = user_email
        self.description = description


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
        return f"{self.title} ({self.description})"
