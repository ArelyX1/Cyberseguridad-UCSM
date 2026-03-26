## Dependencias

Para ejecutar este laboratorio en Ubuntu, asegúrate de tener instalados los siguientes componentes:

- Compilador: g++ (GNU C++ Compiler) para compilar el binario vulnerable.

- Python 3.8+: Para ejecutar el script de automatización (main.py).

- Librerías de Python:

    - subprocess (estándar)

    - re (estándar)

    - os (estándar)

## ¿Cómo funciona?

El laboratorio opera en tres fases automatizadas por el script de Python:

Instrumentación del Binario: El script compila el código C++ con el flag -g (símbolos de depuración) y ejecuta el proceso capturando sus direcciones de memoria reales mediante printf y punteros de C++.

Inyección de Payload: Python envía una cadena de datos diseñada para superar el límite del buffer id[11]. Al usar el operador glotón cin >>, el programa absorbe no solo las "A", sino también el texto destinado a las siguientes variables, fusionándolos en una sola escritura continua en la memoria.

Análisis de Corrupción: El script compara las direcciones base de id y nombre. Si detecta que los bytes del primer envío terminaron en la dirección del segundo, declara un estado de Vulnerabilidad.

PSDT: Alternativamente si desea probar cuando no hay del buffer oveerflow, puedes modificar el codigo para aumentar el input de 11 a n, o tambien en el python en la linea 41 en vez de colocar 11, colocar un numero mas pequeño.

## Resultado

Al ejecutar python3 main.py, el sistema arroja una radiografía de la memoria:

Memoria Detectada: Muestra las direcciones hexadecimales (ej. 0x7ffc02431f65). Esto confirma que las variables están separadas por exactamente 11 bytes en la Pila.

Salida del Programa: El binario reporta un id de 25 caracteres, a pesar de que su tamaño definido era 11.

Hexdump (Stack Around ID): Una representación visual de los bytes 41 (A) seguidos inmediatamente por los bytes de INTENTO-NOMBRE, demostrando la contigüidad física del desbordamiento.

## ¿Qué significa este resultado? / EXTRAS

El diagnóstico "Buffer Overflow Detectado" significa lo siguiente a nivel de Ingeniería de Sistemas:
A. Corrupción de Datos (Data Integrity)

El desbordamiento no es solo un "error de entrada". Significa que la variable id ha invadido el espacio de memoria de nombre. En un sistema real, esto permitiría a un atacante cambiar valores críticos (como un precio, un ID de usuario o un permiso) simplemente escribiendo de más en un campo no protegido.
B. El Comportamiento de cin >>

El resultado demuestra que cin >> es intrínsecamente inseguro. No verifica el tamaño del destino y confía ciegamente en que el programador reservó suficiente espacio para lo que hay en el búfer de entrada.
C. Layout de la Memoria (The Stack)

Confirma que el compilador organiza las variables locales en orden secuencial en el Stack. El "desborde" fluye de direcciones menores a mayores, "mojando" todo lo que encuentre a su paso.
D. Seguridad Preventiva

El hecho de que el overflow_len sea 14 indica que 14 bytes de información "ilegal" están viviendo en una zona de memoria que no les corresponde. Para solucionar esto, el README recomienda sustituir cin >> por cin.getline() o std::string.