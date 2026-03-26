import subprocess
import os
import re

# 1. Configuración y compilación
exe = './main2'
source = 'main2.cpp'
# Aseguramos compilación limpia
if os.path.exists(source):
    os.system(f"g++ -g {source} -o {exe}")
else:
    print(f"Error: {source} no encontrado.")
    exit()

# 2. Ejecuta el proceso
proc = subprocess.Popen([exe], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 3. Capturar direcciones base desde la salida del programa
output_start = ""
addr_id = ""
addr_nombre = ""

# Leemos las primeras líneas para extraer las direcciones reales de la RAM
for _ in range(2):
    line = proc.stdout.readline().decode('utf-8').strip()
    if 'Direccion de id:' in line:
        addr_id = line.split(':')[-1].strip()
    if 'Direccion de nombre:' in line:
        addr_nombre = line.split(':')[-1].strip()

if not addr_id or not addr_nombre:
    print("No se pudieron capturar las direcciones de memoria.")
    proc.kill()
    exit()

print(f"\n[!] Memoria detectada en el proceso:")
print(f"    ID (buffer):     {addr_id}")
print(f"    Nombre (buffer): {addr_nombre}")

# 4. Preparar el envío (Intento de overflow)
payload_content = "A" * 11
id_payload = payload_content.encode() + b"\n"
name_payload = b"INTENTO-NOMBRE\n"
age_payload = b"25\n"

print(f"\n[+] Enviando {len(payload_content)} bytes a un buffer de 11...")
proc.stdin.write(id_payload)
proc.stdin.write(name_payload)
proc.stdin.write(age_payload)
proc.stdin.flush()

# 5. Capturar el veredicto del programa
to_read, err = proc.communicate(timeout=2)
remaining = to_read.decode('utf-8', errors='replace')

print('\n--- SALIDA DEL PROGRAMA ---')
print(remaining)

# 6. ANALIZADOR INTELIGENTE
print("-" * 30)
print("[!] DIAGNÓSTICO:")

# Extraer el overflow_len real reportado por el C++
match = re.search(r"overflow_len = (\d+)", remaining)
real_overflow_in_ram = int(match.group(1)) if match else 0

# Extraer el contenido final de las variables para verificar corrupción
id_final = re.search(r"id='(.*?)'", remaining).group(1) if "id='" in remaining else ""
nombre_final = re.search(r"nombre='(.*?)'", remaining).group(1) if "nombre='" in remaining else ""

# Lógica de Verificación
if real_overflow_in_ram > 0:
    print(f"    ESTADO: Buffer Overflow Detectado")
    print(f"    MOTIVO: El programa escribió {real_overflow_in_ram} bytes fuera del límite de 'id'.")
    print(f"    EVIDENCIA: La variable 'nombre' fue pisada y ahora contiene: '{nombre_final}'")
else:
    print(f"    ESTADO: Control de Límites Activo")
    print(f"    MOTIVO: Aunque enviamos {len(payload_content)} bytes, cin.getline bloqueó la escritura en el byte 11.")
    print(f"    EVIDENCIA: El ID se truncó a '{id_final}' y 'nombre' quedó a salvo.")

# Comparación de direcciones (Layout)
distancia = int(addr_nombre, 16) - int(addr_id, 16)
print(f"\n[i] Info Técnica: Las variables están separadas por {distancia} bytes en el Stack.")