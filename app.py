import getpass
import time
from flask import Flask, url_for, jsonify, request, render_template, flash, redirect, Blueprint
from flask_sqlalchemy import SQLAlchemy
from routes.graficar_topologia import graficar_topologia
from routes.filtros import extraccion_datos_brief, obtener_nombre_interfaz
from routes.ssh import delete_user_ssh, ssh_connect, configure_router_ssh, modify_user_ssh
from routes.execute import execute_comando, execute_delete_user, execute_info_one, execute_users_all, execute_info_router_one, execute_info_all
import paramiko


app = Flask(__name__)
app.secret_key = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@localhost/redesdb'
db = SQLAlchemy(app)
dic_topologia = {"inicio": "inicio"} #Para guardar la topologia en un diccionario global, la razon de esto, nos evita crear una tabla de la conexion de los routers

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

@app.route("/actualizar_usuario/<id>/<username>/<permiso>/<dispositivo>", methods=["PUT"])
def actualizar_usuario(id, username, permiso, dispositivo):
    #usuario = Usuarios.query.get(id)
    usuario = Usuarios.query.get_or_404(id)
    old_username = usuario.nombre
    usuario.nombre = username
    print(old_username)
    print(username)
    usuario.permisos = permiso
    usuario.dispositivos = dispositivo
    db.session.commit()
    routers = Routers.query.all()
    for router in routers:
        modify_user_ssh(router.admin_ip, old_username, username, usuario.permisos)
    

    # Devuelve la información actualizada del usuario en formato JSON
    return jsonify({'id': usuario.id, 'nombre': usuario.nombre, 'permisos': usuario.permisos, 'dispositivos': usuario.dispositivos})
    #return users_info_all("show running-config | include username") 


    
    


@app.route('/new_usuario', methods=['POST'])
def add_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        permisos = request.form['permisos']
        dispositivos = request.form['dispositivos']

        new_usuario = Usuarios(nombre, permisos, dispositivos)
        routers = Routers.query.all()
        agregar_usuario(nombre, permisos, routers, False)

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
        db.session.commit()
        routers = Routers.query.all()
        for router in routers:
            modify_user_ssh(router.admin_ip, old_username, usuario.nombre , usuario.permisos)
        

        flash('Usuario Actualizado')
        

        return users_info_all("show running-config | include username") 

    return render_template("update_usuario.html", usuario=usuario)


@app.route("/delete_usuario/<id>", methods=["DELETE"])
def delete_usuario(id):
    #usuario = Usuarios.query.get(id)
    usuario = Usuarios.query.get_or_404(id)
    routers = Routers.query.all()
    for router in routers:
        delete_user_ssh(router.admin_ip, usuario.nombre)

    db.session.delete(usuario)
    db.session.commit()
    #Primero hay que estar seguros de haber eliminado todos los usarios ne los oruters, una vez hecho esto
    #AHora si podemos descomentar estas lineas para eliminar el usuario en la bd.

    # Devuelve la información actualizada del usuario en formato JSON
    return jsonify({'id': usuario.id, 'nombre': usuario.nombre, 'permisos': usuario.permisos, 'dispositivos': usuario.dispositivos})



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
    return routers_info_all("show cdp neighbors")


@app.route('/get_users')
def get_users():
    return users_info_all("show running-config | include username")
     
@app.route("/get_router/<int:id>", methods=["GET"])
def get_router(id):
    router = Routers.query.get(id)
    return router_info("show cdp neighbors", router)

@app.route("/get_interfaz", methods=["GET", "POST"])
def get_interfaz():
    hostname = request.form["hostname"]
    router = Routers.query.filter_by(hostname=hostname).first()
    interfaz  = request.form['interfaz']
    print(interfaz)
    return info_interfaz(router, interfaz)

@app.route("/get_interfaz2/<hostname>/<num_interfaz>", methods=["GET", "POST"])
def get_interfaz2 (hostname, num_interfaz ):
    interfaz = num_interfaz.replace("+","/")
    #hostname = request.form["hostname"]
    router = Routers.query.filter_by(hostname=hostname).first()
    #interfaz  = request.form['interfaz']
    print(interfaz)
    return info_interfaz(router, interfaz)

@app.route("/get_router_usuarios/<id>", methods=["GET"])
def get_router_usuarios(id):
    router = Routers.query.get(id)
    router_results = {}
    ip = router.admin_ip
    hostname = router.hostname
    username = "root"  # Tu nombre de usuario
    password = "root"#PARA QUE LO HAGA AUTO
    ssh_client = ssh_connect(ip, username, password)
    if ssh_client:
        command= "show running-config | include username"
        router_results[hostname] = execute_info_one(ssh_client, router.admin_ip,command )

        ssh_client.close()
    return jsonify(router_results)

@app.route("/actualizar_usuario_one_router/<id_router>/<id_user>/<username>/<permiso>", methods=["PUT"])
def actualizar_usuario_one_router(id_user, id_router, username, permiso):
    #usuario = Usuarios.query.get(id)
    usuario = Usuarios.query.get_or_404(id_user)
    old_username = usuario.nombre
    usuario.nombre = username
    usuario.permisos = permiso
    db.session.commit()
    router = Routers.query.get_or_404(id_router)
    modify_user_ssh(router.admin_ip, old_username, username, usuario.permisos)
    ssh_client = ssh_connect(router.admin_ip, "root", "root")
    router_results = {}
    if ssh_client:
        router.admin_ip
        command= "show running-config | include username"
        router_results[router.hostname] = execute_info_one(ssh_client, router.admin_ip,command )

        ssh_client.close()
    return jsonify(router_results)


@app.route("/update_one/<id>", methods=["GET", "POST"])
def update_one(id):
    router = Routers.query.get(id)
    if request.method == "POST":
        nombre = request.form['nombre_one']
        permisos = request.form['permisos_one']
        print(nombre, permisos)
        dispositivos = request.form['dispositivos_one']

        new_usuario = Usuarios(nombre, permisos, dispositivos)
        agregar_usuario(nombre, permisos, router, True)
        ssh_client = ssh_connect(router.admin_ip, "root", "root")
        router_results = {}
        if ssh_client:
            router.admin_ip
            command= "show running-config | include username"
            router_results[router.hostname] = execute_info_one(ssh_client, router.admin_ip,command )

            ssh_client.close()
        db.session.add(new_usuario)
        db.session.commit()
        return jsonify(router_results)
    
    return render_template("edit_one.html", router = router)

@app.route("/delete_usuario_one_router/<id_router>/<id_user>", methods=["DELETE"])
def delete_usuario_one_router(id_user, id_router):
    #usuario = Usuarios.query.get(id)
    usuario = Usuarios.query.get_or_404(id_user)    
    router = Routers.query.get_or_404(id_router)
    delete_user_ssh(router.admin_ip, usuario.nombre)

    ssh_client = ssh_connect(router.admin_ip, "root", "root")
    router_results = {}
    if ssh_client:
        router.admin_ip
        command= "show running-config | include username"
        router_results[router.hostname] = execute_info_one(ssh_client, router.admin_ip,command )

        ssh_client.close()
    #De igual formar solo descomentar esat linea cuando este seguro de que se elimino el usuario
    # db.session.delete(usuario)
    # db.session.commit()
    return jsonify(router_results)

@app.route("/get_topologia", methods=["GET"])
def recuperar_topologia():
    analizar_topologia()
    #print(dic_topologia)
    return jsonify(dic_topologia)

@app.route("/graph_topology", methods=["GET"])
def imprimir_topologia():
    graficar_topologia(dic_topologia)
    return render_template("topologia.html")
    
def routers_info_all(command):
    routers = Routers.query.all()
    router_results = {}
    for router in routers:
        ip = router.admin_ip
        hostname = router.hostname
        username = "root"  # Tu nombre de usuario
        password = "root"#PARA QUE LO HAGA AUTO
        
        ssh_client = ssh_connect(ip, username, password)
        if ssh_client:
            router.admin_ip
            router_results[hostname] = execute_info_all(ssh_client, router.admin_ip,command, router.rol, router.empresa, router.so, router.vecinos, router.loopback, router.hostname )

            ssh_client.close()
    return jsonify(router_results)


def users_info_all(command):
    routers = Routers.query.all()
    router_results = {}
    for router in routers:
        ip = router.admin_ip
        hostname = router.hostname
        username = "root"  # Tu nombre de usuario
        password = "root"#PARA QUE LO HAGA AUTO
        
        ssh_client = ssh_connect(ip, username, password)
        if ssh_client:
            router.admin_ip
            router_results[hostname] = execute_users_all(ssh_client, command, router.id)

            ssh_client.close()
    return jsonify(router_results)



def router_info(command, router):
    router_result = {}
    ip = router.admin_ip
    username = "root"  # Tu nombre de usuari
    password = "root"
    ssh_client = ssh_connect(ip, username, password)
    if ssh_client:
        output = execute_info_all(ssh_client, router.admin_ip,command, router.rol, router.empresa, router.so, router.vecinos, router.loopback, router.hostname )
        router_result[router.hostname] = output
        ssh_client.close()
    return jsonify(router_result)


    
def info_interfaz(router, interfaz): 
    command =  "show ip interface fastEthernet " + interfaz
    #print(interfaz, router.id)
    router_result = {}
    ip = router.admin_ip
    username = "root"  # Tu nombre de usuario
    password = "root"
    ssh_client = ssh_connect(ip, username, password)
    ssh_client2 = ssh_connect(ip, username, password)
    numero = 0
    if ssh_client:
        output = execute_info_interfaz(ssh_client, ssh_client2, command, interfaz )
        router_result[router.hostname] = output
        router_result[f'Usuarios del router'] = f'http://127.0.0.1:5000/get_router_usuarios/{router.id}'
        ssh_client.close()
        ssh_client2.close()
    return jsonify(router_result)

def execute_info_interfaz(ssh_client, ssh_client2, command, interfaz):
    try:
        results = {}
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode()
        tipo, ip, mascara, estado = extraccion_datos_brief(output)
        stdin, stdout, stderr = ssh_client2.exec_command("show cdp neighbors")
        link_inter_conect = obtener_nombre_interfaz(stdout.read().decode())
        for link in link_inter_conect:
            if link[1] == interfaz:
                 router = Routers.query.filter_by(hostname=link[0]).first()
                 results["Router conectado"] = f'http://127.0.0.1:5000/get_router/{router.id}'
                 break
        results["Tipo y numero"] = tipo
        results["ip"] = ip
        results["mascara"] = mascara
        results["estado"] = estado
        return results
    except Exception as e:
        print(f"Error al ejecutar el comando: {str(e)}")
 

def agregar_usuario(nombre, permisos, routers, solo):
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
    if solo:
        result = configure_router_ssh(routers.admin_ip, username, password, commands)
    else:
        for router in routers:
            result = configure_router_ssh(router.admin_ip, username, password, commands)
    print(result)

def ejecutar_vecinos(router):
    ip = router.admin_ip
    username = "root"  # Tu nombre de usuario
    password = "root"
    ssh_client = ssh_connect(ip, username, password)
    if ssh_client:
        output = execute_comando(ssh_client, "show cdp neighbors")
        ssh_client.close()
    return obtener_nombre_interfaz(output)

def analizar_topologia():
    dic_topologia.clear()
    routers = Routers.query.all()
    for router in routers:
        conexiones = ejecutar_vecinos(router)
        vecinos = [conexion[0] for conexion in conexiones]
        dic_topologia[router.hostname] = vecinos

if __name__ == '__main__':
    app.run(debug=True)