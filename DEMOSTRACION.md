# Fundamento y alcance de la demostracion

Se trabaja con x,y,z,K enteros. Definimos S=x+y, V=x-y y
Q=x^2-xy+y^2. El objetivo es x^3+y^3+z^3=K.

## 1. Reduccion por divisores

La identidad x^3+y^3=S*Q demuestra que S divide K-z^3.
Ademas, 4Q=S^2+3V^2. Multiplicando por S:

    4(K-z^3)=S^3+3*S*V^2.

Por tanto, la identidad con signo del discriminante es:

    3*S*(4(K-z^3)-S^3)=(3*S*V)^2.

Lean formaliza la factorizacion, la divisibilidad y esta identidad en
`cube_sum_factorization`, `divisor_necessary` y `signed_discriminant`.

## 2. Paso al divisor positivo

Q es no negativo porque 4Q=S^2+3V^2. Para S distinto de cero, Q es
estrictamente positivo. Asi, S y K-z^3 tienen el mismo signo.
Sea d=abs(S). Entonces abs(K-z^3)=d*Q y d^2=S^2. Se obtiene:

    Delta=3*d*(4*abs(K-z^3)-d^3)=(3*d*V)^2.

`unsigned_discriminant` verifica esta igualdad para toda solucion,
incluido S=0. Es una igualdad necesaria, no una garantia de que cualquier
raiz modular produzca una solucion.

## 3. Reconstruccion suficiente

Se requiere que Delta sea un cuadrado r^2, que 3d divida r y que
S+V sea par, donde V=r/(3d) y S tiene el signo de K-z^3 y magnitud d.
Se define x=(S+V)/2, y=(S-V)/2. El programa comprueba finalmente
x^3+y^3+z^3=K con enteros exactos.

`reconstruction_sound` formaliza la suficiencia de las ecuaciones
2x=S+V, 2y=S-V y 3SV^2=4(K-z^3)-S^3. No formaliza la implementacion
Python de la raiz cuadrada ni de la division entera.

## 4. Cota finita

Si d>0, Delta>=0 implica d^3<=4*abs(K-z^3).
Por la desigualdad triangular:

    abs(K-z^3)<=abs(K)+abs(z)^3<=abs(K)+B^3,

cuando B>=0 y abs(z)<=B. Luego:

    d^3<=4*(B^3+abs(K)).

El caso d=0 satisface la desigualdad directamente.
`divisor_cube_bound` verifica esta cota. La implementacion utiliza la raiz
cubica entera inferior de 4*(B^3+abs(K)), sin redondeo de punto flotante.
Es una cota de d; no se exige que abs(x) y abs(y) esten acotados por B.

## 5. Rama S=0

Si S=0, entonces y=-x y K=z^3. Para un objetivo que no es cubo esta
rama es imposible. Si K es cubo, da la familia infinita (t,-t,cuberoot(K)).
`zero_sum_branch` verifica la condicion K=z^3. El cazador de resultados
finitos rechaza objetivos cubicos; el CLI directo informa esta familia.

## 6. Cobertura del algoritmo y limites de la formalizacion

La explicacion matematica del recorrido es: enumerar todos los d del
intervalo declarado, resolver z^3=K modulo d y recorrer sus progresiones
dentro de las bandas especificadas. Se incluyen raices singulares mediante
levantamiento completo y se combinan factores coprimos con CRT. Cada
candidato reconstruido se verifica con la identidad original.

Las pruebas Python comparan este recorrido contra enumeracion independiente.
Lean verifica los lemas algebraicos de arriba y cinco ternas conocidas.
No se ha formalizado la equivalencia de cada funcion Python con su
especificacion, la completitud de la rutina de raices modulares ni la
integridad de la ejecucion fisica de los barridos.

Los 35 registros negativos publicados son evidencia computacional limitada.
No constituyen una prueba formal de inexistencia global para ningun K.

## Compilar la formalizacion

Con elan y Lake instalados:

```sh
cd formal
lake update
lake exe cache get
lake build
```

El job `lean` de GitHub Actions ejecuta la compilacion. Solo su finalizacion
satisfactoria permite afirmar que el archivo formal fue comprobado.
`#print axioms` muestra las dependencias logicas de los teoremas principales.
El archivo no contiene `sorry`, `admit`, `native_decide` ni axiomas propios.


## Comprobacion confirmada

Los 12 teoremas (siete lemas y cinco controles conocidos) compilaron
correctamente en Lean 4.19.0, con Mathlib fijado al commit indicado en
el manifiesto. Los jobs Python y Lean finalizaron satisfactoriamente.

Evidencia: https://github.com/Iro007/suma-cubos/actions/runs/38106620320
Registro de versiones, archivo y axiomas observados:
[evidence/formal-verification.json](evidence/formal-verification.json).

El informe de la cota y de la reconstruccion muestra propext,
Classical.choice y Quot.sound; el control K=579 muestra propext y
Quot.sound. Ninguno de esos tres informes contiene sorryAx.


## Denominador minimo con tres fracciones positivas para K=114

Escribimos x=a/q, y=b/q, z=c/q, con q,a,b,c naturales positivos.
La ecuacion equivale a a^3+b^3+c^3=114*q^3. La equivalencia por eliminacion
del denominador tambien se expresa en Lean.

Para q<=5, la positividad implica a^3,b^3,c^3<=114*5^3=14250.
Como 25^3=15625>14250, cada numerador pertenece a {1,...,24}.
Se comprueba exhaustivamente que ningun q en {1,...,5} y ninguna terna
de esos numeradores satisface la ecuacion. La enumeracion finita se
comprueba por reduccion del kernel de Lean, sin recurrir a native_decide.

Para q=6, 13^3+14^3+27^3=24624=114*6^3. Las fracciones reducidas son
13/6,7/3,9/2, todas positivas. Existencia y exclusion de q<6 demuestran
la minimalidad. No se permite cancelar cubos positivos con negativos;
el teorema no cubre el problema de minimo denominador con signos libres.

## Altura minima computacional en enteros gaussianos

Para cada H se generan todos los (a,b) en [-H,H]^2. Su cubo es
(a^3-3ab^2,3a^2b-b^3). Se indexan los cubos por ambas componentes.
Para cada par de valores se busca el cubo complementario de 114+0i.
Se incluyen repeticiones y se ordenan indices para quitar solo permutaciones.
Si un cubo tiene mas de una preimagen, se conservan todas: no se presupone
inyectividad de la funcion cubo.

Para H=22 hay 2025 valores y 2051325 pares no ordenados con repeticion.
No hubo ternas. Todo dominio de altura menor esta contenido en ese cuadrado.
Para H=23 hay 2209 valores y 2440945 pares. Se hallo una unica terna salvo
permutaciones: (-23-10i,-23+10i,22).

Un segundo algoritmo usa pares ordenados, indice del tercer cubo solamente
por parte real y cubos calculados mediante multiplicaciones de pares.
Ambos resultados coinciden exactamente. Se verifica tambien el algoritmo
contra enumeracion directa de triples en cuadrados pequenos.

Esto demuestra minimalidad con el respaldo de una computacion exhaustiva
exacta. Lean certifica la igualdad del testigo y su altura 23, pero no la
completitud ni el resultado negativo de la enumeracion gaussiana.


## Verificacion de la ampliacion

Lean verifico los ocho teoremas nuevos, incluyendo la minimalidad del
denominador positivo 6, la equivalencia al eliminar denominadores y el
testigo gaussiano. El proyecto completo tiene 20 teoremas compilados.

Ejecucion: https://github.com/Iro007/suma-cubos/actions/runs/38108589020
La huella de cada archivo formal y el alcance estan en
[evidence/domains-formal-verification.json](evidence/domains-formal-verification.json).
La minimalidad gaussiana NO se incluye entre las pruebas Lean verificadas.
