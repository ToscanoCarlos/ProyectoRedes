import getpass
from flask import Flask, url_for, jsonify, request, render_template, flash, redirect, Blueprint
from flask_sqlalchemy import SQLAlchemy
from routes.ssh import ssh_connect, configure_router_ssh, modify_user_ssh
from routes.execute import execute_delete_user, execute_users_all, execute_info_router_one, execute_info_interfaz, execute_info_all
import paramiko


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

class Routers(db.Model):
    __tablename__ = 'routers'
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(64), unique=True)
    loopback = db.Column(db.String(120))
    admin_ip = db.Column(db.String(120))
    rol = db.Column(db.String(64))
    empresa = db.Column(db.String(64))
    so = db.Column(db.String(64))
    vecinos = db.Column(db.String(64))
    
    def __init__(self, hostname, loopback, admin_ip, rol, empresa, so, vecinos):
        self.hostname = hostname
        self.loopback = loopback
        self.admin_ip = admin_ip
        self.rol = rol
        self.empresa = empresa
        self.so = so
        self.vecinos = vecinos
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
        agregar_usuario(nombre, permisos)

        db.session.add(new_usuario)
        db.session.commit()

        flash('Usuario agregado')

        return users_info_all("show running-config | include username")
    
@app.route("/update_usuario/<id>", methods=["GET", "POST"])
def update_usuario(id):
    #usuario = Usuarios.query.get(id)
    usuario = db.session.get(Usuarios, id)  # Cambia esta línea
    old_username = usuario.nombre

    if request.method == "POST":
        usuario.nombre = request.form['nombre']
        usuario.permisos = request.form['permisos']
        usuario.dispositivos = request.form['dispositivos']
        routers = Routers.query.all()
        for router in routers:
            modify_user_ssh(router.admin_ip, old_username, usuario.nombre , usuario.permisos)
        db.session.commit()

        flash('Usuario Actualizado')
        

        return users_info_all("show running-config | include username") 

    return render_template("update_usuario.html", usuario=usuario)


@app.route("/delete_usuario/<id>", methods=["GET"])
def delete_usuario(id):
    usuario = Usuarios.query.get(id)
    db.session.delete(usuario)
    db.session.commit()
    delete_user(usuario.nombre)
    flash('Usuario Eliminado')


    return users_info_all("show running-config | include username") 


@app.route('/routes')
def routes():
    routers = Routers.query.all()
    return render_template('routes.html', routers = routers)

@app.route('/new_router', methods=['POST'])
def add_router():
    if request.method == 'POST':
        hostaname = request.form['hostaname']
        loopback = request.form['loopback']
        admin_ip = request.form['admin_ip']
        rol = request.form['rol']
        empresa = request.form['empresa']
        so = request.form['so']
        vecinos = request.form['vecinos']

        new_router = Routers(hostaname, loopback, admin_ip, rol, empresa, so, vecinos)

        db.session.add(new_router)
        db.session.commit()

        flash('router agregado')

        return redirect(url_for('routes'))
    
@app.route("/update_router", methods=["GET", "POST"])
def update_router():
    print("entro antes")
    router_name = request.form.get('update-delete-router-hostname')
    #router_name = request.form['update-delete-router-hostname']
    print(router_name)
    print(request.form)
    # get router by NAME
    router = Routers.query.get(router_name)

    if request.method == "POST":
        print("entro aqui")
        router.hostname = request.form.get('update-delete-router-hostname')
        router.admin_ip = request.form.get('update-delete-router-ip')
        router.loopback = request.form.get('update-delete-router-loopback')

        db.session.commit()

        flash('router Actualizado')

        return redirect(url_for('routes'))

    return render_template("routes.html", router=router)


@app.route("/delete_router/<id>", methods=["GET"])
def delete_router(id):
    router = Routers.query.get(id)
    db.session.delete(router)
    db.session.commit()

    flash('Router Eliminado')

    return redirect(url_for('routes'))  
    
@app.route('/topologia')
def topologia():
    return render_template('topologia.html')

@app.route('/info_routers')
def activar_comandos():
    return routers_info_all("show ip interface brief")


@app.route('/get_users')
def get_users():
    return users_info_all("show running-config | include username")
     
@app.route("/get_router/<int:id>", methods=["GET"])
def get_router(id):
    router = Routers.query.get(id)
    return router_info("show ip interface brief", router)

@app.route("/get_interfaz", methods=["GET", "POST"])
def get_interfaz():
    hostname = request.form["hostname"]
    router = Routers.query.filter_by(hostname=hostname).first()
    interfaz  = request.form['interfaz']
    print(interfaz)
    return info_interfaz(router, interfaz)

   
 
def routers_info_all(command):
    routers = Routers.query.all()
    router_results = {}
    for router in routers:
        ip = router.admin_ip
        hostname = router.hostname
        

        username = "root"  # Tu nombre de usuario
        #password = getpass.getpass(f"Contraseña para {username}: ")  # Solicita la contraseña de forma segura
        password = "root"#PARA QUE LO HAGA AUTO
        
        ssh_client = ssh_connect(ip, username, password)
        if ssh_client:
            router.admin_ip
            router_results[hostname] = execute_info_all(ssh_client, router.admin_ip,command, router.rol, router.empresa, router.so, router.vecinos, router.loopback )

            ssh_client.close()
    return jsonify(router_results)


def delete_user(nombre):
    routers = Routers.query.all()
    #ip = '10.10.10.10'  # Reemplaza con la dirección IP de tu router en GNS3
    username = 'root'  # Reemplaza con tu nombre de usuario
    password = 'root'  # Reemplaza con tu contraseña
    commands = [
        'conf t',
        f'no username {nombre}',
        'end'
    ]
    for router in routers:
        execute_delete_user(router.admin_ip, username, password, commands)



def users_info_all(command):
    routers = Routers.query.all()
    router_results = {}
    for router in routers:
        ip = router.admin_ip
        hostname = router.hostname
        

        username = "root"  # Tu nombre de usuario
        #password = getpass.getpass(f"Contraseña para {username}: ")  # Solicita la contraseña de forma segura
        password = "root"#PARA QUE LO HAGA AUTO
        
        ssh_client = ssh_connect(ip, username, password)
        if ssh_client:
            router.admin_ip
            router_results[hostname] = execute_users_all(ssh_client, command)

            ssh_client.close()
    return jsonify(router_results)



def router_info(command, router):
    router_result = {}
    ip = router.admin_ip
    username = "root"  # Tu nombre de usuario
    #password = getpass.getpass(f"Contraseña para {username}: ")  # Solicita la contraseña de forma segura
    #comando para ver los usarios y la contra en el router : show running-config | include username
    password = "root"
    ssh_client = ssh_connect(ip, username, password)
    if ssh_client:
        output = execute_info_router_one(ssh_client, router.admin_ip,command, router.rol, router.empresa, router.so, router.vecinos, router.loopback )
        router_result[router.hostname] = output
        ssh_client.close()
    return jsonify(router_result)


    
def info_interfaz(router, interfaz): 
    command =  "show ip interface fastEthernet " + interfaz
    #print(interfaz, router.id)
    router_result = {}
    ip = router.admin_ip
    username = "root"  # Tu nombre de usuario
    #password = getpass.getpass(f"Contraseña para {username}: ")  # Solicita la contraseña de forma segura
    #comando para ver los usarios y la contra en el router : show running-config | include username
    password = "root"
    ssh_client = ssh_connect(ip, username, password)
    if ssh_client:
        output = execute_info_interfaz(ssh_client, command, interfaz )
        router_result[router.hostname] = output
        ssh_client.close()
    return jsonify(router_result)


def agregar_usuario(nombre, permisos):
    routers = Routers.query.all()
    #ip = '10.10.10.10'  # Reemplaza con la dirección IP de tu router en GNS3
    username = 'root'  # Reemplaza con tu nombre de usuario
    password = 'root'  # Reemplaza con tu contraseña
    commands = [
        'conf t',
        f'username {nombre} privilege {permisos} secret root',
        'crypto key generate rsa usage-keys label [nombre_clave] modulus [tamaño_de_modulo]',
        'ip ssh version 2',
        'ip ssh time-out [tiempo_en_segundos]',
        'ip ssh authentication-retries [intentos]',
        'line vty 0 15',
        'transport input ssh',
        'login local',
        'exit',
        'end'
    ]
    for router in routers:
        result = configure_router_ssh(router.admin_ip, username, password, commands)
    print(result)


if __name__ == '__main__':
    app.run(debug=True)
