# Plan de Santiago Torres — Montaje y firmware del hardware

**Rama:** `feat/hardware` · **Archivos a tu cargo:** `firmware/include|src/CerraduraServo.*`, `firmware/include|src/SensorTapa.*`, `docs/diagramas/circuito.*`, `docs/GUIA_MONTAJE.md`, `docs/PRUEBAS_FISICAS.md` · Ver los acuerdos en [00-resumen.md](00-resumen.md).

Sos el responsable de que la caja exista físicamente y de que el servo y el sensor funcionen. Adrián se encarga de la conexión con AWS. Tus dos clases son las que él usa desde `main.cpp`.

## Materiales

- ESP32 DOIT DEVKIT V1, servo SG90, reed switch con imán, protoboard y cables.
- Fuente de 5 V para el servo (un cargador USB con cable cortado o un módulo regulador). Con USB el servo puede funcionar desde VIN, pero sus picos de corriente pueden reiniciar el ESP32.
- Un capacitor electrolítico de 470–1000 µF entre los 5 V y el GND del servo, como recomendación contra esos picos.
- La caja (cartón duro, MDF o una caja de madera) y un pestillo: el brazo del servo traba una pestaña de la tapa.

## Iteración 0 — jue 06 / vie 07 (mañana): hardware probado

1. Con un sketch de prueba simple (no hace falta que quede en el repo), mover el servo entre dos ángulos y **elegir los ángulos de "cerrada" y "abierta"** que traban y destraban de verdad la tapa. Anotarlos.
2. Leer el reed switch con `INPUT_PULLUP` por Serial y comprobar que cambia al abrir la tapa. Anotar **qué valor lógico corresponde a "tapa cerrada"**.
3. Confirmar o cambiar los pines (servo en GPIO 18, reed en GPIO 4) y la forma de alimentar el servo. **Avisarle a Adrián** para que quede en `docs/contratos.md`.
4. Fijar el servo, el imán y el reed en la caja.

**Listo cuando:** el servo traba y destraba la tapa, y el Serial muestra el cambio del reed al abrirla.

## Iteración 1 — vie 07: clases del hardware

Adrián ya habrá subido la estructura del repo y `platformio.ini` (con la biblioteca `ESP32Servo`). Crear tu rama desde `main`:

- **`CerraduraServo`** (actuador):
  - `CerraduraServo(uint8_t pin, int anguloCerrada, int anguloAbierta)`
  - `iniciar()`, `abrir()`, `cerrar()`, `estaAbierta() const`
  - `aplicar(const char* estado)`: acepta `"abierta"` o `"cerrada"`, devuelve `false` con un valor inválido y no mueve nada en ese caso.
  - Al iniciar queda **cerrada**. Tras moverse, conviene desconectar el PWM (`detach`) para que el servo no zumbe ni consuma de más.
- **`SensorTapa`** (sensor):
  - `SensorTapa(uint8_t pin)`, `iniciar()`, `actualizar()`, `estaAbierta() const`, `huboCambio()`
  - **Antirrebote** de unos 50 ms, sin `delay()`, usando `millis()`. `huboCambio()` devuelve `true` una sola vez por cada cambio confirmado: Adrián lo usa para el reporte inmediato.
- Seguir el estilo de PracticaMQTT (`SensorUltrasonico.h`, `ControlLeds.h`): constructor que solo guarda los pines, `iniciar()` que toca el hardware, y comentarios breves en español.
- Hacer un PR a `main` y pedirle la revisión a Adrián. Probar juntos la integración con `main.cpp`.

**Listo cuando:** al cambiar `desired.cerradura` desde la consola de AWS, el servo se mueve y `reported.tapa` cambia al abrir la caja con la mano (prueba conjunta con Adrián).

## Iteración 2 — sáb 08: circuito y guía de montaje

- **Diagrama del circuito** con ESP32, servo, alimentación, capacitor y reed (Fritzing, Wokwi o el SVG de Practica2 como modelo), en `docs/diagramas/`.
- **`docs/GUIA_MONTAJE.md`**: lista de materiales, conexiones pin a pin, ángulos calibrados y fotos del montaje. El formato de Practica2 sirve de modelo.
- Ordenar el cableado: el montaje ordenado y seguro se evalúa en la demo.

## Iteración 3 — dom 09: mediciones físicas (RNF)

Registrar todo en `docs/PRUEBAS_FISICAS.md`, con fotos y videos en `docs/evidencias/`:

| Prueba | Procedimiento | Resultado esperado |
|---|---|---|
| Exactitud del sensor | 30 aperturas y cierres de la tapa, comparando el estado real con el `reported.tapa`. Medir con regla la distancia del imán a la que conmuta el reed. | 30/30 correctos y la distancia de conmutación en mm. |
| Tiempo de respuesta | Grabar en video la pantalla del simulador junto a la caja y medir desde que termina la orden hasta que el servo se mueve. 10 repeticiones. Hacerlo con Lucía. | ≤3 s de máximo. |
| Estabilidad | Caja conectada ≥10 minutos con órdenes cada minuto, observando el Serial. | 0 reinicios. |
| Consumo del servo | Opcional: corriente con un multímetro en reposo y en movimiento. | Justifica la alimentación elegida. |

## Iteración 4 — lun 09 / mar 10: informe y ensayo

- Redactar en `INFORME.md` el **diagrama de circuito**, la justificación del sensor y del actuador (junto con Lucía) y la parte de montaje.
- Ensayar la demo con la caja: llevar repuestos (cables y un segundo servo si hay).

## Para la defensa: qué repasar de los demás

- Cómo llega una orden desde Alexa hasta el servo: intent → Lambda → `UpdateThingShadow` (`desired`) → `delta` → ESP32 → `reported`.
- Qué son `desired`, `reported` y `delta`, y qué pasa si el ESP32 estaba desconectado.
- Por qué TLS con certificados y qué permite la política de IoT.
- Cómo funciona la vinculación con el código de 4 dígitos y la tabla de DynamoDB.
