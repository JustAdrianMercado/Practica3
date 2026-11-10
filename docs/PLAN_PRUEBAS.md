# Plan y matriz de frases de Alexa

El [informe](../INFORME.md#4-pruebas-y-validaciones) contiene la metodología,
los resultados RF/RNF y las incidencias. Esta matriz conserva las 48 frases
reales del [modelo es-US](../config/alexa/modelo-interaccion.es-US.json).
El equipo confirmó haberlas probado todas; no elaboró transcripciones
individuales, conteos de repeticiones ni cronometraje.

## Identificadores de escenarios

| ID | Escenario de referencia del informe |
|---|---|
| PF01 | Lectura del sensor. |
| PF02 | Reporte del sensor y actuador. |
| PF03 | Aplicación de la orden recibida. |
| PF04 | Consulta de tapa. |
| PF05 / PF06 | Apertura / cierre. |
| PF07 | Consulta de cerradura. |
| PF08 / PF09 | Vinculación / conservación entre sesiones. |
| PF10 | Resolución por usuario y orientación sin vínculo. |
| PF11 / PF12 | Validación de Thing/código / cambio y eliminación. |
| PF13 | Intents integrados y fin de sesión, cubiertos automáticamente. |
| PN01–PN05 | Estabilidad, exactitud discreta, respuesta, reporte y reconexión, respectivamente. |
| PS01 | Revisión de seguridad y validaciones del backend. |

## Matriz de las frases configuradas

La respuesta esperada describe el comportamiento según el estado del usuario y
del Shadow; no es una transcripción inventada. Los slots se sustituyen con datos
de prueba, sin publicar el código real. «Aprobado (manual)» significa
**Aprobado — validación manual reportada por el equipo**. No certifica una
medición cuantitativa ni añade frases a las del modelo exportado.

| Intent | Frase configurada | Prueba | Resultado esperado | Resultado reportado | Estado |
|---|---|---|---|---|---|
| `VincularCajaIntent` | vincula mi caja {numeroCaja} con el código {codigo} | PF08 / PF09 | Solicitar slots ausentes; con datos válidos, confirmar la relación guardada o reemplazada. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `VincularCajaIntent` | registra la caja {numeroCaja} con el código {codigo} | PF08 / PF09 | Solicitar slots ausentes; con datos válidos, confirmar la relación guardada o reemplazada. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `VincularCajaIntent` | vincula mi caja | PF08 / PF09 | Solicitar slots ausentes; con datos válidos, confirmar la relación guardada o reemplazada. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `VincularCajaIntent` | registra mi caja | PF08 / PF09 | Solicitar slots ausentes; con datos válidos, confirmar la relación guardada o reemplazada. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `VincularCajaIntent` | vincula la caja {numeroCaja} | PF08 / PF09 | Solicitar slots ausentes; con datos válidos, confirmar la relación guardada o reemplazada. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `VincularCajaIntent` | registra la caja {numeroCaja} | PF08 / PF09 | Solicitar slots ausentes; con datos válidos, confirmar la relación guardada o reemplazada. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `VincularCajaIntent` | cambia mi caja | PF08 / PF09 | Solicitar slots ausentes; con datos válidos, confirmar la relación guardada o reemplazada. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `VincularCajaIntent` | asocia mi caja | PF08 / PF09 | Solicitar slots ausentes; con datos válidos, confirmar la relación guardada o reemplazada. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `DesvincularCajaIntent` | desvincula mi caja | PF12 | Confirmar la eliminación de la relación del usuario o explicar que no existe. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `DesvincularCajaIntent` | olvida mi caja | PF12 | Confirmar la eliminación de la relación del usuario o explicar que no existe. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `DesvincularCajaIntent` | elimina mi vinculación | PF12 | Confirmar la eliminación de la relación del usuario o explicar que no existe. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `DesvincularCajaIntent` | quita mi caja | PF12 | Confirmar la eliminación de la relación del usuario o explicar que no existe. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `DesvincularCajaIntent` | desasocia mi caja | PF12 | Confirmar la eliminación de la relación del usuario o explicar que no existe. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `DesvincularCajaIntent` | borra la vinculación | PF12 | Confirmar la eliminación de la relación del usuario o explicar que no existe. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `DesvincularCajaIntent` | quiero desvincular mi caja | PF12 | Confirmar la eliminación de la relación del usuario o explicar que no existe. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `DesvincularCajaIntent` | deja de usar mi caja | PF12 | Confirmar la eliminación de la relación del usuario o explicar que no existe. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `ConsultarTapaIntent` | cómo está la caja | PF04 | Informar abierta/cerrada según reported.tapa; reconocer dato ausente. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `ConsultarTapaIntent` | cómo está la tapa | PF04 | Informar abierta/cerrada según reported.tapa; reconocer dato ausente. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `ConsultarTapaIntent` | la tapa está abierta | PF04 | Informar abierta/cerrada según reported.tapa; reconocer dato ausente. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `ConsultarTapaIntent` | la tapa está cerrada | PF04 | Informar abierta/cerrada según reported.tapa; reconocer dato ausente. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `ConsultarTapaIntent` | consulta la tapa | PF04 | Informar abierta/cerrada según reported.tapa; reconocer dato ausente. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `ConsultarTapaIntent` | dime el estado de la tapa | PF04 | Informar abierta/cerrada según reported.tapa; reconocer dato ausente. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `ConsultarTapaIntent` | está abierta la tapa | PF04 | Informar abierta/cerrada según reported.tapa; reconocer dato ausente. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `ConsultarTapaIntent` | está cerrada la tapa | PF04 | Informar abierta/cerrada según reported.tapa; reconocer dato ausente. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `ConsultarCerraduraIntent` | cómo está la cerradura | PF07 | Informar el último reported.cerradura y advertir una orden sin confirmar cuando corresponda. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `ConsultarCerraduraIntent` | está trabada la caja | PF07 | Informar el último reported.cerradura y advertir una orden sin confirmar cuando corresponda. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `ConsultarCerraduraIntent` | está destrabada la caja | PF07 | Informar el último reported.cerradura y advertir una orden sin confirmar cuando corresponda. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `ConsultarCerraduraIntent` | la cerradura está abierta | PF07 | Informar el último reported.cerradura y advertir una orden sin confirmar cuando corresponda. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `ConsultarCerraduraIntent` | la cerradura está cerrada | PF07 | Informar el último reported.cerradura y advertir una orden sin confirmar cuando corresponda. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `ConsultarCerraduraIntent` | consulta la cerradura | PF07 | Informar el último reported.cerradura y advertir una orden sin confirmar cuando corresponda. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `ConsultarCerraduraIntent` | dime el estado de la cerradura | PF07 | Informar el último reported.cerradura y advertir una orden sin confirmar cuando corresponda. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `ConsultarCerraduraIntent` | está cerrada la cerradura | PF07 | Informar el último reported.cerradura y advertir una orden sin confirmar cuando corresponda. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `AbrirCerraduraIntent` | abre la cerradura | PF05 | Anunciar el envío de apertura y solicitar desired.cerradura=abierta. | Envío confirmado; ensayo de comunicación con desired=reported=abierta, Shadow v115. | Aprobado (manual) |
| `AbrirCerraduraIntent` | destraba la caja | PF05 | Anunciar el envío de apertura y solicitar desired.cerradura=abierta. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `AbrirCerraduraIntent` | abre mi caja | PF05 | Anunciar el envío de apertura y solicitar desired.cerradura=abierta. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `AbrirCerraduraIntent` | desbloquea la cerradura | PF05 | Anunciar el envío de apertura y solicitar desired.cerradura=abierta. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `AbrirCerraduraIntent` | quiero abrir la caja | PF05 | Anunciar el envío de apertura y solicitar desired.cerradura=abierta. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `AbrirCerraduraIntent` | destraba mi caja | PF05 | Anunciar el envío de apertura y solicitar desired.cerradura=abierta. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `AbrirCerraduraIntent` | abre la caja | PF05 | Anunciar el envío de apertura y solicitar desired.cerradura=abierta. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `AbrirCerraduraIntent` | desbloquea mi caja | PF05 | Anunciar el envío de apertura y solicitar desired.cerradura=abierta. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `CerrarCerraduraIntent` | cierra la cerradura | PF06 | Anunciar el envío de cierre y solicitar desired.cerradura=cerrada. | Envío confirmado; ensayo de comunicación con desired=reported=cerrada, Shadow v118. | Aprobado (manual) |
| `CerrarCerraduraIntent` | traba la caja | PF06 | Anunciar el envío de cierre y solicitar desired.cerradura=cerrada. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `CerrarCerraduraIntent` | cierra mi caja | PF06 | Anunciar el envío de cierre y solicitar desired.cerradura=cerrada. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `CerrarCerraduraIntent` | bloquea la cerradura | PF06 | Anunciar el envío de cierre y solicitar desired.cerradura=cerrada. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `CerrarCerraduraIntent` | quiero cerrar la caja | PF06 | Anunciar el envío de cierre y solicitar desired.cerradura=cerrada. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `CerrarCerraduraIntent` | traba mi caja | PF06 | Anunciar el envío de cierre y solicitar desired.cerradura=cerrada. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `CerrarCerraduraIntent` | cierra la caja | PF06 | Anunciar el envío de cierre y solicitar desired.cerradura=cerrada. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |
| `CerrarCerraduraIntent` | bloquea mi caja | PF06 | Anunciar el envío de cierre y solicitar desired.cerradura=cerrada. | Funcionamiento confirmado por el equipo; sin transcripción individual. | Aprobado (manual) |

Los casos inválidos, usuarios sin vinculación, reemplazo, eliminación y estados
sin confirmar se relacionan con las pruebas automatizadas en el apartado 4.2.
Las capturas/fotografías se catalogan en el apartado 8.2. Las series cuantitativas
se distinguen de esta validación funcional en los
[protocolos de medición](PRUEBAS_FISICAS.md).
