import subprocess
import threading
import sys
import time
import shutil
import os
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

console = Console()

def prepare_environment():
    home = os.path.expanduser("~")
    extra_paths = [f"{home}/go/bin", f"{home}/.local/bin", "/usr/local/go/bin", "/usr/bin", "/bin"]
    current_path = os.environ.get("PATH", "")
    for p in extra_paths:
        if os.path.exists(p) and p not in current_path:
            current_path += os.pathsep + p
    os.environ["PATH"] = current_path

class ScannerDashboard:
    def __init__(self, target, tools_names):
        self.target = target
        self.results = {name: {"status": "Esperando...", "count": 0, "time": 0.0, "color": "cyan"} for name in tools_names}
        self.all_found = set()
        self.lock = threading.Lock()

    def update_status(self, name, status, count=None, elapsed=None, color=None):
        with self.lock:
            if count is not None: self.results[name]["count"] = count
            if elapsed is not None: self.results[name]["time"] = elapsed
            if color: self.results[name]["color"] = color
            self.results[name]["status"] = status

    def add_subdomain(self, sub):
        with self.lock:
            if sub: self.all_found.add(sub)

    def generate_table(self):
        table = Table(title=f"[bold magenta]{self.target}[/]", expand=True)
        table.add_column("Herramienta", style="bright_magenta")
        table.add_column("Estado", justify="center")
        table.add_column("Hallazgos", justify="right", style="bright_green")
        table.add_column("Tiempo", justify="right", style="bright_blue")
        
        with self.lock:
            for name, data in self.results.items():
                table.add_row(
                    name, 
                    f"[{data['color']}]{data['status']}[/]", 
                    str(data['count']), 
                    f"{data['time']:.1f}s"
                )
        return table

def clean_input(raw_line, domain):
    if not raw_line: return None
    clean = raw_line.strip().lower()
    # Eliminar protocolos, puertos y comas
    if "://" in clean: clean = clean.split("://")[-1]
    clean = clean.split("/")[0].split(":")[0].split(",")[0].split(" ")[0]
    
    if clean.startswith("www."): clean = clean[4:]
    
    # Validar que pertenezca al dominio y no sea basura de la terminal
    if domain in clean and clean != domain and "." in clean and not clean.startswith("["):
        return clean
    return None

def get_resolvers():
    res = "/tmp/resolvers.txt"
    if not os.path.exists(res):
        with open(res, "w") as f:
            f.write("8.8.8.8\n8.8.4.4\n1.1.1.1\n1.0.0.1\n9.9.9.9\n")
    return res

def run_passive_tool(name, cmd_list, domain, dashboard, output_dir):
    start = time.time()
    found_in_tool = set()
    binary = shutil.which(cmd_list[0])
    
    if not binary:
        dashboard.update_status(name, "❌ No instalado", color="red")
        return

    try:
        dashboard.update_status(name, "🚀 Iniciando", color="yellow")
        cmd_list[0] = binary 
        
        process = subprocess.Popen(
            cmd_list, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, 
            text=True, bufsize=1, universal_newlines=True
        )
        
        for line in iter(process.stdout.readline, ''):
            sub = clean_input(line, domain)
            if sub and sub not in found_in_tool:
                found_in_tool.add(sub)
                dashboard.add_subdomain(sub)
                dashboard.update_status(name, "🔍 Escaneando", len(found_in_tool), time.time() - start)
        
        process.wait()
        dashboard.update_status(name, "✅ Finalizado", len(found_in_tool), time.time() - start, "green")
    except Exception:
        dashboard.update_status(name, "💥 Error", color="red")

def run_shuffledns_resolve(domain, dashboard, output_dir):
    """Emula el pipe: subfinder | shuffledns -mode resolve"""
    name = "Shuffledns"
    start = time.time()
    rs = get_resolvers()
    
    # Recolectamos lo que los otros scanners encontraron hasta ahora
    with dashboard.lock:
        input_list = list(dashboard.all_found)
    
    if not input_list:
        dashboard.update_status(name, "Nada que resolver", color="yellow")
        return

    temp_input = os.path.join(output_dir, "to_resolve.txt")
    with open(temp_input, "w") as f:
        f.write("\n".join(input_list))

    cmd = ["shuffledns", "-d", domain, "-list", temp_input, "-r", rs, "-mode", "resolve", "-silent"]
    
    try:
        dashboard.update_status(name, "Validando...", color="yellow")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        
        valid_subs = set()
        for line in iter(process.stdout.readline, ''):
            sub = clean_input(line, domain)
            if sub:
                valid_subs.add(sub)
                # Aquí NO añadimos a dashboard.all_found para no duplicar, 
                # Shuffledns actúa como filtro final.
                dashboard.update_status(name, "🔍 Validando", len(valid_subs), time.time() - start)
        
        process.wait()
        
        # Guardamos la lista validada
        if valid_subs:
            valid_file = os.path.join(output_dir, "shuffledns_valid.txt")
            with open(valid_file, "w") as f:
                f.write("\n".join(sorted(valid_subs)))

        dashboard.update_status(name, "✅ Finalizado", len(valid_subs), time.time() - start, "green")
        return valid_subs
    except Exception:
        dashboard.update_status(name, "💥 Error", color="red")
        return set()

def main():
    if len(sys.argv) < 2:
        console.print("[bold red]Uso: python3 app.py <dominio.com>[/]")
        return

    prepare_environment()
    target = sys.argv[1].lower().strip()
    output_dir = f"results_{target.replace('.', '_')}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Herramientas pasivas primero
    passive_tools = [
        ("Subfinder", ["subfinder", "-d", target, "-silent"]),
        ("Findomain", ["findomain", "-t", target, "-q"]),
        ("Assetfinder", ["assetfinder", "--subs-only", target])
    ]

    # Dashboard incluye Shuffledns que se activará después
    db = ScannerDashboard(target, [t[0] for t in passive_tools] + ["Shuffledns"])

    threads = []
    for name, cmd in passive_tools:
        t = threading.Thread(target=run_passive_tool, args=(name, cmd, target, db, output_dir), daemon=True)
        threads.append(t)
        t.start()

    with Live(db.generate_table(), refresh_per_second=4) as live:
        # Esperar a los scanners pasivos
        while any(t.is_alive() for t in threads):
            time.sleep(0.5)
            live.update(db.generate_table())
        
        # Una vez terminan los pasivos, ejecutamos Shuffledns para validar
        valid_results = run_shuffledns_resolve(target, db, output_dir)
        live.update(db.generate_table())

    # Consolidación de resultados
    final_list = valid_results if valid_results else db.all_found
    if final_list:
        total_file = os.path.join(output_dir, "final_results.txt")
        with open(total_file, "w") as f:
            f.write("\n".join(sorted(final_list)))
        
        console.print(f"\n[bold green]📊 Total {len(final_list)} únicos guardados en: {total_file}[/]")

        # Validación final con HTTPX
        httpx_bin = shutil.which("httpx")
        if httpx_bin:
            console.print("[bold yellow] Iniciando validación HTTPX para servicios activos...[/]")
            httpx_out = os.path.join(output_dir, "httpx_valid.txt")
            subprocess.run([httpx_bin, "-l", total_file, "-silent", "-sc", "-title", "-ip", "-o", httpx_out])
            console.print(f"[bold blue]📄 Verificación completada: {httpx_out}[/]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]⏹️ Escaneo cancelado.[/]")
        sys.exit(0)
