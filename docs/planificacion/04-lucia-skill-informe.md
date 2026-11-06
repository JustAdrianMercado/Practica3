# Plan de Lucía Escobar — Skill de Alexa, pruebas de voz y coordinación del informe

**Rama:** `feat/skill` · **Archivos a tu cargo:** `config/alexa/modelo-interaccion.es-US.json`, `docs/PLAN_PRUEBAS.md`, coordinación de `INFORME.md` · Ver los acuerdos en [00-resumen.md](00-resumen.md).

Sos la responsable de la parte que el usuario ve y escucha: la skill (invocación, intents, slots y frases), su conexión con la Lambda de Mateo y las pruebas de todas las frases. También coordinás el informe, porque es 1/3 de la nota.

## Iteración 0 — jue 06 / vie 07 (mañana): skill creada y conectada

1. En la **Alexa Developer Console** (developer.amazon.com), crear la skill **Custom** con idioma **Spanish (US)**, modelo *Custom* y backend *Provision your own*.
2. Nombre de invocación: **"caja de enigmas"**.
3. Crear un intent de prueba (por ejemplo `ConsultarTapaIntent` con 2–3 frases) y compilar el modelo (*Build*).
4. Copiar el **Skill ID** y pasárselo a Mateo para el disparador de la Lambda. En *Endpoint*, pegar el ARN de su función.
5. En la pestaña *Test*, activar el modo *Development* y probar "abre caja de enigmas".
6. Junto con Adrián, revisar el esqueleto de `INFORME.md` y la asignación de las secciones.

**Listo cuando:** el simulador recibe una respuesta de la Lambda, y al final de la It. 0 "¿cómo está la caja?" devuelve el dato publicado por el ESP32.

## Iteración 1 — vie 07: modelo de interacción completo

Definir los intents con los nombres acordados (no cambiarlos sin avisar a Mateo):

| Intent | Slots | Frases de ejemplo (poner 8–15 por intent) |
|---|---|---|
| `VincularCajaIntent` | `numeroCaja` (AMAZON.NUMBER), `codigo` (AMAZON.FOUR_DIGIT_NUMBER) | "vincula mi caja {numeroCaja} con el código {codigo}", "registra la caja {numeroCaja}" |
| `DesvincularCajaIntent` | — | "desvincula mi caja", "olvida mi caja" |
| `ConsultarTapaIntent` | — | "¿la tapa está abierta?", "¿cómo está la caja?" |
| `ConsultarCerraduraIntent` | — | "¿la cerradura está cerrada?", "¿está trabada la caja?" |
| `AbrirCerraduraIntent` | — | "abre la cerradura", "destraba la caja" |
| `CerrarCerraduraIntent` | — | "cierra la cerradura", "traba la caja" |
| Integrados | — | Help, Cancel, Stop, Fallback, NavigateHome |

- Configurar el **diálogo** de `VincularCajaIntent` con los dos slots obligatorios, para que Alexa pida los que falten ("¿cuál es el número de tu caja?", "¿cuál es el código que muestra?").
- Opcional: confirmación en `DesvincularCajaIntent`.
- Exportar el JSON del modelo (*JSON Editor*) a `config/alexa/modelo-interaccion.es-US.json` en cada cambio. Es un entregable.
- PR a `main`, revisado por Mateo.

## Iteración 2 — sáb 08: pruebas de voz e integración

- **`docs/PLAN_PRUEBAS.md`**: tabla con cada frase de ejemplo, la respuesta esperada, la respuesta obtenida y si pasó. Cubrir todos los casos: sin vincular, código incorrecto, caja inexistente, vincular, cambiar la vinculación, desvincular, consultas y comandos.
- Probarlas todas en el simulador y guardar capturas en `docs/evidencias/`.
- Probar **dos usuarios** con Mateo (modo *Manual JSON* con otro `userId`, o una segunda cuenta de Amazon como beta tester).
- Reportar a Mateo las frases que Alexa no entiende y ajustar el modelo.

## Iteración 3 — dom 09: mediciones y extensión

- Medición de **tiempo de respuesta extremo a extremo** con Santiago: grabar en video el simulador y la caja, 10 repeticiones, y calcular el promedio y el máximo (objetivo ≤3 s).
- Extensión opcional con Mateo: el **acertijo** antes de abrir (`ResponderAcertijoIntent` con un slot de respuesta). Es la base de la mecánica del Escape Room.

## Iteración 4 — lun 09 / mar 10: cierre del informe

**Coordinación de `INFORME.md`:**
- Revisar que estén todas las secciones del §4.2: caso de uso, requerimientos, diagramas (arquitectura, circuito, clases y secuencia), Shadow, vinculación, skill, desarrollo, configuraciones, pruebas, resultados, conclusiones, recomendaciones y anexos.
- Unificar el estilo y comprobar que los enlaces al código funcionen.
- Controlar la **matriz de trazabilidad**: cada RF y RNF debe tener su diseño, su código y su prueba (formato de Practica2).

**Tus secciones:**
- **Caso de uso y requerimientos**, junto con Santiago para la justificación del sensor y del actuador.
- **Diseño de la skill**: invocación, intents, slots y frases.
- **Diagramas de secuencia**: vinculación, consulta del sensor y comando al actuador, del usuario al ESP32 (en mermaid, junto con Mateo).
- **Configuración de Alexa**.
- **Pruebas**, **resultados**, **conclusiones** y **recomendaciones**, incluidas las extensiones hacia el Escape Room.

**Entrega:** enviar el enlace del repo por el LMS antes del **martes 10/11 a las 17:45**, después de comprobar que el docente puede acceder.

## Para la defensa: qué repasar de los demás

- Qué hace la Lambda con el `userId` y cómo valida el Thing y el código.
- `desired`, `reported` y `delta`, y qué pasa si la caja está desconectada cuando se da la orden.
- Cómo se conecta el ESP32 (TLS con certificados, política de IoT) y la reconexión.
- El circuito: servo, alimentación y reed switch.
