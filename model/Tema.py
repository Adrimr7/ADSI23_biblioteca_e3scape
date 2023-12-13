from .Connection import Connection

db = Connection()


class Tema:
    def __init__(self, title, description):
        self.title = title
        self.description = description

    def __str__(self):
        return f"{self.title} ({self.description})"
