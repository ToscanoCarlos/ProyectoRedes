from flask import Flask, url_for, jsonify, request, render_template, flash, redirect, Blueprint
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = 'mysecret'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:12345@localhost/redesdb'

db = SQLAlchemy(app)

# Inicializa Flask-SQLAlchemy

class Usuarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    permisos = db.Column(db.String(100))
    dispositivos = db.Column(db.String(100))
    
    def __init__(self, nombre, permisos, dispositivos):
        self.nombre = nombre
        self.permisos = permisos
        self.dispositivos = dispositivos


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/usuarios')
def usuarios():
    usuarios = Usuarios.query.all()
    return render_template('usuarios.html', usuarios=usuarios)


@app.route('/new_usuario', methods=['POST'])
def add_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        permisos = request.form['permisos']
        dispositivos = request.form['dispositivos']

        new_usuario = Usuarios(nombre, permisos, dispositivos)

        db.session.add(new_usuario)
        db.session.commit()

        flash('Usuario agregado')

        return redirect(url_for('usuarios'))
    
@app.route("/update_usuarios/<string:id>", methods=["GET", "POST"])
def update_usuario(id):
    # get usuario by Id
    print(id)
    usuario = Usuarios.query.get(id)

    if request.method == "POST":
        usuario.nombre = request.form['nombre']
        usuario.permisos = request.form['permisos']
        usuario.dispositivos = request.form['dispositivos']

        db.session.commit()

        flash('usuario Actualizado')

        return redirect(url_for('usuarios'))

    return render_template("update_usuarios.html", usuario=usuario)


@app.route("/delete_usuario/<id>", methods=["GET"])
def delete_usuario(id):
    usuario = Usuarios.query.get(id)
    db.session.delete(usuario)
    db.session.commit()

    flash('Usuario Eliminado')

    return redirect(url_for('usuarios'))    

@app.route('/routes')
def routes():
    return render_template('routes.html')
    
@app.route('/topologia')
def topologia():
    return render_template('topologia.html')    

if __name__ == '__main__':
    app.run(debug=True)
