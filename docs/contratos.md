# Contratos entre componentes

Este documento fija los nombres, formatos y reglas que comparten el firmware, la Lambda y la skill, para que cada integrante trabaje en paralelo. **Si alguien necesita cambiar algo de aquí, lo avisa en el grupo antes de cambiar su código** y actualiza este archivo en el mismo PR.

| Estado | Responsables de aprobar |
|---|---|
| Borrador v0.1 (06/11/2026) | ☐ Santiago · ☐ Adrián · ☐ Mateo · ☐ Lucía |

## 1. AWS

| Elemento | Valor |
|---|---|
| Región | `us-east-1` (N. Virginia), para todo: IoT Core, Lambda y DynamoDB. |
| Cuenta | Una sola cuenta del grupo, con un usuario IAM por integrante; nadie usa la cuenta raíz ni crea access keys. |
| Nombre de los Things | `caja-enigmas-NN`, con dos dígitos: `caja-enigmas-01`, `caja-enigmas-02`, … |
| Política de IoT | `CajaEnigmasPolitica` ([config/aws/politica-iot.json](../config/aws/politica-iot.json)), asociada al certificado de cada Thing. |
| Client id MQTT | Igual al nombre del Thing (la política lo exige). |
| Endpoint de datos | `xxxxxxxx-ats.iot.us-east-1.amazonaws.com` (IoT Core → Settings). Se guarda en la configuración local del firmware y en la variable `IOT_ENDPOINT` de la Lambda, no en el código. |

## 2. Documento Shadow (Shadow clásico, sin nombre)

| Atributo | Sección | Tipo | Valores válidos | Quién lo escribe | Cuándo |
|---|---|---|---|---|---|
| `cerradura` | `desired` | string | `"abierta"`, `"cerrada"` | Lambda | Al recibir un comando de voz. |
| `cerradura` | `reported` | string | `"abierta"`, `"cerrada"` | ESP32 | Después de mover el servo. |
| `tapa` | `reported` | string | `"abierta"`, `"cerrada"` | ESP32 | Al cambiar el reed switch (con antirrebote). |
| `codigoVinculacion` | `reported` | string de 4 dígitos | `"0000"`–`"9999"` | ESP32 | Se genera en el primer arranque, se guarda en NVS y se reporta en cada reporte completo. |
| `firmware` | `reported` | string | versión semántica, p. ej. `"0.1.0"` | ESP32 | En cada reporte completo. |

Ejemplo con una orden pendiente:

```json
{
  "state": {
    "desired":  { "cerradura": "abierta" },
    "reported": { "cerradura": "cerrada", "tapa": "cerrada",
                  "codigoVinculacion": "4821", "firmware": "0.1.0" },
    "delta":    { "cerradura": "abierta" }
  }
}
```

Reglas:
- **Solo la Lambda escribe en `desired`** y **solo el ESP32 escribe en `reported`**.
- El ESP32 ignora en el `delta` los atributos que no conoce y los valores fuera de la lista. Si recibe un valor inválido, no mueve nada y vuelve a reportar su estado real.
- Después de aplicar un `delta`, el ESP32 reporta el nuevo estado. Así `reported` vuelve a coincidir con `desired` y AWS borra el `delta`.
- El ESP32 nunca borra `desired`.
- Se agregarán atributos nuevos (p. ej. `desafios`, `nivel`) sin cambiar los existentes.

## 3. Temas MQTT del ESP32

Prefijo: `$aws/things/<thingName>/shadow/`

| Tema | Dirección | Uso |
|---|---|---|
| `update` | ESP32 → AWS | Publica `{"state":{"reported":{...}}}`. |
| `update/delta` | AWS → ESP32 | Recibe los cambios de `desired` que difieren de `reported`. |
| `get` | ESP32 → AWS | Al conectar o reconectar pide el Shadow completo (payload vacío). |
| `get/accepted` | AWS → ESP32 | Respuesta al `get`: si trae `state.delta`, se aplica (orden pendiente). |
| `update/rejected`, `get/rejected` | AWS → ESP32 | Opcionales: registrar errores por Serial. |

**Frecuencia de reporte:**
- **Por evento:** apertura o cierre de la tapa y cada movimiento del servo, en ≤1 s.
- **Periódico de respaldo:** reporte completo cada **60 s**.
- **Justificación:** la tapa es un evento discreto, así que se reporta de inmediato. El respaldo de 60 s mantiene el Shadow vigente con unos 1 440 mensajes por día y por caja, muy por debajo del límite de la capa gratuita.

## 4. Vinculación usuario ↔ caja

1. El ESP32 muestra su código de 4 dígitos por Serial al iniciar y lo publica en `reported.codigoVinculacion`.
2. El usuario dice: *"vincula mi caja **uno** con el código **cuatro ocho dos uno**"*.
3. La Lambda arma `thingName = "caja-enigmas-" + f"{numeroCaja:02d}"`.
4. Valida que el Thing exista (`DescribeThing`); si no existe, lo informa y no guarda nada.
5. Lee el Shadow (`GetThingShadow`) y compara `codigo` con `reported.codigoVinculacion`; si no coinciden, lo informa y no guarda nada.
6. Guarda o reemplaza la vinculación (`PutItem`). Una vinculación nueva **reemplaza** a la anterior (cambiar de caja).
7. Desvincular hace `DeleteItem`.

Un usuario tiene como máximo una caja vinculada.

## 5. DynamoDB

| Elemento | Valor |
|---|---|
| Tabla | `CajaEnigmasVinculaciones`, capacidad *on-demand*. |
| Clave de partición | `userId` (S): `context.System.user.userId` de la solicitud de Alexa. |
| Atributos | `thingName` (S), `fechaVinculacion` (S, ISO-8601 UTC, p. ej. `2026-11-08T15:20:00Z`). |

## 6. Lambda

| Elemento | Valor |
|---|---|
| Función | `caja-enigmas-skill`, Python 3.12, us-east-1. |
| Rol | `caja-enigmas-lambda-rol` ([config/aws/politica-rol-lambda.json](../config/aws/), lo agrega Mateo). |
| Variables de entorno | `TABLA_VINCULACIONES=CajaEnigmasVinculaciones`, `PREFIJO_THING=caja-enigmas-`, `IOT_ENDPOINT=https://xxxxxxxx-ats.iot.us-east-1.amazonaws.com`. |
| Disparador | Alexa Skills Kit, con verificación del Skill ID. |

## 7. Skill de Alexa

| Elemento | Valor |
|---|---|
| Idioma | Spanish (US), `es-US`. |
| Nombre de invocación | `caja de enigmas` |
| Modelo exportado | `config/alexa/modelo-interaccion.es-US.json` |

| Intent | Slots | Efecto |
|---|---|---|
| `VincularCajaIntent` | `numeroCaja` (`AMAZON.NUMBER`), `codigo` (`AMAZON.FOUR_DIGIT_NUMBER`) | Vincula o cambia la caja (RF7, RF9). |
| `DesvincularCajaIntent` | — | Elimina la vinculación (RF9). |
| `ConsultarTapaIntent` | — | Lee `reported.tapa` (RF4). |
| `ConsultarCerraduraIntent` | — | Lee `reported.cerradura` (RF6). |
| `AbrirCerraduraIntent` | — | `desired.cerradura = "abierta"` (RF5). |
| `CerrarCerraduraIntent` | — | `desired.cerradura = "cerrada"` (RF5). |
| `AMAZON.HelpIntent`, `CancelIntent`, `StopIntent`, `FallbackIntent`, `NavigateHomeIntent` | — | Intents integrados. |

Todo intent que actúa sobre una caja resuelve primero la vinculación del `userId`. Si no la hay, la skill explica cómo vincular (RF8).

## 8. Hardware

Los valores del firmware están todos en [firmware/include/ConfiguracionHardware.h](../firmware/include/ConfiguracionHardware.h); al calibrar el montaje se cambia solo ese archivo. El cableado está en [docs/GUIA_MONTAJE.md](GUIA_MONTAJE.md).

| Elemento | Valor | Estado |
|---|---|---|
| Placa | ESP32 DOIT DEVKIT V1 (`esp32doit-devkit-v1`). | Confirmado |
| Servo SG90 (señal) | GPIO 18. | Confirmado |
| Alimentación del servo | Fuente externa regulada de 5 V, **sin usar VIN**, con **GND común con el ESP32**; capacitor de 470–1000 µF recomendado. | Confirmado; fuente pendiente de compra |
| Ángulos del servo | cerrada = 45° / abierta = 135° | **Provisionales**: calibrar con `firmware/pruebas/servo` |
| Reed switch | Entre GPIO 4 y GND, con `INPUT_PULLUP`. | Confirmado; reed pendiente de compra |
| Valor lógico con la tapa cerrada | `LOW` (imán cerca: el reed cierra a GND). `HIGH` = tapa abierta. | **Provisional**: verificar con `firmware/pruebas/reed` |

Sin el reed conectado, el pull-up deja GPIO 4 en `HIGH` y la placa reporta `tapa: "abierta"`. Es lo esperado mientras no esté el montaje.
