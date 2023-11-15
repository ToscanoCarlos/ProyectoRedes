import time
import paramiko
import re

from routes.filtros import extraccion_datos_brief, obtener_nombre_interfaz

def encontrar_interfaces(texto):
    patron = re.compile(r"\d/\d")

    # Buscar coincidencias en el texto
    coincidencias = patron.findall(texto)
    interfaces = set(coincidencias)
    return list(interfaces)

def execute_info_all(ssh_client, ip ,command, rol, empresa, so, vecinos, loopback,hostname ):
    try:
        results = {}
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode()
        output = encontrar_interfaces(output) 
        if len(output) > 1 :
            for inter in output:
                pas_inter = inter.replace('/', '+')
                results[f"FastEthernet {inter}"] = f'http://127.0.0.1:5000/get_interfaz2/{hostname}/{pas_inter}'
        else:
            pas_inter = output.replace('/', '+')
            results[f"FastEthernet {output}"] = f'http://127.0.0.1:5000/get_interfaz2/{pas_inter}'
        results["ip"] = ip
        results["rol"] = rol
        results["empresa"] = empresa
        results["so"] = so
        results["vecinos"] = vecinos
        results["loopback"] = loopback
        return results
    except Exception as e:
        print(f"Error al ejecutar el comando: {str(e)}")
        return None
    
def execute_comando(ssh_client, comando):
    try:
        stdin, stdout, stderr = ssh_client.exec_command(comando)
        output = stdout.read().decode()
        return output
    except Exception as e:
        print(f"Error al ejecutar el comando general: {str(e)}")
        return None   

def execute_info_one(ssh_client, ip ,command):
    try:
        results = {}
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode()
        output = output.split("\r")
        numero = 0
        for out in output:
            if len(out) > 5: 
                resultados = out.split(" ")
                results[f'username {numero}'] = resultados[1]
                results[f'privilegios {numero}'] = resultados[3]
                numero +=1
        return results
    except Exception as e:
        print(f"Error al ejecutar el comando: {str(e)}")
        return None   
    
def execute_delete_user(ip, username, password, commands):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip, username=username, password=password)

        ssh_shell = ssh_client.invoke_shell()

        for command in commands:
            ssh_shell.send(command + '\n')
            output = ssh_shell.recv(65535)  # Recibir la salida
            time.sleep(1)

        ssh_client.close()
        return output.decode()  # Convertir la salida a una cadena legible
    except Exception as e:
        return str(e)   
    
def execute_users_all(ssh_client ,command, id_router):
    try:
        results = {}
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode()

        output = output.split("\r")
        numero = 0
        for out in output:
            if len(out) > 5: 
                resultados = out.split(" ")
                results[f'username {numero}'] = resultados[1]
                results[f'privilegios {numero}'] = resultados[3]
                results[f'Direccion {numero}'] = f'http://127.0.0.1:5000/get_router_usuarios/{id_router}'
                numero +=1

        return results
    except Exception as e:
        print(f"Error al ejecutar el comando: {str(e)}")
        return None  
  
#CReo que se puede borrar esta funcion  
def execute_info_router_one(ssh_client, ip,command, rol, empresa, so, vecinos, loopback ):
    try:
        results = {}
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode()
        results["interfaces activas"] = output
        results["ip"] = ip
        results["rol"] = rol
        results["empresa"] = empresa
        results["so"] = so
        results["vecinos"] = vecinos
        results["loopback"] = loopback
        return results
    except Exception as e:
        print(f"Error al ejecutar el comando: {str(e)}")
        return None     
    