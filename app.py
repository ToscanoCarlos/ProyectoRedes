from flask import Flask, url_for, jsonify, request, render_template
from utils.db import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:12345@localhost/redesdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa Flask-SQLAlchemy


class ValidaError(ValueError):
    pass

class Router(db.Model):
    __tablename__ = 'routers'
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(64), unique=True)
    loopback = db.Column(db.String(120))
    admin_ip = db.Column(db.String(120))
    rol = db.Column(db.String(64))
    empresa = db.Column(db.String(64))
    so = db.Column(db.String(64))

    def dame_url(self):
        return url_for('get_router_by_hostname', hostname=self.hostname, _external=True)

    def exporta_datos(self):
        return {
            'url': self.dame_url(),
            'hostname': self.hostname,
            'loopback': self.loopback,
            'admin_ip': self.admin_ip,
            'rol': self.rol,
            'empresa': self.empresa,
            'so': self.so
        }

    def importa_datos(self, datos):
        try:
            self.hostname = datos['hostname']
            self.loopback = datos['loopback']
            self.admin_ip = datos['admin_ip']
            self.rol = datos['rol']
            self.empresa = datos['empresa']
            self.so = datos['so']
        except KeyError as e:
            raise ValidaError('Router inválido: falta ' + e.args[0])
        return self

class Interface(db.Model):
    __tablename__ = 'interfaces'
    id = db.Column(db.Integer, primary_key=True)
    router_id = db.Column(db.Integer, db.ForeignKey('routers.id'))
    tipo = db.Column(db.String(64))
    numero = db.Column(db.String(64))
    ip = db.Column(db.String(120))
    mascara = db.Column(db.String(120))
    estado = db.Column(db.String(64))
    router_conectado = db.Column(db.String(64))

    def exporta_datos(self):
        return {
            'tipo': self.tipo,
            'numero': self.numero,
            'ip': self.ip,
            'mascara': self.mascara,
            'estado': self.estado,
            'router_conectado': self.router_conectado
        }

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    permisos = db.Column(db.String(100))
    dispositivos = db.Column(db.String(100))

    def exporta_datos(self):
        return {
            'nombre': self.nombre,
            'permisos': self.permisos,
            'dispositivos': self.dispositivos
        }

    def importa_datos(self, datos):
        try:
            self.nombre = datos['nombre']
            self.permisos = datos['permisos']
            self.dispositivos = datos['dispositivos']
        except KeyError as e:
            raise ValidaError('Usuario inválido: falta ' + e.args[0])
        return self

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/usuarios')
def usuarios():
    return render_template('usuarios.html')

@app.route('/topologia')
def topologia():
    return render_template('topologia.html')

@app.route('/routes')
def routes():
    return render_template('routes.html')

@app.route('/routers', methods=['GET'])
def get_all_routers():
    routers = Router.query.all()
    return jsonify({'routers': [router.exporta_datos() for router in routers]})

@app.route('/routers/<string:hostname>', methods=['GET'])
def get_router_by_hostname(hostname):
    router = Router.query.filter_by(hostname=hostname).first_or_404()
    return jsonify(router.exporta_datos())

@app.route('/routers/<string:hostname>/interfaces', methods=['GET'])
def get_router_interfaces(hostname):
    router = Router.query.filter_by(hostname=hostname).first_or_404()
    interfaces = Interface.query.filter_by(router_id=router.id)
    return jsonify({'interfaces': [interface.exporta_datos() for interface in interfaces]})

@app.route('/routers/<string:hostname>/usuarios', methods=['GET'])
def get_router_users(hostname):
    # Implementa la lógica para obtener usuarios en el router específico y devuelve la respuesta en formato JSON.
    return jsonify({})

@app.route('/routers/<string:hostname>/usuarios', methods=['POST'])
def create_router_user(hostname):
    # Implementa la lógica para crear un nuevo usuario en el router específico y devuelve la respuesta en formato JSON.
    return jsonify({}), 201

@app.route('/routers/<string:hostname>/usuarios/<int:user_id>', methods=['PUT', 'DELETE'])
def update_or_delete_router_user(hostname, user_id):
    if request.method == 'PUT':
        # Implementa la lógica para actualizar un usuario en el router específico y devuelve la respuesta en formato JSON.
        return jsonify({})
    elif request.method == 'DELETE':
        # Implementa la lógica para eliminar un usuario en el router específico y devuelve la respuesta en formato JSON.
        return jsonify({})

if __name__ == '__main__':
    app.run(debug=True)
