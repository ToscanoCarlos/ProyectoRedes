# Requisitos Generales del Proyecto Final - Administración de Servicios en Red  Grupo 7CM1

## Integrantes
- [x] Islas Osorio Enrique
- [x] Romero Hernandez Martin Manuel
- [x] Toscano Sarabio Carlos Eduardo
- [x] Vazquez Sanchez Alejandro

## Objetivo
Desarrollar una API en Python que proporcione un conjunto de herramientas para la gestión de una red de cómputo en una arquitectura de transferencia de estado representacional (REST).

## Características y Funciones
### Características Generales
1. Comunicación segura con dispositivos de red mediante SSH.
2. Gestión de claves RSA y cifrado de mensajes usando SSH.
3. Respuesta HTTP 404 cuando se solicita un elemento que no existe en la topología.

### Funciones
1. Generación dinámica de una representación gráfica de la topología de la red.
2. CRUD de usuarios en dispositivos de red (globales y por dispositivo) con gestión de permisos y acceso vía SSH.
3. Obtención de información general de enrutadores en la red.
4. Obtención de información general por interfaz del enrutador.

## Características de la Revisión
La topología de revisión es dinámica y se basa en la siguiente topología de prueba:
- Direcciones IP de las interfaces.
- Enrutamiento dinámico.
- Usuario con permisos de administración y acceso por telnet.

## Primera Presentación
Implementación de las siguientes funciones de la API-REST:

### CRUD Usuarios
- Ruta: `/usuarios`
- Comando HTTP: GET y POST
- Descripción:
    - GET: Devuelve JSON con todos los usuarios existentes en los routers, incluyendo nombre, permisos y dispositivos donde existe.
    - POST: Agrega un nuevo usuario a todos los routers y devuelve JSON con la misma información de GET pero del usuario agregado.
- Comando HTTP: PUT y DELETE
- Descripción:
    - PUT: Actualiza un usuario en todos los routers y devuelve JSON con la misma información de GET pero del usuario actualizado.
    - DELETE: Elimina un usuario común a todos los routers y recupera JSON con la misma información de GET pero del usuario eliminado.

### Enrutadores
- Ruta: `/routers`
- Comando HTTP: GET
- Descripción: Regresa la información general de todos los routers de la topología, incluyendo Nombre, IP loopback, IP administrativa, rol, empresa, Sistema operativo y ligas a las interfaces activas.

### Información del Enrutador
- Ruta: `/routers/<hostname>/`
- Comando HTTP: GET
- Descripción: Regresa en formato JSON la información general del router definido, incluyendo Nombre, IP loopback, IP administrativa, rol, empresa, Sistema operativo y ligas a las interfaces activas.

### Interfaces por Router
- Ruta: `/routers/<hostname>/interfaces`
- Comando HTTP: GET
- Descripción: Regresa en formato JSON la información general de la interfaz del router definido, incluyendo tipo, número, IP, máscara de subred, estado y la liga al router al que está conectada, si es el caso.

### CRUD Usuarios por Enrutador
- Ruta: `/routers/<hostname>/usuarios/`
- Comando HTTP: GET y POST
- Descripción:
    - GET: Regresa JSON con los usuarios existentes en el router específico, incluyendo nombre y permisos.
    - POST: Agrega un nuevo usuario al router específico y regresa JSON con la misma información de GET pero del usuario agregado.
- Comando HTTP: PUT y DELETE
- Descripción:
    - PUT: Actualiza un usuario en el router específico y regresa JSON con la misma información de GET pero del usuario actualizado.
    - DELETE: Elimina un usuario común a todos los routers y recupera JSON con la misma información de GET pero del usuario eliminado.

### Detectar Topología
- Ruta: `/topologia`
- Comando HTTP: GET y POST
- Descripción:
    - GET: Regresa JSON con los routers existentes en la topología y las ligas a sus routers vecinos.
    - POST: Activa un demonio que explora la red cada 5 minutos para detectar cambios en la misma.
- Comando HTTP: PUT y DELETE
- Descripción:
    - PUT: Permite cambiar el intervalo de tiempo en el que el demonio explora la topología.
    - DELETE: Detiene el demonio que explora la topología.

### Gráfica de Topología
- Ruta: `/topologia/grafica`
- Comando HTTP: GET
- Descripción: Regresa un archivo en algún formato gráfico que permite visualizar la topología existente.

¡Bienvenidos al proyecto de Administración de Servicios en Red! Este README.md proporciona una visión general de los objetivos, características y funciones del proyecto.
