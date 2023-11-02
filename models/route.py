from utils.db import db


class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    ip_loopback = db.Column(db.String(100))
    ip_admin = db.Column(db.String(100))
    rol = db.Column(db.String(100))
    empresa = db.Column(db.String(100))
    sitema = db.Column(db.String(100))
    ligas = db.Column(db.String(100))

    def __init__(self, nombre, ip_loopback, ip_admin, rol, empresa, sitema, ligas):
        self.nombre = nombre
        self.ip_loopback = ip_loopback
        self.ip_admin = ip_admin
        self.rol = rol
        self.empresa = empresa
        self.sitema = sitema
        self.ligas = ligas