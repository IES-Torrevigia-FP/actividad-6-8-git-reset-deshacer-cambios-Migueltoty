# 🧨 Actividad 6.8 – `git reset`: deshacer cambios y reescribir historia local

> En actividades anteriores has aprendido a avanzar en el historial (`commit`, `merge`, `rebase`).
> Ahora vas a aprender a **retroceder** con seguridad usando `git reset`, diferenciando `--soft`, `--mixed` y `--hard`.

---

## 🎯 Objetivos de la actividad

Al finalizar esta actividad serás capaz de:

- Explicar qué hace `git reset` y en qué se diferencia de `git revert`.
- Usar `git reset --soft`, `git reset` (mixed, por defecto) y `git reset --hard` en casos sencillos.
- Deshacer el último commit dejando cambios staged, unstaged o descartados según convenga.
- Entender cuándo es peligroso usar `git reset --hard`.

---

## 🧠 Conceptos clave: estados y tipos de reset

Recuerda los tres “espacios” de Git:

- **HEAD / historial de commits**: lo que ya está confirmado.
- **Staging area (index)**: cambios preparados para el próximo commit.
- **Working directory**: archivos tal como están ahora en tu disco.

`git reset` mueve la referencia `HEAD` a otro commit y puede afectar también a staging y working directory, según el modo:

| Modo                    | HEAD  | Staging (index)                   | Working directory                  |
| ----------------------- | ----- | --------------------------------- | ---------------------------------- |
| `--soft`                | Mueve | Conserva cambios staged           | Conserva archivos tal cual         |
| `--mixed` (por defecto) | Mueve | Deshace staging (pasa a unstaged) | Conserva archivos tal cual         |
| `--hard`                | Mueve | Resetea index                     | Resetea archivos (pierdes cambios) |

---

## 🧩 Parte 1 – Preparar un historial con varios commits

### Reto 1.1 – Crear el escenario

1. Crea una carpeta para esta actividad:

   ```bash
   mkdir actividad-6-8-git-reset
   cd actividad-6-8-git-reset
   ```

2. Inicializa el repositorio:

   ```bash
   git init
   ```

3. Crea `progreso.txt` con:

   ```text
   Paso 1: estructura inicial del proyecto.
   ```

4. Añade y haz commit:

   ```bash
   git add progreso.txt
   git commit -m "Paso 1: estructura inicial"
   ```

5. Añade más pasos con commits separados:
   - Paso 2:

     ```bash
     echo "Paso 2: añade módulo de login." >> progreso.txt
     git add progreso.txt
     git commit -m "Paso 2: módulo de login"
     ```

   - Paso 3 (con un mensaje poco claro a propósito):

     ```bash
     echo "Paso 3: refactoriza código de login." >> progreso.txt
     git add progreso.txt
     git commit -m "fix cosas"
     ```

   - Paso 4:

     ```bash
     echo "Paso 4: añade módulo de registro de usuarios." >> progreso.txt
     git add progreso.txt
     git commit -m "Paso 4: registro de usuarios"
     ```

6. Revisa el historial:

   ```bash
   git log --oneline
   ```

### Checkpoint 1 – Evidencia

- Crea `cp1-historial-inicial.txt` con la salida de `git log --oneline`.

---

## 🧩 Parte 2 – `git reset --soft`: deshacer commits manteniendo cambios staged

### Reto 2.1 – Rehacer el último commit en dos commits más limpios

Imagínate que el último commit (`Paso 4`) debería separarse o rehacerse.

1. Ejecuta:

   ```bash
   git reset --soft HEAD~1
   ```

   Esto mueve `HEAD` al commit anterior, pero mantiene los cambios del último commit **en staging**.

2. Comprueba:

   ```bash
   git status
   ```

   Verás cambios preparados para commit (staged), pero el mensaje “Paso 4” ya no está en el historial.

3. Haz un nuevo commit con un mensaje mejor:

   ```bash
   git commit -m "Paso 4: registro de usuarios (mejorado)"
   ```

4. Revisa:

   ```bash
   git log --oneline
   ```

### Checkpoint 2 – Evidencia

- Crea `cp2-soft-reset.txt` con:
  - La salida de `git status` inmediatamente después de `git reset --soft HEAD~1`.
  - La salida de `git log --oneline` después del nuevo commit.
  - Una frase explicando qué ha hecho exactamente `--soft` (qué se ha tocado y qué no).

---

## 🧩 Parte 3 – `git reset` (mixed): deshacer commit y volver a unstaged

### Reto 3.1 – Deshacer el commit “fix cosas”

Ahora queremos rehacer el commit “fix cosas” y decidir con calma qué va en el siguiente commit.

1. Localiza el hash del commit anterior a “fix cosas” en `git log --oneline`.
   Por ejemplo, si el historial es:

   ```text
   abc1234 Paso 4: ...
   def5678 fix cosas
   ghi9012 Paso 2: ...
   ...
   ```

2. Ejecuta un **mixed reset** hasta el commit anterior a “fix cosas”, por ejemplo:

   ```bash
   git reset HEAD~2
   ```

   (ajusta el número según tu historial real; el objetivo es dejar fuera “fix cosas” y el commit posterior)

   Sin especificar modo, `git reset` usa `--mixed` por defecto.

3. Comprueba:

   ```bash
   git status
   ```

   Verás cambios **sin preparar** (unstaged) en el working directory, correspondientes a los commits deshechos.

4. Decide qué volver a commitear, por ejemplo:

   ```bash
   git add progreso.txt
   git commit -m "Paso 3 y 4: cambios revisados"
   ```

### Checkpoint 3 – Evidencia

- Crea `cp3-mixed-reset.txt` con:
  - Explicación breve de qué partes del historial han desaparecido temporalmente.
  - Salida de `git status` justo después de `git reset HEAD~...`.
  - Una frase comparando `--soft` y `mixed` respecto a staging y working directory.

---

## 🧩 Parte 4 – `git reset --hard`: volver atrás y descartar cambios

> ⚠️ Esta parte es **peligrosa**: vas a usar `--hard` en un entorno de práctica. Nunca lo hagas sin pensar en repositorios reales.

### Reto 4.1 – Crear cambios y descartarlos con `--hard`

1. Asegúrate de que tu historial está limpio y sin cambios pendientes:

   ```bash
   git status
   ```

2. Haz cambios sin commitear:

   ```bash
   echo "Línea experimental: no debería quedarse." >> progreso.txt
   git add progreso.txt
   echo "Otra línea que tampoco debería quedarse." >> progreso.txt
   ```

   Ahora tienes cambios staged y unstaged.

3. Comprueba:

   ```bash
   git status
   ```

4. Ejecuta:

   ```bash
   git reset --hard HEAD
   ```

   Esto resetea HEAD, index y working directory al commit actual, descartando todos los cambios.

5. Comprueba de nuevo:

   ```bash
   git status
   cat progreso.txt
   ```

   Las líneas experimentales habrán desaparecido.

### Checkpoint 4 – Evidencia

- Crea `cp4-hard-reset.txt` con:
  - Una explicación de qué ha ocurrido con los cambios staged y unstaged tras `--hard`.
  - El contenido actual de `progreso.txt`.
  - Una frase indicando por qué `git reset --hard` se considera “opción nuclear”.

---

## 🧩 Parte 5 – `git reset HEAD` para deshacer staging

### Reto 5.1 – Solo sacar archivos del staging area

1. Modifica `progreso.txt` con una línea nueva y añádela:

   ```bash
   echo "Paso extra: documentación." >> progreso.txt
   git add progreso.txt
   ```

2. Comprueba:

   ```bash
   git status
   ```

3. Usa:

   ```bash
   git reset HEAD progreso.txt
   ```

   Esto **solo deshace el `git add`**, pasando los cambios de staged a unstaged, sin tocar el contenido del archivo.

4. Comprueba:

   ```bash
   git status
   ```

### Checkpoint 5 – Evidencia

- Crea `cp5-reset-head.txt` con:
  - Salida de `git status` antes y después de `git reset HEAD progreso.txt`.
  - Una explicación de cuándo te resulta útil “deshacer el add” sin perder cambios.

---

## 🧩 Parte 6 – Reflexión final: reset vs revert

Crea `reflexion-6-8.md` y responde:

1. Explica con tus palabras las diferencias entre:
   - `git reset --soft`
   - `git reset` (mixed)
   - `git reset --hard`
2. ¿Por qué `git reset` se suele usar **solo en local** y antes de compartir cambios, mientras que `git revert` es más seguro en ramas compartidas?
3. Describe una situación real en la que usarías:
   - `--soft`
   - `mixed`
   - `--hard` (en un entorno controlado).

---

## 📦 Entrega esperada en el repositorio

Tu repositorio de la Actividad 6.8 debe incluir:

- `progreso.txt` (versión final).
- `cp1-historial-inicial.txt`
- `cp2-soft-reset.txt`
- `cp3-mixed-reset.txt`
- `cp4-hard-reset.txt`
- `cp5-reset-head.txt`
- `reflexion-6-8.md`

---

## 🏁 Evaluación sugerida

- 4 pts – Uso correcto de `git reset --soft`, `git reset` (mixed) y `git reset --hard`, y de `git reset HEAD`.
- 3 pts – Evidencias claras en los archivos de checkpoints.
- 3 pts – Calidad de la reflexión en `reflexion-6-8.md` (comprender riesgos y buenas prácticas).

**Puntuación máxima: 10 puntos.**

---

## 🤖 Evaluación automática y redacción de informe

Esta actividad incluye una evaluación automática similar a la de la actividad anterior, adaptada a `git reset` y a sus modos `--soft`, `mixed` y `--hard`:

- Workflow: `.github/workflows/evaluacion.yml`
- Script de evaluación: `tools/evaluar_repo.py`
- Script de redacción IA: `tools/ai_redactor.py`

### ¿Qué genera?

Al ejecutarse en GitHub Actions, se generan los siguientes archivos en `reportes/`:

- `informe.md` (resumen técnico de evaluación)
- `informe.json` (métricas en formato estructurado)
- `metricas.csv` (puntuaciones por criterio)
- `arbol.txt` (resumen del árbol del repositorio)

Si hay credenciales de IA configuradas en Secrets/Variables, también se generan:

- `retro.md` (retroalimentación redactada por IA)
- `retro.docx` (versión formal en Word)

### Parámetros del workflow (`workflow_dispatch`)

- `min_commits` (por defecto: `6`)
- `required_files` (por defecto: `progreso.txt,cp1-historial-inicial.txt,cp2-soft-reset.txt,cp3-mixed-reset.txt,cp4-hard-reset.txt,cp5-reset-head.txt,reflexion-6-8.md`)

---
