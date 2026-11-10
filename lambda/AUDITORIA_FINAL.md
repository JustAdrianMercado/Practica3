# Auditoría final de Mateo: Lambda y DynamoDB

**Actualización del 09/11/2026:** el paquete definitivo ya se reconstruyó y
validó, con respaldo del ZIP anterior. Los resultados actuales y los pasos
de carga están en [DESPLIEGUE_FINAL.md](DESPLIEGUE_FINAL.md). El contenido
siguiente conserva el registro histórico de la auditoría del 07/11.

Auditoría local del 07/11/2026, rama `feat/lambda`. Referencias:
[consigna](../docs/consigna/Práctica_3.md),
[plan](../docs/planificacion/03-mateo-lambda.md) y
[contratos](../docs/contratos.md). No se modificaron recursos AWS ni archivos
de otros integrantes. No se hicieron commits, push, merge ni PR.

## Estado de entrega

El backend y los entregables escritos están listos para revisión local. La
aceptación de la integración completa requiere evidencias manuales, la prueba
física y las mediciones todavía pendientes. **Las correcciones de esta
auditoría no están desplegadas: hay que generar un nuevo ZIP, actualizar AWS
desde la consola y repetir la regresión real con Lucía.**

El ZIP anterior `lambda/caja-enigmas-skill.zip` se conserva, está ignorado por
Git y no representa el código corregido. Su SHA-256 anterior es
`a3c6c6261a3ec30a63736bc993a852b7fb4c86d6d7107b8703d42cf27eb39111`.
Faltan en él `manejadores/identidad.py` y las versiones corregidas de seis
manejadores. No se sobrescribió ese artefacto ni se modificó el despliegue.

## Hallazgos y correcciones

| Hallazgo reproducido | Corrección local | Regresión |
|---|---|---|
| Launch consultaba DynamoDB con `user_id=None`; faltas de `context`/`System`/`user` terminaban en error genérico. | Función compartida `obtener_user_id`; todos los manejadores de caja responden sin acceder a AWS si falta identidad. No hay alternativa desde `session.user`. | Tres pruebas con múltiples solicitudes y niveles de contexto ausente/vacío. |
| Se aceptaba `reported.codigoVinculacion` numérico convirtiéndolo a string. | Se exige string conforme al contrato y se conservan ceros iniciales. | Código numérico rechazado y código `0421` aceptado. |
| Un código mal formado producía consultas AWS antes de validar su formato. | Validación local de cuatro dígitos ASCII antes de `DescribeThing` y `GetThingShadow`. | Códigos cortos, Unicode, alfanuméricos y blancos no llaman a AWS. |
| El nombre leído de DynamoDB se insertaba sin escapar en SSML de bienvenida. | Escape XML del texto dinámico antes de `speak`. | SSML válido sin interpretar etiquetas contenidas en el dato. |
| Desvincular sin caja no explicaba cómo vincular. | Se agrega la frase de orientación, conservando la respuesta anterior. | Sin `DeleteItem` y con ayuda para vincular. |
| Documentos decían Python 3.11, falta de despliegue y de disparador. | Se actualizan a Python 3.12.10 y se registran los resultados comunicados por Mateo con su procedencia. | Revisión documental y de enlaces. |
| La receta de compresión íntegra podía incluir tests y lanzadores Windows traídos por pip. | README con destino nuevo, filtro de archivos y comprobaciones del ZIP. No se altera el ZIP anterior. | Sintaxis de la receta revisada; el nuevo empaquetado queda pendiente. |

Los errores de conexión y timeout del SDK también se probaron sin exponer
URLs o mensajes en voz/logs. No se modificaron las 67 pruebas previas. El
archivo nuevo [test_auditoria.py](tests/test_auditoria.py) contiene nueve
pruebas; varios métodos usan subtests, que no se cuentan como pruebas extra.

### Archivos de esta auditoría

- Creados: `manejadores/identidad.py`, `tests/test_auditoria.py`,
  `AUDITORIA_FINAL.md`, `APORTE_INFORME.md` y `GUIA_DEFENSA.md`.
- Modificados: `manejadores/lanzamiento.py`, `vincular_caja.py`,
  `desvincular_caja.py`, `consultar_tapa.py`, `consultar_cerradura.py`,
  `controlar_cerradura.py`, `README.md` e `INFORME_TECNICO.md`.
- Los cambios locales anteriores en el builder, ServicioShadow y los demás
  manejadores/tests se conservaron. Los dos JSON de configuración propios
  se revisaron sin editarlos. `INFORME.md`, contratos, firmware y archivos de
  Alexa no se modificaron.

## RF4–RF9

En esta tabla, «real comunicado» significa información proporcionada por
Mateo en la conversación. No implica inspección nueva de AWS por el agente.

| Requisito | Estado del backend local | Estado de integración y evidencia |
|---|---|---|
| RF4: consultar sensor | Implementado: `ConsultarTapaIntent`, `reported.tapa`, respuesta en español y dato desconocido. Tests aprobados. | Se comunicó una consulta real de estado, sin identificar el intent. Precisar si fue tapa/cerradura y adjuntar evidencia. Sensor físico pendiente. |
| RF5: controlar actuador | Implementado: abrir/cerrar escriben solo `desired.cerradura` de la caja vinculada. Tests aprobados. | Orden real de cierre comunicada. Apertura y aplicación física aún sin evidencia. No se afirma movimiento del servo. |
| RF6: consultar actuador | Implementado: último `reported.cerradura` y aviso de orden pendiente. Tests aprobados. | Coincidencia `desired`/`reported` comunicada en IoT; falta precisar consulta real de cerradura. No equivale a prueba física. |
| RF7: vincular y persistir | Implementado: Thing existente, código string de cuatro dígitos y `PutItem` con fecha UTC. Tests aprobados. | Vinculación real de la caja 1 comunicada. Adjuntar ítem redactado y persistencia tras cerrar/reabrir sesión. |
| RF8: resolver por usuario | Implementado: `context.System.user.userId`, lectura consistente por petición y orientación sin vinculación. Dos usuarios cubiertos con mocks. | Falta probar y documentar dos usuarios reales y usuario sin vincular. |
| RF9: validar, cambiar y eliminar | Implementado: `DescribeThing`, rechazo de código incorrecto, reemplazo por usuario y eliminación. Tests aprobados. | Falta evidencia real de Thing inexistente, código incorrecto, cambio y desvinculación. |

La confirmación antes de desvincular y el acertijo son opcionales en el plan;
no están implementados y no bloquean RF4–RF9. No se añadieron intents ni se
cambiaron slots, estados o atributos del contrato. Las definiciones de
hardware del contrato siguen provisionales; corresponden a Santiago/Adrián.

## Requerimientos no funcionales y límites

| Aspecto | Verificación local | Pendiente para declararlo medido |
|---|---|---|
| Modularidad y POO | Manejadores por responsabilidad, servicios con clientes inyectados y clase común de comandos. | Revisión de código por Lucía. |
| Runtime y sintaxis | Python 3.12.10, 76 tests y `compileall` correctos. | Regresión del código actualizado en la Lambda real. |
| Manejo de errores | Mocks de errores IoT/DynamoDB, payload inválido y errores de red. Respuesta genérica y log limitado. | Observar errores reales y configuración de timeout sin forzar fallos destructivos. |
| Seguridad | Sin hallazgos de secretos en archivos candidatos; rol exportado acotado, identidad sin fallback y SSML escapado. | Adjuntar políticas activas, logs y verificación del Skill ID. |
| Tiempo de respuesta | No se agregan esperas/sondeo. Clientes reutilizados entre invocaciones. | Medir `Duration` e `Init Duration` de Lambda y tiempo completo con hardware. El objetivo del plan es ≤3 s extremo a extremo, no una duración unitaria de tests. |
| Estabilidad | Tests deterministas sin servicios externos. | Ensayo del sistema durante el período declarado por el grupo (referencia de consigna: ≥10 min), registrando peticiones, errores y reinicios físicos. |
| Exactitud, frecuencia y reconexión | Contratos respetados por el backend; no medidos con mocks. | Santiago/Adrián con dispositivo real: sensor, reporte por evento ≤1 s, respaldo 60 s y aplicación de orden pendiente al reconectar. |

La configuración del SDK no fija timeouts ni reintentos explícitos. En la
versión local, `Config()` tiene conexión/lectura de 60 s y `retries=None`;
el timeout efectivo de la Lambda y la configuración de su entorno no se
leyeron. **Esto no garantiza responder antes del timeout de Alexa.** Revisar
el timeout real y las métricas, declarar un presupuesto y decidir los límites
de las llamadas con mediciones antes de ajustar código/configuración. El
manejador global no puede recuperar una invocación terminada por el runtime.
Referencia de [configuración de boto3](https://docs.aws.amazon.com/boto3/latest/guide/configuration.html).

No hay detección de conectividad ni de antigüedad del reporte: una consulta
devuelve el último dato almacenado. `desired == reported` demuestra igualdad
de atributos en el Shadow, no quién escribió `reported` ni un movimiento real.

El código de cuatro dígitos es el mecanismo académico acordado: tiene 10 000
posibilidades y el backend no implementa un límite de intentos. No equivale a
Account Linking/OAuth ni a una autenticación fuerte para una cerradura de uso
real. Un límite de intentos o un mecanismo distinto requiere diseño y
coordinación con el grupo; no se alteró el contrato para introducirlo aquí.

## Evidencias manuales que faltan

No se crearon capturas ni registros experimentales ficticios. Para cada
evidencia, registrar fecha/hora, versión/ZIP probado, responsable, pasos,
resultado observado y archivo. Guardar únicamente copias redactadas;
coordinar con Lucía su incorporación a los anexos del grupo.

| ID | Fuente y procedimiento manual | Contenido necesario |
|---|---|---|
| E01 | Lambda → `caja-enigmas-skill` → Runtime/Configuration | Python 3.12, arquitectura, handler, última actualización, memoria, timeout y las tres variables contractuales. Identificar versión/alias que invoca Alexa. |
| E02 | Lambda → desencadenador Alexa Skills Kit; Alexa → Endpoint | Disparador, verificación de Skill ID y correspondencia con el ARN efectivo. No basta una captura de `$LATEST` si se invoca un alias. |
| E03 | IAM → rol real y sus políticas activas | Confianza en `lambda.amazonaws.com`, seis acciones del JSON exportado y permisos de CloudWatch Logs; identificar políticas adicionales y restricciones. No adjuntar access keys. |
| E04 | DynamoDB → tabla → detalles | `userId` String como partición, sin sort key, capacidad on-demand. |
| E05 | DynamoDB → Explore table items, antes/después | Vincular, persistir entre sesiones, cambiar y desvincular. Seudónimos estables para usuarios A/B; `thingName` y fecha UTC visibles. No exportar CSV con datos personales. |
| E06 | Alexa → Test, `es-US` | Capturas/transcripción de la vinculación, consulta real de estado y cierre ya comunicados. Identificar qué intent produjo la consulta y el backend utilizado. Ocultar código real y tokens. |
| E07 | Alexa → Test, regresión completa | Tapa, cerradura, abrir, cerrar, Help/Stop/Cancel/Fallback, sin vincular, código incorrecto, Thing inexistente, cambio y desvinculación; dos usuarios con cajas distintas. Registrar lo observado, no solo lo esperado. |
| E08 | IoT Core → Thing → Shadow clásico | Antes/después de la orden, `desired.cerradura`, `reported.cerradura`, `tapa`, versión y timestamps. Ocultar `codigoVinculacion`. Identificar si `reported` provino de firmware, prueba manual o si su origen no está determinado. |
| E09 | CloudWatch → grupo configurado para la función | Logs completos de las invocaciones correlacionadas y sus `REPORT`: `Duration`, `Billed Duration`, `Max Memory Used` e `Init Duration` cuando exista. Marcar frías/calientes y la versión probada. |
| E10 | Ensayo conjunto con ESP32 y servo | Video/capturas que relacionen orden, movimiento y reporte real; prueba de desconexión/reconexión. Sigue pendiente y requiere a Santiago/Adrián. |
| E11 | Medición de respuesta con el grupo | Repeticiones, tiempos observados, promedio/máximo y criterio de aceptación; no sustituirlos por el tiempo que demora unittest. |

El grupo por defecto de logs sería `/aws/lambda/caja-enigmas-skill`; comprobar
cuál está configurado. Los campos `REPORT` distinguen duración del handler y
arranque; ver [logs de Lambda](https://docs.aws.amazon.com/lambda/latest/dg/python-logging.html).
No activar DEBUG de boto3 ni guardar eventos completos que contengan tokens.

## Revisión de Git y datos sensibles

La referencia local revisada es `origin/main` **747c917** y `HEAD` **7643840**:
0 commits detrás y 3 delante. No se hizo fetch; esta comparación no asegura
que el remoto siga en ese commit al momento de la entrega.

Se revisaron `git status`, el diff de trabajo, el índice y los cambios desde
`origin/main`. Los candidatos pertenecen a `lambda/**` o a
`config/aws/politica-rol-lambda.json` y `config/aws/tabla-vinculaciones.json`,
ambos asignados a Mateo. No hay archivos preparados en el índice. Se
examinaron nombres sensibles y patrones de claves privadas/access keys y
secretos literales, sin hallazgos en los candidatos ni nombres sensibles entre
los archivos versionados. Los ARN de recursos de los JSON son identificadores,
no credenciales.

`git check-ignore` confirma `lambda/paquete/` y el ZIP; el ZIP no está
versionado. Los archivos privados ignorados no se abrieron ni se incorporaron.
Las CA públicas del SDK autorizadas están dentro del paquete ignorado, no en
el conjunto de archivos a incorporar. Repetir la revisión después de añadir
capturas o nuevos archivos; ocultar identificadores privados antes de Git.

## Responsables y entrega

- **Mateo:** revisar estos cambios, generar ZIP nuevo sin sobrescribir el
  anterior, subirlo manualmente, adjuntar configuración/logs y revisar los
  permisos efectivos. Capturar la duración de Lambda y revisar sus timeouts.
- **Lucía:** revisar el PR, exportar el modelo `es-US` (ausente en esta rama),
  verificar Skill ID/endpoint/delegación automática, probar frases y dos
  usuarios, integrar [APORTE_INFORME.md](APORTE_INFORME.md) y las evidencias.
- **Adrián:** verificar el Shadow clásico, el código string de cuatro dígitos,
  la autoría de `reported`, las confirmaciones y la reconexión del firmware.
- **Santiago:** validar reed, alimentación/calibración del servo, movimiento
  y mediciones físicas. Junto con Lucía, medir respuesta de extremo a extremo.

### Pasos manuales para commit, push y PR

Estos comandos son instrucciones para Mateo; **no se ejecutaron**. Antes de
publicar, comprobar que `user.name` y `user.email` corresponden a su cuenta.
No añadir ZIP, paquete, certificados, credenciales, CSV ni evidencias sin
redactar; no usar `git add -f`.

```powershell
git status --short --branch
git config --get user.name
git config --get user.email
git fetch origin
git diff --name-status origin/main...HEAD
git diff --name-status
py -3.12 -m unittest discover -s lambda/tests -v
py -3.12 -m compileall -q lambda/lambda_function.py lambda/textos.py lambda/manejadores lambda/servicios lambda/tests
git diff --check
git add -- lambda config/aws/politica-rol-lambda.json config/aws/tabla-vinculaciones.json
git diff --cached --name-status
git diff --cached --check
git diff --cached
```

Revisar el diff completo del índice. Si solo contiene los archivos previstos
y sin datos sensibles, realizar el commit y publicar la rama:

```powershell
git commit -m "feat(lambda): completar backend y entregables de la práctica"
git push -u origin feat/lambda
```

En GitHub abrir Compare & pull request, base **main**, compare **feat/lambda**
y solicitar revisión a **Lucía** con su usuario real de GitHub. Si el fetch
muestra cambios o conflictos, coordinarlos sin descartar trabajo local. No
fusionar hasta la revisión del grupo y la integración que acuerden.

Título sugerido: **Completar backend Lambda, validaciones y entregables de
Caja de los Enigmas**. Descripción para el PR:

> Implementa los intents RF4–RF9 con vinculación persistente por usuario,
> consultas de reported y comandos limitados a desired.cerradura. Añade
> manejo de errores con logging seguro, validación estricta del código,
> protección ante identidad incompleta y escape de texto en SSML.
>
> Validación: 76 pruebas con unittest/mocks y compileall en Python 3.12.10.
> Incluye documentación técnica, auditoría, aporte para el informe y guía de
> defensa. Las pruebas reales de Alexa comunicadas corresponden al backend
> anterior a las correcciones de auditoría; falta generar/subir el nuevo ZIP
> manualmente y repetir la regresión. ESP32/servo y mediciones RNF pendientes.

Actualizar la descripción si antes del PR se incorpora un despliegue nuevo o
evidencias reales: mencionar únicamente lo que efectivamente se haya probado.
