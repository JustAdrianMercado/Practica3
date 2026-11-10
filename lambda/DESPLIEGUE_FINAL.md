# Paquete definitivo de Lambda: 09/11/2026

**Actualización documental con las capturas de Mateo:** la evidencia 04
muestra una ejecución de `$LATEST` cuyo SHA-256 coincide con este ZIP. La
carga y prueba de consola quedan así documentadas para esa instantánea; no
se establece qué versión o alias invoca Alexa. Las siete capturas y sus
límites se describen en
[APORTE_INFORME.md](APORTE_INFORME.md#evidencias-de-implementación-en-aws).

**LISTO PARA SUBIR A AWS.** El ZIP contiene las fuentes actuales del
repositorio, revisadas en el commit local `47de880`. La configuración y el
comportamiento no acreditados por las capturas quedan para las comprobaciones
manuales de abajo. El procedimiento de carga se conserva como referencia.

## Archivo que se debe cargar

| Dato | Resultado |
|---|---|
| Archivo | `lambda/caja-enigmas-skill.zip` |
| Ruta absoluta | `M:\IOT\practica3\Practica3\lambda\caja-enigmas-skill.zip` |
| Tamaño comprimido | **18 245 491 bytes (17,40 MiB)** |
| Tamaño descomprimido | **26 213 967 bytes** |
| Archivos | **2 851**, sin rutas duplicadas |
| SHA-256 | `60cf2ee785a03375b7b365eef36f80bb4e60615143376d3f1d3c5ecaa2b46bd7` |
| Integridad CRC de todos los archivos | Correcta (`ZipFile.testzip()`) |
| Handler | **`lambda_function.lambda_handler`** |
| Plataforma objetivo | **Python 3.12, AWS Lambda Linux x86_64** |
| Suite de Lambda | **76 aprobadas, 0 fallos, 0 errores, 0 omitidas** |
| Comprobación adicional | Arranque y despacho del handler con clientes boto3 reales y DynamoDB simulado mediante `Stubber`: correctos |

Se creó y validó el candidato antes de reemplazar el archivo final. El ZIP
anterior se conservó como
[`caja-enigmas-skill.anterior-a3c6c6261a3e.zip`](caja-enigmas-skill.anterior-a3c6c6261a3e.zip),
con **18 248 513 bytes** y SHA-256
`a3c6c6261a3ec30a63736bc993a852b7fb4c86d6d7107b8703d42cf27eb39111`.
Este respaldo corresponde al paquete local anterior; no se comprobó que
coincida con el código actualmente desplegado en AWS.

## Código, dependencias y compatibilidad

Había siete módulos desactualizados de `manejadores/` tanto en `paquete/`
como en el ZIP anterior: `consultar_cerradura.py`, `consultar_tapa.py`,
`controlar_cerradura.py`, `desvincular_caja.py`, `identidad.py`,
`lanzamiento.py` y `vincular_caja.py`. Se incorporaron al ZIP los **16 archivos
Python de producción actuales** de `lambda/`, `manejadores/` y `servicios/`.
La suite inicial aprobó y no fue necesario cambiar la lógica de la aplicación.

Se reutilizaron las **14 distribuciones** de `lambda/paquete/`, comprobando
requisitos transitivos, restricciones de Python y etiquetas de wheel.
**2 821 archivos incluidos de dependencias** coinciden en tamaño y SHA-256
con sus registros originales de instalación. Los `RECORD` del ZIP se
regeneraron para describir exactamente los archivos conservados. Las
versiones están fijadas en
[`requirements-despliegue.txt`](requirements-despliegue.txt):

| Dependencia | Versión |
|---|---|
| ask-sdk-core / ask-sdk-runtime | 1.19.0 / 1.19.0 |
| ask-sdk-model | 1.82.0 |
| boto3 / botocore | 1.43.126 / 1.43.126 |
| certifi | 2026.10.23 |
| charset-normalizer | 3.5.2 |
| idna | 3.20 |
| jmespath | 1.1.0 |
| python-dateutil | 2.9.0.post0 |
| requests | 2.34.2 |
| s3transfer | 0.19.3 |
| six | 1.17.0 |
| urllib3 | 2.8.0 |

Los originales de `lambda/paquete/` se conservaron. Para construir el ZIP
se seleccionaron únicamente archivos de las distribuciones verificadas y
se agregaron las fuentes actuales de `lambda/`; las copias antiguas de la
aplicación de `paquete/` no se utilizaron. El `requirements.txt` original
mantiene sus rangos de versiones.

Los dos binarios de `charset_normalizer` son ELF de 64 bits, x86_64 y
CPython 3.12. Su wheel declara `manylinux_2_17_x86_64`,
`manylinux2014_x86_64` y `manylinux_2_28_x86_64`. Las referencias GLIBC
encontradas llegan hasta `GLIBC_2.14`, compatibles con glibc 2.34 de Amazon
Linux 2023. Las demás distribuciones usan wheels de Python sin binarios
específicos de plataforma. Véase la
[guía oficial de paquetes Lambda](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html).

Se ejecutaron las 76 pruebas con **Python 3.12.10 en Windows** y se repitieron
con `-I -S -B` sobre el contenido extraído del ZIP, sin paquetes globales.
Se comprobó el origen de los módulos importados. La comprobación adicional
importó el handler de producción, construyó sus clientes SDK y validó los
parámetros de IoT contra los modelos locales de botocore. El despacho de
`LaunchRequest` usó `Stubber` para la lectura DynamoDB. Se bloquearon las
conexiones salientes: **0 intentos de red**. Aparecieron 23 `SyntaxWarning`
del SDK de Alexa; las pruebas terminaron correctamente.

La compatibilidad binaria Linux se comprobó estáticamente; los binarios
Linux no se ejecutaron en Windows. La captura 04 acredita una ejecución real
de consola con el mismo paquete, pero no muestra la versión de Python ni la
arquitectura configuradas. Falta documentar esos valores y la regresión
completa de Alexa sobre el endpoint efectivo.

## Contenido y revisión de datos privados

En la raíz están `lambda_function.py`, `textos.py`, `manejadores/`,
`servicios/` y las dependencias. No hay carpeta contenedora `lambda/` ni
`paquete/`. Los 16 archivos de producción son idénticos byte a byte a las
fuentes actuales. Los archivos tienen permisos POSIX `0644`.

Se excluyeron tests, `__pycache__`, bytecode, lanzadores Windows, `bin/`,
ejemplos independientes, documentación del proyecto, README, `.env`, archivos
de credenciales, certificados del Thing y claves privadas. Se conservaron
licencias, metadatos y los módulos Python y modelos de datos utilizados por
el SDK, incluidos sus módulos `docs/*.py`.

Las únicas CA incluidas son los conjuntos públicos del SDK: se cargaron
correctamente **126 CA de `botocore/cacert.pem`** y **118 CA de
`certifi/cacert.pem`**. No son certificados del Thing.

**No se detectaron credenciales reales, claves privadas, tokens, datos de
usuarios ni datos privados del proyecto en el ZIP.** Se examinó también el
contenido descomprimido de los modelos `.json.gz` y se buscaron identificadores
privados conocidos del proyecto. Dos modelos oficiales de botocore, RDS y
STS, contienen identificadores públicos terminados en `EXAMPLE`. Se
verificaron como ejemplos del SDK, con sus archivos originales intactos;
son falsos positivos del patrón de access keys. AWS publica esos
[identificadores de ejemplo](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-keys-admin-managed.html).

## Contratos revisados

La implementación concuerda con [`docs/contratos.md`](../docs/contratos.md),
el [modelo Alexa actual](../config/alexa/modelo-interaccion.es-US.json), la
[definición de la tabla](../config/aws/tabla-vinculaciones.json) y la
[política exportada del rol](../config/aws/politica-rol-lambda.json):

- Coinciden los **11 intents**: seis propios y cinco integrados.
  `LaunchRequest` y `SessionEndedRequest` se atienden por tipo de solicitud.
- Los slots `numeroCaja` y `codigo` usan `AMAZON.NUMBER` y
  `AMAZON.FOUR_DIGIT_NUMBER`. Ambos son obligatorios, sus prompts existen y
  el diálogo tiene `delegationStrategy: ALWAYS`, compatible con este backend.
  Véase la [delegación de diálogo de Alexa](https://developer.amazon.com/en-US/docs/alexa/custom-skills/delegate-dialog-to-alexa.html).
- La identidad procede de `context.System.user.userId`. DynamoDB usa
  `CajaEnigmasVinculaciones`, clave `userId` String y lectura consistente.
  Guarda `thingName` y `fechaVinculacion` en ISO-8601 UTC; el sufijo `+00:00`
  es UTC, equivalente al `Z` del ejemplo contractual.
- Vincular comprueba `DescribeThing` y el String de cuatro dígitos de
  `reported.codigoVinculacion`, preservando ceros iniciales. `PutItem`
  reemplaza la vinculación del usuario y `DeleteItem` la elimina.
- Se usa el Shadow clásico, sin `shadowName`, en `us-east-1`, con nombres
  `caja-enigmas-NN`. Las consultas leen `reported`; los comandos escriben
  exclusivamente `desired.cerradura`, con `abierta` o `cerrada`.
- La consulta de cerradura compara `desired` y `reported` de una sola
  lectura y avisa si difieren. El comando anuncia el envío de la orden.
  No escribe `reported` ni afirma haber movido el servo.
- Las seis operaciones AWS de los servicios coinciden con las acciones y
  recursos de la política exportada. Los permisos efectivos desplegados
  quedan para la comprobación manual en la consola.

No se encontraron incompatibilidades que requieran cambiar contratos,
firmware o modelo Alexa. Solo se modificaron archivos dentro de `lambda/`.
La desvinculación es inmediata, como permite el plan. La consulta usa el
último estado reportado: no comprueba por sí sola la conexión actual del
dispositivo ni la antigüedad del reporte.

## Carga manual en la consola AWS

Estos pasos son para el integrante responsable. Esta preparación no ejecutó
AWS CLI, no invocó servicios AWS ni modificó recursos de la nube. Tampoco
se hicieron commit, push, merge ni PR.

1. En la consola AWS, seleccionar **N. Virginia (`us-east-1`) → Lambda →
   Functions → `caja-enigmas-skill`**. Registrar la versión o alias usado por
   Alexa. Descargar desde la consola el código desplegado si se necesita
   un respaldo de esa versión concreta.
2. En **Code → Runtime settings**, comprobar **Python 3.12**, **x86_64** y
   **`lambda_function.lambda_handler`**, según la
   [convención de handlers](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html).
3. En **Configuration → Environment variables**, comprobar
   `TABLA_VINCULACIONES=CajaEnigmasVinculaciones`,
   `PREFIJO_THING=caja-enigmas-` e
   `IOT_ENDPOINT=https://<endpoint-ATS-real>.iot.us-east-1.amazonaws.com`.
   Obtener el endpoint real de **IoT Core → Settings**. Las credenciales
   las proporciona el rol de ejecución de Lambda.
4. En **Configuration → Permissions**, comprobar el rol
   `caja-enigmas-lambda-rol`, sus permisos contractuales y CloudWatch Logs.
   En **Triggers**, comprobar Alexa Skills Kit con verificación del Skill
   ID de Lucía. En DynamoDB comprobar la tabla, clave `userId` String y
   capacidad on-demand.
5. En **Code → Code source → Upload from → .zip file → Upload**, seleccionar
   **`M:\IOT\practica3\Practica3\lambda\caja-enigmas-skill.zip`**, abrirlo y
   pulsar **Save**. Esperar a que la actualización termine correctamente.
   Su tamaño permite carga directa desde la consola; véase el
   [procedimiento oficial](https://docs.aws.amazon.com/lambda/latest/dg/configuration-function-zip.html).
6. En **Test**, crear un evento privado con el JSON de abajo y ejecutar
   primero `LaunchRequest`. Revisar la respuesta de voz y los logs: el
   manejador global también puede devolver una respuesta válida con un
   mensaje genérico de error. No debe aparecer `Runtime.ImportModuleError`,
   fallo TLS, permiso denegado ni error de inicialización.
7. Con Lucía, comprobar el ARN en **Alexa Developer Console → Build →
   Endpoint** para América. Si apunta a una versión o alias, cargar el ZIP
   en `$LATEST` no actualiza ese destino automáticamente: publicar una
   versión nueva y, si corresponde, actualizar el alias desde la consola
   antes de probar el endpoint efectivo. El modelo Alexa se conserva.

## Eventos y pruebas finales manuales

Este evento de consola usa un usuario ficticio reservado para pruebas.
Mantener la identidad en `context.System.user.userId`. La prueba directa en
Lambda no verifica el disparador Alexa; después se debe probar el simulador
de la skill y dos cuentas reales distintas.

```json
{
  "version": "1.0",
  "session": {
    "new": true,
    "sessionId": "sesion-prueba-final",
    "application": {"applicationId": "amzn1.ask.skill.prueba-local"},
    "user": {"userId": "prueba-final-A"}
  },
  "context": {
    "System": {
      "application": {"applicationId": "amzn1.ask.skill.prueba-local"},
      "user": {"userId": "prueba-final-A"}
    }
  },
  "request": {
    "type": "LaunchRequest",
    "requestId": "solicitud-prueba-final",
    "timestamp": "2026-11-09T12:00:00Z",
    "locale": "es-US"
  }
}
```

Para vincular, cambiar `request.type` a `IntentRequest` y agregar este
objeto dentro de `request`. Reemplazar el marcador por el código real de
cuatro dígitos obtenido del dispositivo o de su Shadow:

```json
"intent": {
  "name": "VincularCajaIntent",
  "confirmationStatus": "NONE",
  "slots": {
    "numeroCaja": {"name": "numeroCaja", "value": "1"},
    "codigo": {"name": "codigo", "value": "REEMPLAZAR_CODIGO_REAL"}
  }
}
```

Para los demás intents cambiar `intent.name` y usar `"slots": {}`.
Para B, cambiar ambos `userId` a `prueba-final-B` y emplear su caja y código.
Las pruebas de vinculación crean o reemplazan registros de prueba en la tabla;
las de desvinculación los eliminan.

| Orden | Acción manual | Resultado esperado |
|---|---|---|
| 1 | Lanzar y consultar sin vinculación | Orientación para vincular; ninguna orden al Shadow. |
| 2 | Vincular A con caja 01 y código real | Éxito; DynamoDB contiene `userId`, `thingName=caja-enigmas-01` y fecha UTC, todos String. |
| 3 | Código incorrecto, slots ausentes o Thing inexistente comprobado en consola | Rechazo u orientación; la vinculación anterior permanece. En voz, Alexa solicita ambos slots. |
| 4 | Consultar tapa y cerradura | Respuesta coherente con el último `reported`; estado desconocido si falta el atributo. |
| 5 | Abrir | `desired.cerradura=abierta`; respuesta que anuncia envío. Comprobar aparte aplicación por ESP32 y actualización de `reported`. |
| 6 | Cerrar | `desired.cerradura=cerrada`; distinguir envío, reporte y observación física. |
| 7 | Desconectar caja y pedir estado contrario al último `reported` | `desired` cambia, `reported` permanece; consulta avisa orden pendiente. Con Adrián/Santiago, comprobar aplicación y reporte al reconectar. |
| 8 | Vincular B con caja 02 y alternar consultas/comandos de A y B | Cada petición resuelve la caja del usuario correspondiente. |
| 9 | Cambiar A de caja vinculando la nueva | Se reemplaza su único registro; el de B permanece intacto. |
| 10 | Desvincular A | Se elimina solo su registro; sus comandos posteriores piden vinculación. Desvincular B al terminar las pruebas reservadas. |
| 11 | Help, Fallback, Cancel y Stop | Ayuda y repregunta, o despedida y cierre según el intent. `NavigateHomeIntent` directo cierra; `SessionEndedRequest` directo devuelve `response: {}`. |
| 12 | Revisar CloudWatch y repetir mediante Alexa real | Sin errores de importación, TLS o permisos; sin datos privados en logs de la aplicación. Registrar duración Lambda y medir aparte latencia de voz de extremo a extremo. |

**Las 76 pruebas locales y el arranque simulado no demuestran movimiento
físico del servo.** Esa evidencia requiere observar el montaje real. La
aceptación final de la integración requiere las pruebas manuales del runtime,
permisos, disparador y endpoint efectivos.

## Evidencias locales

Tras reanudar después del apagado se verificaron nuevamente el CRC del ZIP
y los SHA-256 de sus **2 851 archivos**. Las **16 fuentes de producción**
coinciden con el código actual; los **13 archivos de tests** coinciden con
los ejecutados en la validación aprobada. Las 14 versiones fijadas y el
respaldo anterior también permanecen intactos. No fue necesario reconstruir
el ZIP ni repetir la suite. El resultado quedó en
[`revalidacion-tras-apagado.json`](paquete/validacion-20261109T142019Z/revalidacion-tras-apagado.json).

Los ZIP y `paquete/` están ignorados por Git. Se conservaron el candidato,
su extracción y las evidencias en
`lambda/paquete/validacion-20261109T142019Z/`:

- [`auditoria.json`](paquete/validacion-20261109T142019Z/auditoria.json): tamaños,
  versiones, hashes de fuentes, CA, binarios, escaneo y respaldo.
- [`contenido-zip.json`](paquete/validacion-20261109T142019Z/contenido-zip.json):
  nombre, tamaño y SHA-256 de cada archivo del ZIP.
- [`pruebas-zip.log`](paquete/validacion-20261109T142019Z/pruebas-zip.log):
  resultado de las 76 pruebas sobre el contenido extraído.
- [`suite-aislado.json`](paquete/validacion-20261109T142019Z/suite-aislado.json)
  y [`arranque-aislado.json`](paquete/validacion-20261109T142019Z/arranque-aislado.json):
  resultados, avisos, origen de los módulos y bloqueo de red.

Comprobaciones locales desde la raíz del repositorio:

```powershell
Get-FileHash -LiteralPath lambda/caja-enigmas-skill.zip -Algorithm SHA256
py -3.12 -m zipfile -t lambda/caja-enigmas-skill.zip
py -3.12 -m unittest discover -s lambda/tests -v
```
