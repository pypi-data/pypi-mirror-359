# Carmen Puta Rastrera (CarmenPR)

**Un módulo de python para demostrar mi odio por carmen (y realizar alguna que otra cosa útil).**

---

## 💔 Llamada a la comunidad de desarrolladores despechados

¿Hay alguien a quien odias con la fuerza de mil `raise Exception()`?
¿Una ex, un ex, un crush, un mejor amigo que dejó de serlo, una ilusión que te dejó en modo `None`?

Pues añade LO QUE QUIERAS A carmenPR para odiarlo, deja un pull request sin problema.
Porque Carmen PR puede haber sido la primera... **pero no tiene por qué ser la última**.

### 😈 El Registro Global de Personas Odiadas

Agrega a la persona que te destrozó emocionalmente con una simple línea de código:

```
pr.odiar("Kevin", "Me dejó por una tía que decía 'jeje' en vez de reírse")
```

Esa persona se añade al archivo interno `CARMEN_BLACKLIST.py`, para que:

* Sea utilizada como objeto de burlas automáticas.
* Reciba culpa aleatoria cuando algo falle.
* Puedas canalizar tu ira sin romper platos (solo variables).

Y LUEGO SE SUBE A LA NUBE DE ODIO PARA QUE TODOS PODAMOS TENER UNA COPIA EN NUESTRO MÓDULO.
¡Entre todos podemos convertir este módulo en el museo del despecho digital!
**Odiar con estilo nunca fue tan fácil.**

---

## 💡 ¿Qué es `Carmen PR`?

Es un módulo de Python lleno de funciones útiles, absurdas y emocionalmente inestables.
Mitad herramientas reales, mitad easter eggs, 100% desprecio hacia Carmen PR (también conocida como **la Puta Rastrera**).

> ¿Podría haber escrito un libro desahogarme? Sí.
> ¿Una canción? Quizá.
> ¿Una carta sincera? Jamás.
>
> Así que hice lo único que sé hacer: **un módulo de Python para odiar y sobrevivir.**

---


## 📖 Historia real (pero exagerada por salud mental)

Carmen PR fue una tía que me hizo sentir cosas que ya ni los ventiladores térmicos de mi GPU consiguen provocar.
Me hizo creer que el amor era mutuo. Que hablábamos de verdad. Que algo iba a pasar.
Y luego, como si fuera un commit sin push, **desapareció**.
No error, no log, no nada.

Así que, sin poder componer, sin querer llorar más, sin ganas de escribir un diario...
...decidí **convertirla en software**.
Así, si me vuelve a dejar, al menos podré hacerle un `pip uninstall carmenpr`.

Este módulo es un acto de resistencia, un altar al despecho, una risa en la oscuridad.
Y sí, también tiene funciones útiles. ¡Faltaría más!

---

## 📦 Instalación

¿Te atreves?

```
pip install carmenpr
```

(Este comando instalará el rencor en tu sistema. No nos hacemos responsables de los sentimientos que puedan surgir.)

---

## 🔧 Uso básico

```python
import carmenpr as pr
```

¿PR? Porque es la abreviatura oficial de **Puta Rastrera**.
Y no lo digo yo, lo dice la documentación emocional no oficial del alma.

---

## 🎁 Ejemplos de funciones

```python
pr.expandir("odiadorDeCarmen.py")
```

Convierte `odiadorDeCarmen.py` en un submódulo usable desde Carmen PR.
Ideal para no tener que copiar y pegar como un cavernícola emocional.

---


```python
pr.llorar()
```

Ejecuta un `while True:` que imprime frases dolorosas mientras suena mentalmente “November Rain” en tu alma.
Frases como:

* “¿Por qué sigo soñando con Carmen si ya ni recuerdo su voz?”
* “¿Y si fui yo el problema?”
* “¿Y si era ella... pero sin PR?”

---

```python
pr.odiar("Carmen PR")
```

Guarda el nombre en una tabla especial y genera insultos pasivo-agresivos cada vez que ejecutas otro script.

Ejemplo de salida:

```
Recordatorio: Carmen PR sigue siendo una decepción en el sistema.
```

---


## 📜 Resumen de funciones actuales de CarmenPR

### 🔥 1. pr.decir_palabrota()
Insulta aleatoriamente o lanza un odio directo hacia Carmen.

**Ejemplo:**
```python
pr.decir_palabrota()
# → "Eres como CarmenPR en lunes por la mañana."
```

---

### 🎭 2. pr.generar_alias(original, alias, modo)
Asocia una palabra con otra como un apodo.

- Modos: "temporal", "local", "global"

**Ejemplo:**
```python
pr.generar_alias("Pepe", "Paco", "temporal")
```

---

### 🔁 3. pr.equivalente(palabra, n=None)
Devuelve una de las asociaciones para esa palabra. Si hay varias, una aleatoria o puedes pasar n para elegir cuál.  
Si no hay segundo argumento (índice), se da una random.

**Ejemplo:**
```python
pr.generar_alias("Paco", "Pepe", "global")
pr.generar_alias("Paco", "Alfonso", "global")
pr.equivalente("Paco")
# → "Alfonso" o "Pepe"

pr.equivalente("Paco", n=1)
# → "Pepe"
```

---

### 📜 4. pr.ver_asociaciones(palabra=None)
Lista todas las asociaciones existentes o solo de una palabra concreta.

**Ejemplo:**
```python
pr.ver_asociaciones("Paco")
# → ['Pepe', 'Alfonso']
```

---

### 🧃 5. pr.agrupador(nombre_grupo, elementos, modo)
Crea grupos de palabras que se pueden identificar como del mismo conjunto.

- Modos: "temporal", "local", "global"

**Ejemplo:**
```python
pr.agrupador("Manzana", ["roja", "verde"], "global")
```

---

### 🔍 6. pr.a_que_grupo_pertenece(palabra)
Detecta a qué grupo pertenece un valor agrupado.

**Ejemplo:**
```python
pr.a_que_grupo_pertenece("verde")
# → "Manzana"
```

---

### 🧩 7. pr.acoplar(ruta_archivo)
Inserta el contenido completo de un archivo Python como si estuviera escrito en esa línea.  
Ideal para APIs partidas en muchos archivos. Es como un import literal.

**Ejemplo:**
```python
pr.acoplar("servicio_musica.py")
```

---

### 📂 8. pr.expandir(nombre_archivo)
Importa dinámicamente todas las funciones públicas de un archivo y las registra en el módulo.

**Ejemplo:**
```python
pr.expandir("funciones_extra.py")
```

---

### ✂️ 9. pr.recortar(nombre_archivo)
Elimina el contenido importado por expandir() y actualiza el __init__.py.

**Ejemplo:**
```python
pr.recortar("funciones_extra.py")
```

---

### ⚙️ 10. pr.configurar(nombre_regla, valor)
Cambia el comportamiento del módulo.

- Ejemplo de regla:  
  "devolver_si_no_hay_asociacion" → "None" o "palabra"

**Ejemplo:**
```python
pr.configurar("devolver_si_no_hay_asociacion", "None")
```

---

### ⏳ 11. pr.va_a_tardar()
Abre una consola que muestra mensajes de odio subidos por la comunidad. Puedes responderlos.  
Se mantiene activo hasta que se llama a pr.terminado()

---

### ✅ 12. pr.terminado()
Cierra la consola de va_a_tardar cuando el proceso principal ha finalizado.

---

### 💀 13. pr.carmen()
Obtiene el nombre de usuario actual de Carmen en Instagram a partir de su ID numérico (que nunca cambia), usando la API interna de Instagram.  
Consulta la API simulada en `esfake.duction.es:6062/carmenPR` para comprobar si eres el primero en detectar un nuevo nombre. Si es así, puedes dejar un comentario de odio único, que se guardará junto al nombre y tu usuario en el historial del servidor.

**Ejemplo:**
```python
pr.carmen()
# Salida: "Su nueva cuenta es: @mecreoqueescondo_peorqueun_hamster"
# Si eres el primero: "¡Enhorabuena! Fuiste el primero en encontrar el nuevo nombre de CarmenPR."
# Se te pedirá un comentario de odio y tu nombre, que se enviarán al servidor.
```
- (Opcional) Puede abrir el perfil en el navegador automáticamente.
- No hace nada ilegal, solo usa un endpoint público de la app de Instagram.

---

### 💭 IDEAS futuras o en desarrollo:
- 🐣 pr.subir_easter_egg("texto", "autor"): añadir mensajes o chistes secretos.
- 📩 pr.mandar_mensaje_de_apoyo(id, texto): responde a otros usuarios random que se desahogaron.
- 💬 pr.ver_mensajes_random(): muestra experiencias de odio hacia CarmenPR subidas por otros.

---

## 💌 Licencia

Este módulo está bajo la **LOVE LICENSE™**.
Un acuerdo emocional que te permite usar este módulo si:

* Amas a todos*
*Menos a carmenPR

Consulta el archivo `LICENCIA.md` para llorar legalmente.

---

## 🤝 Contribuciones

¿Tienes funciones útiles y tristes?
¿Quieres ayudar a otros a vengarse con elegancia?
¿Tu ex programaba en PHP y sientes que eso ya es suficiente trauma?

Haz un pull request.
Abre una issue.
**Deja que tu corazón roto colabore.**

---

## 🧠 ¿Por qué usar `Carmen PR`?

Porque:

* Funciona.
* Es raro.
* Y porque no hay nada más hermoso que el código que nace de un corazón partido.

> "Ella me dejó, pero yo le dejé una librería open source."

---

## 🧨 Final

No somos robots.
No somos mensajes en instagram.
Somos humanos... y Carmen PR lo olvidó.

Pero no pasa nada.

**Porque ahora he aprendido a no enamorame jamás. Y el código no lo olvida.**

---

`pip install carmenpr`
Y si alguien pregunta qué hace este módulo, respóndeles:

> “Lo único que no hizo Carmen PR: algo útil.”

