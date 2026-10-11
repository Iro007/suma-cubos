# Suma de tres cubos: estado del proyecto

Actualizado el 10 de octubre de 2026.

## Objetivo y estado

Se buscan enteros x,y,z con x^3+y^3+z^3=K. Los siete objetivos pendientes
bajo 1000 consultados son 114,390,627,633,732,921,975.
No se ha encontrado una solucion nueva en las campanas registradas aqui.

Fuentes consultadas:
- Booker y Sutherland, On a question of Mordell:
  https://research-information.bris.ac.uk/files/268996955/e2022377118.full.pdf
- Resultados publicados por Andrew Sutherland:
  https://math.mit.edu/~drew/sumsofcubes.html

165,579 y 906 tienen ternas publicadas. Se verificaron con enteros exactos
como controles positivos; no son descubrimientos de este proyecto.
Las afirmaciones anteriores sobre openai/math, BSD, cotas mundiales y
complejidad/rendimiento del C++ no se usan como evidencia del motor actual.

## Motor corregido

`booker_sieve.py` es ahora un buscador exacto por divisores, version
exact-divisor-v2. Usa enteros Python de precision arbitraria. Su nombre
se conserva por compatibilidad; ya no pretende reproducir literalmente
la criba optimizada de Booker.

Se corrigieron las raices modulares singulares, incluido K=732,d=4 y
K=975,d=25. Se aceptan candidatos con discriminante cero y se eliminan
las restricciones de orden y mod 18 del recorrido generico. Los limites
d y z son enteros y su cobertura esta definida algebraicamente.

El C++ anterior esta retirado. Tanto su codigo compilado como la opcion
explicita cpp se niegan a ejecutar el motor inseguro. El backend auto
usa Python. Se conservo una copia del binario anterior en experiments
para evidencia historica; esa copia no es un backend validado.

## Validacion

Pasaron 11 tests de regresion y comparacion independiente:
- 8280 combinaciones K,d comparadas con enumeracion modular directa.
- 84 objetivos comparados con enumeracion independiente en la caja [-12,12]^3.
- Ternas conocidas de gran tamano para 165,579 y 906.
- 1000 ternas construidas con signos y coordenadas de hasta 30 digitos.
- Raices enteras de entradas enormes, intervalos partidos y bandas grandes.
- Checkpoints reanudados, incompatibles y corruptos; bloqueo transitorio Windows.

Registro: experiments/2026-10-10/validation.log.
No se ha formalizado en Lean una prueba de correccion de todo el programa.

## Campanas despues de la correccion

Banda alta COMPLETADA para los siete K:
10^20 <= abs(z) <= 10^20+100000; 1 <= abs(x+y) <= 10000.
Cero soluciones. Es cobertura parcial, no una ausencia global ni un record.
Checkpoints: experiments/validated-v2-high-2026-10-10/kK.json.

Campana baja COMPLETADA para los siete K: abs(z)<=1000000; 1<=abs(x+y)<=1587401.
Cero soluciones. Se releyeron los 14 checkpoints de ambas campanas y se
confirmaron sus parametros, cobertura completada y huella SHA-256 del motor.
El progreso y las soluciones confirmadas de cada K estan en
experiments/validated-v2-low-2026-10-10/kK.json. El campo complete indica
si todo el intervalo declarado termino. No interpretar un checkpoint
incompleto como un barrido terminado.

Los logs de ambas campanas estan en experiments/2026-10-10.
Un bloqueo de reemplazo del checkpoint bajo Windows se corrigio con
reintentos y la campana se reanudo desde el ultimo prefijo confirmado.

## Continuacion

REPRODUCIBILITY.md contiene los comandos exactos y la justificacion de
cobertura. El mismo comando reanuda la misma campana. Para extender las
cotas se usa otra carpeta porque cambiar B requiere volver a revisar
los d anteriores con los z nuevos; un checkpoint viejo no autoriza
saltarlos.


## Ampliacion completada el 10 de octubre de 2026

Se completaron otras tres campanas para los siete K (21 ejecuciones).
No se encontraron soluciones nuevas. Se releyeron los 21 checkpoints,
confirmando los parametros, el rango completo de d y la huella SHA-256
exacta del motor. Se exploraron ambos signos de z.

- high20-extension: 10^20+100001 <= abs(z) <= 10^20+400000;
  1 <= abs(x+y) <= 10000.
- high20-divisors: 10^20 <= abs(z) <= 10^20+100000;
  10001 <= abs(x+y) <= 100000.
- high21: 10^21 <= abs(z) <= 10^21+100000;
  1 <= abs(x+y) <= 10000.

No se repitieron los rectangulos de busqueda anteriores. Los checkpoints
estan en experiments/high20-extension-2026-10-10,
experiments/high20-divisors-2026-10-10 y experiments/high21-2026-10-10.
Los logs estan en experiments/2026-10-10/high20-extension.log,
high20-divisors.log, high21.log y extension-readback.log.
Son tres regiones finitas y parciales: las cotas superiores de z no
significan que se haya explorado todo el intervalo desde cero hasta ellas.


## Publicacion y formalizacion verificadas

Repositorio publico: https://github.com/Iro007/suma-cubos

Se formalizaron siete lemas del fundamento algebraico y cinco controles
publicados en Lean 4.19.0 con Mathlib fijado. Los 12 teoremas compilaron
correctamente; evidencia y alcance en DEMOSTRACION.md y
https://github.com/Iro007/suma-cubos/actions/runs/38106620320.

Tambien se ejecutaron siete pruebas locales para valores mayores de 1000,
con abs(z)<=10000 y rango completo de divisores. Se hallaron 11 ternas
por permutacion para cinco K, todos ya representados en la tabla historica
de Mishima. Para 1011 y 1020 no hubo resultados en ese rango. No se ha
establecido un nuevo caso mundial ni el estado global actual de esos dos K.
Los datos estan en evidence/beyond-1000-probe.json.
