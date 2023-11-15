import paramiko
def ssh_connect(ip, username, password, port=22):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip, port, username, password)
        return ssh_client
    except Exception as e:
        print(f"Error al conectar por SSH a {ip}: {str(e)}")
        return None
    
def configure_router_ssh(ip, username, password, commands):
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
    

def modify_user_ssh(ip, old_username, new_username, new_privilege_level):
    try:
        with paramiko.SSHClient() as ssh_client:
            ssh_client.load_system_host_keys()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            username = "root"  # Tu nombre de usuario
            password = "root"#PARA QUE LO HAGA AUTO
            ssh_client.connect(ip, 22, username, password)

            with ssh_client.invoke_shell() as ssh_shell:
                # Comandos para modificar el nombre de usuario
                commands = [
                    'conf t',
                    f'no username {old_username}',
                    f'username {new_username} privilege {new_privilege_level} secret root',
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
                for command in commands:
                    #print(f"Enviando comando: {command}")
                    ssh_shell.send(command + '\n')
                    output = ssh_shell.recv(65535)
                    #print(f"Salida del comando: {output.decode()}")

                    if "ERROR" in output.decode():
                        raise Exception(f"Error al ejecutar el comando: {command}")

                return output.decode()  # Devolver la salida después de ejecutar todos los comandos

    except Exception as e:
        return str(e)
    
def delete_user_ssh(ip, old_username):
    try:
        with paramiko.SSHClient() as ssh_client:
            ssh_client.load_system_host_keys()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            username = "root"  # Tu nombre de usuario
            password = "root"#PARA QUE LO HAGA AUTO
            ssh_client.connect(ip, 22, username, password)

            with ssh_client.invoke_shell() as ssh_shell:
                # Comandos para modificar el nombre de usuario
                commands = [
                    'conf t',
                    f'no username {old_username}',
                ]
                for command in commands:
                    #print(f"Enviando comando: {command}")
                    ssh_shell.send(command + '\n')
                    output = ssh_shell.recv(65535)
                    #print(f"Salida del comando: {output.decode()}")

                    if "ERROR" in output.decode():
                        raise Exception(f"Error al ejecutar el comando: {command}")

                return output.decode()  # Devolver la salida después de ejecutar todos los comandos

    except Exception as e:
        return str(e)