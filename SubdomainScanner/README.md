# Setup instalaciones por GO version go1.24.1 linux/amd64
La direccion delas herramientas esta apuntando a  ~/go/bin/*
#### Subfinder 2.13.0:
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@v2.13.0
#### Findomain 10.0.1
go install github.com/findomain/findomain@latest
#### Shuffledns 1.2.1
go install -v github.com/projectdiscovery/shuffledns/cmd/shuffledns@v1.2.1
#### Assetfinder 0.1.1
go install github.com/tomnomnom/assetfinder@v0.1.1
#### HTTPX 1.9.0
go install -v github.com/projectdiscovery/httpx/cmd/httpx@v1.9.0

Luego instalar requeriments.txt

---------------------------------------------------------------------------------------------------
los resultados se guardaran en una carpeta donde habra primero el archivo to_resolve que son todos los subdomains encontrados y luego otro archivo final txt que son todos los fitrados por suffle dns