import paramiko

def execute_info_all(ssh_client, ip ,command, rol, empresa, so, vecinos, loopback ):
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

        ssh_client.close()
        return output.decode()  # Convertir la salida a una cadena legible
    except Exception as e:
        return str(e)   
    
def execute_users_all(ssh_client ,command ):
    try:
        results = {}
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode()
        results["Usuarios"] = output
        return results
    except Exception as e:
        print(f"Error al ejecutar el comando: {str(e)}")
        return None    
    
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
    
def execute_info_interfaz(ssh_client, command, interfaz):
    try:
        results = {}
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode()
        results[interfaz] = output
        return results
    except Exception as e:
        print(f"Error al ejecutar el comando: {str(e)}")
        return None    