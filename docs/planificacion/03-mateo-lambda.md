# Plan de Mateo Rojas — Lambda (backend de la skill) y DynamoDB

**Rama:** `feat/lambda` · **Archivos a tu cargo:** `lambda/**`, `config/aws/politica-rol-lambda.json`, `config/aws/tabla-vinculaciones.json` · Ver los acuerdos en [00-resumen.md](00-resumen.md).

Sos el responsable del "cerebro" de la skill: recibe el intent de Alexa, resuelve qué caja tiene el usuario, lee o modifica su Shadow y arma la respuesta en español. La Lambda **nunca habla con el ESP32**: solo lee y escribe el Shadow.

## Iteración 0 — jue 06 / vie 07 (mañana): Lambda mínima conectada a AWS

Adrián te crea un usuario IAM en la cuenta del grupo y te pasa el endpoint de datos de IoT.

1. **DynamoDB:** crear la tabla `CajaEnigmasVinculaciones` con clave de partición `userId` (String) y capacidad *on-demand*. Exportar su definición a `config/aws/tabla-vinculaciones.json`.
2. **Rol IAM** `caja-enigmas-lambda-rol`: `AWSLambdaBasicExecutionRole` (logs) más una política propia con `iot:GetThingShadow`, `iot:UpdateThingShadow` e `iot:DescribeThing` sobre `arn:aws:iot:us-east-1:<cuenta>:thing/caja-enigmas-*`, y `dynamodb:GetItem`, `PutItem` y `DeleteItem` sobre la tabla. Guardar el JSON en `config/aws/politica-rol-lambda.json`.
3. **Lambda** `caja-enigmas-skill` (Python 3.12, us-east-1, ese rol), con las variables de entorno `TABLA_VINCULACIONES`, `PREFIJO_THING=caja-enigmas-` e `IOT_ENDPOINT`.
4. Primera versión que lee el Shadow de `caja-enigmas-01` con `boto3.client("iot-data", endpoint_url=IOT_ENDPOINT).get_thing_shadow(...)` y responde a un `LaunchRequest`.
5. Agregar el **disparador "Alexa Skills Kit"** con el *Skill ID* que te pasa Lucía (verificación del ID activada).

**Listo cuando:** una prueba desde la consola de Lambda devuelve el Shadow sin errores de permisos, y Lucía recibe respuesta desde el simulador.

## Iteración 1 — vie 07: estructura del código y servicios

Estructura orientada a objetos con `ask-sdk-core`:

```text
lambda/
  lambda_function.py          SkillBuilder: registra manejadores y el manejador de errores
  manejadores/                Una clase por intent (AbstractRequestHandler)
  servicios/
    repositorio_vinculaciones.py   obtener(userId), guardar(userId, thingName), eliminar(userId)
    servicio_shadow.py             leer_reported(thing), pedir_cerradura(thing, estado)
    servicio_registro.py           existe_thing(thing) -> bool  (DescribeThing)
  textos.py                   Frases de respuesta en español, en un solo lugar
  requirements.txt            ask-sdk-core
  tests/                      unittest con boto3 simulado (mocks)
```

- Los servicios reciben el cliente de boto3 en el constructor, así se reemplaza por un mock en los tests (mismo estilo que los tests del `mcp_server` de PracticaMQTT).
- `pedir_cerradura` hace `update_thing_shadow` con `{"state": {"desired": {"cerradura": "abierta"}}}`.
- Tests de cada servicio: Thing inexistente (`ResourceNotFoundException`), Shadow sin `reported`, usuario sin vinculación.
- Ejecutar con `py -m unittest discover -s lambda/tests -v`.

**Empaquetado:** `pip install -r requirements.txt -t paquete/`, copiar el código y comprimirlo en un zip para subirlo. Documentar el comando en `lambda/README.md`.

## Iteración 2 — sáb 08: manejadores (RF4–RF9)

| Intent | Comportamiento |
|---|---|
| `LaunchRequest` | Da la bienvenida. Si el usuario no tiene caja vinculada, le explica cómo vincularla (RF8). |
| `VincularCajaIntent` | `thingName = PREFIJO + f"{numeroCaja:02d}"`; comprueba que exista con `DescribeThing` (RF9); compara `codigo` con `reported.codigoVinculacion`; si coincide, guarda en DynamoDB con `fechaVinculacion` (RF7). Si ya tenía una caja, la reemplaza (cambiar la vinculación). |
| `DesvincularCajaIntent` | `DeleteItem` (RF9). Conviene pedir confirmación. |
| `ConsultarTapaIntent` | Lee `reported.tapa` (RF4). |
| `ConsultarCerraduraIntent` | Lee `reported.cerradura` (RF6). Si hay un `desired` distinto todavía no aplicado, avisa: "la caja todavía no confirmó la orden". |
| `AbrirCerraduraIntent` / `CerrarCerraduraIntent` | Escribe en `desired` (RF5). Opcional: esperar ~1,5 s y volver a leer para confirmar. |
| Help / Cancel / Stop / Fallback / SessionEnded | Respuestas estándar en español. |
| Manejador de errores | Mensaje amable y log en CloudWatch, sin datos sensibles. |

- Todo intent que necesita una caja **resuelve primero la vinculación** a partir de `context.System.user.userId`. Si no la hay, guía al usuario a vincular.
- Probar **dos usuarios distintos**: con tests y con el simulador en modo *Manual JSON* cambiando el `userId`, sobre `caja-enigmas-01` y `caja-enigmas-02`.
- PR a `main`, revisado por Lucía.

## Iteración 3 — dom 09: pruebas

- Plan de pruebas de la Lambda: cada intent con usuario vinculado, sin vincular, código incorrecto, Thing inexistente y caja desconectada.
- Medir en los logs de CloudWatch la duración de la Lambda (es parte de los ≤3 s de extremo a extremo).
- Extensión opcional junto con Lucía: el **acertijo** antes de abrir (`ResponderAcertijoIntent`, respuesta validada en la Lambda y guardada en atributos de sesión).

## Iteración 4 — lun 09 / mar 10: informe

- Redactar en `INFORME.md`: el **diagrama de clases de la Lambda**, el **diseño de la vinculación** (identificador, modelo de la tabla y validaciones), la configuración de la Lambda, DynamoDB y el rol IAM, y la **justificación de los permisos**: cuáles se dieron, por qué y cuáles serían los mínimos en producción.
- El diagrama de secuencia de la vinculación, junto con Lucía.

## Para la defensa: qué repasar de los demás

- `desired`, `reported` y `delta`: qué hace el ESP32 cuando recibe el `delta` y por qué hace `/get` al reconectar.
- Cómo se autentica el ESP32 (certificados) y qué permite la política de IoT.
- El circuito y la alimentación del servo.
- El modelo de interacción: intents, slots y frases de ejemplo.
