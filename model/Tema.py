from .Connection import Connection

db = Connection()


class Tema:
    def __init__(self, title, user_email, description):
        self.title = title
        self.user_email = user_email
        self.description = description

    def __str__(self):
        return f"{self.title} ({self.description})"
