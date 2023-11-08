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
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip, "root", "root")

        ssh_shell = ssh_client.invoke_shell()

        # Comandos para modificar el nombre de usuario
        commands = [
            'conf t',
            f'username {old_username} privilege {new_privilege_level}',
            f'username {old_username} new-username {new_username}',
            'exit',
            'end',
        ]

        for command in commands:
            ssh_shell.send(command + '\n')
            output = ssh_shell.recv(65535)  # Recibir la salida

        ssh_client.close()
        return output.decode()  # Convertir la salida a una cadena legible
    except Exception as e:
        return str(e)     
  