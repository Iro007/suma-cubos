# Suma de tres cubos: buscador exacto y fundamento formal

Este repositorio publica un buscador reproducible para
`x^3 + y^3 + z^3 = K`, sus pruebas de regresion, 35 registros de campanas
completadas y la formalizacion en Lean 4 de su base algebraica.

**No se ha descubierto una solucion nueva para los siete objetivos
114,390,627,633,732,921,975.** Los barridos negativos son resultados
limitados a regiones finitas; no prueban inexistencia global.

## Que esta verificado

- Python: 11 tests locales aprobados, con comparaciones contra enumeracion
  independiente, raices singulares, enteros grandes y reanudacion.
- Evidencia: 35 pares campana-K completados y auditados con el SHA-256
  del motor. Todos reportan cero ternas dentro de sus regiones.
- Lean: el proyecto `formal/` verifica identidades, condiciones necesarias,
  reconstruccion y la cota de divisores. La comprobacion del kernel se
  ejecuta en el job `lean` de [GitHub Actions](https://github.com/Iro007/suma-cubos/actions).
  La primera ejecucion de CI determina el estado de compilacion.

La prueba formal no certifica todo el programa Python, los archivos JSON,
la ausencia global de soluciones ni un descubrimiento mundial.

## Uso

Python 3.10 o posterior; solo biblioteca estandar. Desde Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m unittest test_search -v
.\.venv\Scripts\python.exe scripts\audit_campaigns.py
.\.venv\Scripts\python.exe hunt_unsolved.py --all --B 100000 --threads 2 --run-dir experiments\mi-campana
```

En Linux/macOS usa `.venv/bin/python` para los mismos comandos.
El motor directo permite otros K:

```powershell
.\.venv\Scripts\python.exe booker_sieve.py --K 1002 --B 1000
```

Ese comando explora un valor mayor de 1000; no afirma que 1002 sea un caso
abierto ni que una terna encontrada sea nueva en la literatura.

## Resultados y regiones

`d` significa `abs(x+y)`. Se revisan ambos signos de `z`.

1. `abs(z)<=10^6`, `1<=d<=1587401`.
2. `10^20<=abs(z)<=10^20+100000`, `1<=d<=10000`.
3. `10^20+100001<=abs(z)<=10^20+400000`, `1<=d<=10000`.
4. `10^20<=abs(z)<=10^20+100000`, `10001<=d<=100000`.
5. `10^21<=abs(z)<=10^21+100000`, `1<=d<=10000`.

Cada region se completo para los siete objetivos: 5x7=35 ejecuciones.
Los detalles estan en [RESULTADO.md](RESULTADO.md), los checkpoints en
`experiments/` y las verificaciones locales en `evidence/`.
No se exploro todo el intervalo de cero a 10^21.

## Demostracion

Sea `S=x+y`, `V=x-y`. El metodo utiliza:

- `x^3+y^3 = S*(x^2-x*y+y^2)`;
- `3*S*V^2 = 4*(K-z^3)-S^3`;
- para `d=abs(S)`, `3*d*(4*abs(K-z^3)-d^3)=(3*d*V)^2`;
- si `abs(z)<=B`, entonces `d^3<=4*(B^3+abs(K))`.

La derivacion y el alcance estan en [DEMOSTRACION.md](DEMOSTRACION.md).
El codigo formal esta en [formal/SumaCubos.lean](formal/SumaCubos.lean).
Lean 4.19.0 y Mathlib estan fijados a versiones concretas.

## Sobre valores mayores de 1000

1000 no es una frontera matematica. Es un corte historico muy estudiado.
Hay estudios y tablas de busqueda hasta 10000, como el trabajo de
[H. Mishima](https://www.asahi-net.or.jp/~kc2h-msm/mathland/math04/cube00.htm).
Esa tabla es historica: una entrada ausente no confirma un problema abierto
hoy. Tampoco generar un K a partir de una terna constituye por si solo un
nuevo resultado cientifico. No se ha verificado aqui una lista actual de
objetivos abiertos mayores de 1000.

Se ejecutaron ademas siete pruebas locales para K=1002,1005,1011,1014,
1020,1023,1029 con abs(z)<=10000 y el rango completo de d. El archivo
[evidence/beyond-1000-probe.json](evidence/beyond-1000-probe.json) registra
las ternas verificadas y declara que su novedad bibliografica no fue
establecida. Por ejemplo, 1002=1^3+1^3+10^3 es una representacion sencilla;
no se presenta como descubrimiento. Las ternas se agrupan por permutacion.

Para un posible hallazgo se requiere: verificar la suma entera, contrastar
las bases y publicaciones y distinguir primera representacion conocida,
nueva representacion y mejora de cota. Ninguna de esas novedades se
atribuye a las campanas publicadas en este repositorio.

## Referencias

- Booker, Cracking the problem with 33 (2019): https://arxiv.org/abs/1903.04284
- Booker y Sutherland, On a question of Mordell:
  https://doi.org/10.1073/pnas.2022377118
- Datos de Sutherland: https://math.mit.edu/~drew/sumsofcubes.html
- Huisman, Newer sums of three cubes: https://arxiv.org/abs/1604.07746
- Mishima, busquedas hasta 10000:
  https://www.asahi-net.or.jp/~kc2h-msm/mathland/math04/cube00.htm

El backend C++ y otros experimentos anteriores no forman parte de la
publicacion validada. [REPRODUCIBILITY.md](REPRODUCIBILITY.md) explica la
cobertura y los checkpoints.
