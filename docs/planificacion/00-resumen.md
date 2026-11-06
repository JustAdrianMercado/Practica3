# Planificación — Práctica 3: Caja de los Enigmas (módulo de cerradura por voz)

Primer módulo del proyecto final **Escape Room IoT: La Caja de los Enigmas**. La caja tiene una tapa trabada por un **servo SG90** y un **reed switch** que detecta si la tapa está abierta. Alexa vincula la caja a cada usuario, responde por el estado de la tapa y de la cerradura, y abre o cierra la cerradura. Toda la comunicación pasa por el **Device Shadow** de AWS IoT Core.

**Entrega: martes 10/11/2026 a las 17:45** (enlace del repositorio por el LMS-UCB).

| Integrante | Área | Plan |
|---|---|---|
| Santiago Torres | Montaje y firmware del hardware | [01-santiago-hardware.md](01-santiago-hardware.md) |
| Adrián Mercado | Repositorio, AWS IoT y firmware de conectividad | [02-adrian-firmware-aws-iot.md](02-adrian-firmware-aws-iot.md) |
| Mateo Rojas | Lambda (backend de la skill) y DynamoDB | [03-mateo-lambda.md](03-mateo-lambda.md) |
| Lucía Escobar | Skill de Alexa, pruebas de voz y coordinación del informe | [04-lucia-skill-informe.md](04-lucia-skill-informe.md) |

## Calendario común

| It. | Fecha | Meta del grupo | Cierre |
|---|---|---|---|
| **0** | jue 06 – vie 07 (mañana) | **Esqueleto de punta a punta**: cada pieza existe y está conectada con la siguiente. | En el simulador, "¿cómo está la caja?" devuelve un dato publicado por el ESP32. |
| **1** | vie 07 | Objeto inteligente completo (RF1–RF3). | Se edita `desired` desde la consola de AWS y el servo se mueve; `reported` refleja el servo y la tapa. |
| **2** | sáb 08 | Skill y Lambda completas (RF4–RF9). | Vincular, consultar, abrir, cerrar, cambiar y desvincular desde el simulador. |
| **3** | dom 09 | Pruebas y mediciones de los RNF, evidencias, extensión opcional del acertijo. | Tablas de resultados con valores medidos y evidencias en `docs/evidencias/`. |
| **4** | lun 09 → mar 10 | Informe final, configuraciones exportadas, ensayo de demo y defensa. | Enlace entregado antes del 10/11 a las 17:45. |

## Reglas de trabajo

- **Cada uno hace commits con su propia cuenta de GitHub**: el docente usa el historial como evidencia en la defensa individual.
- Una rama por integrante y área (`feat/hardware`, `feat/firmware-aws`, `feat/lambda`, `feat/skill`); se integra a `main` con un **pull request revisado por otro integrante**.
- Commits pequeños y frecuentes, con mensajes en español que digan qué cambió (`firmware: aplicar delta del Shadow al servo`).
- **Nunca subir secretos**: certificados, clave privada, contraseña del WiFi ni access keys de AWS. Antes de cada push: `git status` y revisar que no aparezcan.
- Código modular (POO), comentado en español y siguiendo las convenciones del lenguaje (C++ en el firmware, PEP 8 en Python).
- Un **chat del grupo** para avisar cuando una pieza queda lista, porque desbloquea a otro integrante.
- **Defensa individual:** pueden preguntarle a cualquiera por cualquier parte. Cada plan termina con una lista de lo que hay que repasar de las demás áreas.

## Acuerdos iniciales (versión provisional)

La versión oficial queda en `docs/contratos.md`, que Adrián publica en la It. 0 y que los cuatro aprueban. Si alguien necesita cambiar un acuerdo, lo avisa en el grupo **antes** de cambiar su código.

**AWS:** todo en la región **us-east-1** (N. Virginia), que es donde debe estar la Lambda de una skill para América. Se usa una sola cuenta de AWS, la de Adrián, con un usuario IAM para cada integrante (nadie usa la cuenta raíz) y una alerta de facturación.

**Things:** `caja-enigmas-01`, `caja-enigmas-02`, … (dos dígitos).

**Shadow:**

| Atributo | Sección | Tipo | Valores | Quién lo escribe |
|---|---|---|---|---|
| `cerradura` | `desired` | string | `"abierta"` / `"cerrada"` | Lambda |
| `cerradura` | `reported` | string | `"abierta"` / `"cerrada"` | ESP32, después de mover el servo |
| `tapa` | `reported` | string | `"abierta"` / `"cerrada"` | ESP32 (reed switch) |
| `codigoVinculacion` | `reported` | string de 4 dígitos | `"0000"`–`"9999"` | ESP32 (se genera en el primer arranque y se guarda en NVS) |
| `firmware` | `reported` | string | `"0.1.0"` | ESP32 |

**Reporte:** por evento (cambio de tapa o de cerradura, en ≤1 s) y un reporte periódico de respaldo cada 60 s.

**DynamoDB:** tabla `CajaEnigmasVinculaciones`, con clave de partición `userId` (S) y los atributos `thingName` (S) y `fechaVinculacion` (S, ISO-8601 UTC).

**Skill (es-US):**
- Nombre de invocación: **"caja de enigmas"**.
- Intents: `VincularCajaIntent` (slots `numeroCaja`: `AMAZON.NUMBER` y `codigo`: `AMAZON.FOUR_DIGIT_NUMBER`), `DesvincularCajaIntent`, `ConsultarTapaIntent`, `ConsultarCerraduraIntent`, `AbrirCerraduraIntent` y `CerrarCerraduraIntent`.
- Intents integrados: `AMAZON.HelpIntent`, `AMAZON.CancelIntent`, `AMAZON.StopIntent`, `AMAZON.FallbackIntent` y `AMAZON.NavigateHomeIntent`.

**Lambda:** función `caja-enigmas-skill` en Python 3.12. Variables de entorno: `TABLA_VINCULACIONES`, `PREFIJO_THING=caja-enigmas-` e `IOT_ENDPOINT` (endpoint de datos `https://xxxx-ats.iot.us-east-1.amazonaws.com`).

**Hardware (Santiago lo confirma):**
- Señal del servo en GPIO 18. El servo se alimenta con 5 V de una fuente externa o del pin VIN, con **GND común con el ESP32**.
- Reed switch entre GPIO 4 y GND, con `INPUT_PULLUP`.

**Dependencias entre integrantes:**

```text
Adrián: Thing + certificados + política ──► ESP32 publica en el Shadow ──┐
Santiago: servo + reed probados ──► clases CerraduraServo/SensorTapa ──┴─► Objeto completo (It. 1)
Mateo: tabla + rol IAM + Lambda que lee el Shadow ──┐
Lucía: skill creada + modelo de interacción ────────┴─► Skill completa (It. 2)
```
