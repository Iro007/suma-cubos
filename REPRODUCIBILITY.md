# Reproducibilidad del buscador exacto

Actualizado el 10 de octubre de 2026. Los comandos y tiempos anteriores del
motor C++ se conservan como evidencia historica en `experiments/2026-10-10`.
El C++ antiguo esta deshabilitado por desbordamientos no detectados y por su
cobertura restringida. La ruta publicada utiliza el motor Python exacto.

## Entorno

Windows / PowerShell; `.venv` con Python 3.13.15. El motor y los tests usan
solo la biblioteca estandar. No se instalaron paquetes adicionales.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -v
.\.venv\Scripts\python.exe booker_sieve.py --K 6 --B 12 --procs 2
```

## Cobertura y limites matematicos

Para S=x+y distinto de cero, d=abs(S) y V=x-y:

- d divide K-z^3.
- Delta = 3d(4 abs(K-z^3)-d^3) = (3dV)^2.
- Por tanto, si abs(z)<=B, d^3<=4(B^3+abs(K)).

Se recorren todos los d del intervalo declarado y todas las raices cubicas
modulares, incluidas las singulares. Para cada raiz se recorren las
progresiones de z positivas y negativas. Se comprueba que Delta sea un
cuadrado, que la reconstruccion tenga paridad correcta y que la suma exacta
sea K. No se impone orden sobre las coordenadas ni se usa el lema mod 18.
Las cotas, raices cuadradas y cubicas se calculan con enteros arbitrarios.
Una terna puede aparecer bajo distintas permutaciones; eso no significa
que sean soluciones matematicamente distintas.

Con el rango completo de d, el metodo enumera todas las soluciones con
S distinto de cero y abs(z)<=B. Si K es un cubo, S=0 produce la familia
infinita (t,-t,cuberoot(K)); el CLI directo la informa separadamente.
El cazador de objetivos finitos rechaza ese caso para evitar confundir
una familia infinita con la lista de resultados finitos.

Esto es una justificacion algebraica y validacion computacional; no es
una prueba formal en Lean de la implementacion completa.

## Busqueda de los siete objetivos

```powershell
.\.venv\Scripts\python.exe hunt_unsolved.py --all --B 1000000 --threads 2 --chunk-size 8192 --run-dir experiments\validated-v2-low-2026-10-10
```

Rango: 0<=abs(z)<=1000000; 1<=d<=1587401 para cada objetivo.
Esta cota de z no es una cota sobre el maximo de las tres coordenadas.
Para una caja completa con las tres coordenadas acotadas por B, este
rango incluye todos sus triples, pero puede incluir otros mayores.

Una banda de coordenadas grandes, con cobertura parcial explicita:

```powershell
.\.venv\Scripts\python.exe hunt_unsolved.py --all --z-min 100000000000000000000 --B 100000000000000100000 --d-max 10000 --threads 2 --chunk-size 512 --run-dir experiments\validated-v2-high-2026-10-10
```

Se revisan ambos signos de z. No cubre otros z ni divisores d>10000.
No demuestra ausencia global ni representa una cota record publicada.

## Checkpoints

Cada objetivo tiene un JSON con K, B, z_min, d_min, d_max, version y SHA-256
del motor. El ultimo d avanza solo al terminar bloques consecutivos y
verificar sus resultados. El guardado usa reemplazo atomico con reintentos
para bloqueos transitorios de archivos en Windows. Una interrupcion
repite a lo sumo trabajo no confirmado, sin saltarse bloques.

El mismo comando reanuda automaticamente. Cambiar cotas o motor exige
otra carpeta: el cazador rechaza checkpoints incompatibles. Los antiguos
TXT no se importan porque no contienen parametros suficientes.
No ejecutar dos cazadores simultaneamente en la misma carpeta de salida.

## Evidencia de validacion

Pasaron los 11 tests originales y cinco tests nuevos sobre dominios numericos (16 en total). Las dos campanas terminaron para los siete objetivos,
con cero soluciones, y los 14 checkpoints pasaron la revision de parametros
y huella del motor.

`test_search.py` compara contra enumeraciones independientes:

- 8280 combinaciones (K,d) para las raices modulares.
- 84 valores de K en cajas de coordenadas entre -12 y 12.
- Subgrupos cubicos profundos, signos, discriminante cero y bandas partidas.
- Ternas publicadas para 165, 579 y 906, con cubos mucho mayores que 128 bits.
- 1000 ternas construidas con coordenadas de hasta 30 digitos y ambos signos.
- Raices cubicas enteras hasta entradas de 301 digitos.
- Reanudacion, incompatibilidad, corrupcion y bloqueos de checkpoints.

La salida de los tests y las busquedas esta en `experiments/2026-10-10`.
Los JSON de cada campana muestran el rango realmente completado.


## Estudio de dominios numericos

```powershell
.\.venv\Scripts\python.exe number_domains.py
.\.venv\Scripts\python.exe number_domains.py --output .git\domains-replay.json
.\.venv\Scripts\python.exe scripts\audit_number_domains.py .git\domains-replay.json
```

Para cambiar el objetivo, se puede indicar --K y las cotas. Sin --output,
el nombre del archivo incluye K para no sobrescribir la evidencia de 114.
Los resultados gaussianos se contrastan contra otro recorrido exacto y las
fracciones positivas contra enumeracion de triples ordenados. CI repite
la busqueda completa y compara su JSON con la evidencia publicada.

El minimo denominador 6 requiere las tres fracciones estrictamente positivas.
La altura gaussiana es la maxima componente entera absoluta; su minimo 23
se verifica por enumeracion y contraste, no por una prueba Lean de ausencia.
Lean compilo el teorema del denominador minimo y los certificados de los
testigos racional y gaussiano. Ver DEMOSTRACION.md.
