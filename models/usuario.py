from utils.db import db


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    permisos = db.Column(db.String(100))
    dispositivos = db.Column(db.String(100))

    def __init__(self, nombre, permisos, dispositivos):
        self.nombre = nombre
        self.permisos = permisos
        self.dispositivos = dispositivos