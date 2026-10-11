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
