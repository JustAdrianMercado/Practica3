# Procedimientos y registro de pruebas físicas

**Todas las pruebas están pendientes. No se han realizado ni aprobado pruebas físicas.**
Este archivo es una plantilla para registrar observaciones reales, no evidencia de
funcionamiento. No completar con valores simulados ni copiar resultados esperados
en la columna de observados. Un ensayo sin requisitos o instrumentos suficientes
se mantiene **pendiente**, con el motivo anotado.

Leer antes la [guía de montaje](GUIA_MONTAJE.md), el
[circuito](diagramas/circuito.svg) y los [contratos](contratos.md).
Antes de recablear, desconectar USB y fuente externa. No alimentar el servo desde
GPIO/3V3, ni unir positivos USB y externo. No manipular el lado de red eléctrica.

## Alcance y preparación

| Prueba | Alcance | Estado |
|---|---|---|
| 1. Alimentación y polaridad | Local, sin AWS/Alexa | Pendiente |
| 2. Servo sin carga | Local, diagnóstico `servo` | Pendiente |
| 3. Calibración | Local, montaje mecánico controlado | Pendiente |
| 4. Reed e imán | Local, diagnóstico `reed` | Pendiente |
| 5. Antirrebote | Local, diagnóstico `reed`; precisión limitada por muestreo/Serial | Pendiente |
| 6. 30 ciclos de tapa | AWS y firmware integrado para comparar con `reported.tapa`; Alexa no necesaria | Pendiente |
| 7. 10 tiempos de respuesta | AWS, Lambda, Alexa y firmware integrado | Pendiente |
| 8. Estabilidad ≥10 minutos | Observación local posible; validación integral requiere AWS y firmware integrado | Pendiente |
| 9. Recuperación y Shadow | AWS y firmware integrado; Alexa/Lambda para producir una orden pendiente | Pendiente |

Las pruebas 1–5 pueden realizarse sin cuenta AWS. Las pruebas 6–9 requieren
coordinación con Adrián; la 7 también con Mateo y Lucía. El `main.cpp` revisado solo
mantiene WiFi: los diagnósticos actuales no publican ni sincronizan Shadow.
En la prueba 8 anotar expresamente si el ensayo es local o integrado; uno local no
demuestra recuperación ni sincronización en AWS.

Estados permitidos: **pendiente**, **aprobada**, **fallida**. Aprobar solo tras
ejecutar el procedimiento y conservar evidencia suficiente. Registrar fallos sin
descartar repeticiones desfavorables. Si se cambia montaje o firmware, identificar
qué ensayos deben repetirse.

## Datos de la sesión

| Campo | Registro por completar |
|---|---|
| Fecha, hora y responsables | — |
| Rama y versión/commit del firmware realmente cargado | — |
| Programa: servo, reed o integración | — |
| ESP32 y servo identificados | — |
| Fuente: modelo, tensión/corriente declaradas y polaridad | — |
| Instrumentos disponibles y método de observación | — |
| Capacitor: ausente o valor, tensión nominal y polaridad | — |
| Fotografía del montaje y ubicación de los componentes | — |
| Thing de prueba y región, solo si aplica | — (`caja-enigmas-NN`, `us-east-1`) |

Guardar evidencias bajo `docs/evidencias/`, con prueba y fecha en el nombre, según
su [README](evidencias/README.md). No incluir certificados, claves, credenciales
WiFi, identificadores personales ni capturas con el ID de la cuenta.

## Prueba 1. Alimentación del servo y polaridad

**Objetivo:** confirmar las condiciones para conectar la fuente externa de 5 V CC.

**Materiales:** fuente y adaptador definitivos, fichas/etiquetas, cableado y cámara;
instrumento adecuado y ayuda competente si hay que medir tensión o polaridad.
No se presupone disponibilidad de multímetro.

**Procedimiento:**

1. Mantener servo y ESP32 desconectados de la fuente. Leer modelo, salida regulada,
   tensión, capacidad de corriente y polaridad de conector/bornes.
2. Comparar con los requisitos documentados del SG90 adquirido. Identificar su señal,
   positivo y GND mediante documentación, no solamente por colores.
3. Inspeccionar fuente, adaptador, aislamiento y cables. No abrir la fuente ni cortar
   cables. Si los bornes o datos no son inequívocos, mantener pendiente y pedir medición.
4. Si se dispone de instrumento y conocimiento, verificar la salida sin el circuito
   conectado; registrar valor, polaridad y método. Desconectar después la fuente.
   Una etiqueta no sustituye esa medición; sin instrumento escribir «no medido».
5. Sin energía, revisar S1–S6 de la guía: GND común, positivos separados y capacitor
   correcto si se instala. Medir continuidad solo con el circuito sin tensión, si hace falta.
6. Autorizar la conexión solo si se resolvieron dudas críticas. Esta revisión inicial
   no demuestra estabilidad de la fuente bajo carga; observarla también en 2 y 8.

**Resultado esperado:** fuente identificada y compatible con 5 V CC del montaje,
capacidad adecuada al servo real, polaridad inequívoca, GND común y sin uniones
indebidas entre positivos. No hay incertidumbres críticas pendientes para energizar.

| Dato | Declarado/documentado | Medido u observado |
|---|---|---|
| Salida y regulación | — | — |
| Capacidad de corriente | — | — |
| Polaridad de salida/adaptador | — | — |
| Cableado y separación de positivos | — | — |
| Capacitor opcional | — | — |

**Resultado observado:** por completar. **Estado:** pendiente.
**Observaciones y evidencias:** por completar; indicar limitaciones y qué no se midió.

## Prueba 2. Movimiento del SG90 sin carga

**Objetivo:** observar la respuesta básica sin riesgo de bloquear el mecanismo.

**Materiales:** montaje de servo revisado en 1, ESP32 por USB, computadora con
diagnóstico `servo`, monitor Serial a 115200 y cámara. Brazo desacoplado de la cerradura.

**Procedimiento:**

1. Con el servo separado, cargar el diagnóstico según el
   [README](../firmware/pruebas/README.md). Apagar y cablear siguiendo la guía.
2. Completar toda la revisión antes de energizar las dos alimentaciones.
3. Comprobar que no hay barrido automático. Enviar `estado`, después `iniciar` con
   el eje libre: solicita 90°, que puede estar lejos de la posición inicial desconocida.
4. Enviar primero `+` y `-`. Esperar movimiento completo y al menos 300 ms entre
   órdenes; probar otros ángulos solo con cambios máximos de 5° dentro de 45°–135°.
5. Comparar ángulo solicitado impreso y movimiento observado. No confundir el número
   enviado con medición angular. No forzar topes ni mantener esfuerzos.
6. Interrumpir ambas alimentaciones si hay atasco, calentamiento anormal o reinicios.
   Para apagar normalmente, esperar que finalice el movimiento; no cambiar cableado energizado.

**Resultado esperado:** sin movimiento repetitivo automático; respuesta visible a
órdenes válidas, sin atasco ni reinicios. No se define aún abierta/cerrada.

| Orden enviada | Ángulo solicitado impreso | Movimiento observado | Anomalías/evidencia |
|---|---|---|---|
| — | — | — | — |
| — | — | — | — |
| — | — | — | — |

**Resultado observado:** por completar. **Estado:** pendiente.
**Observaciones y evidencias:** por completar.

## Prueba 3. Calibración de apertura y cierre

**Objetivo:** elegir posiciones que destraben y traben sin forzar y con cierre
sostenido mecánicamente, sin depender de PWM permanente.

**Materiales:** servo aprobado en 2, caja/pestillo/soporte, fijaciones, diagnóstico,
herramientas de montaje y cámara. Alimentación revisada.

**Procedimiento:**

1. Revisar la geometría sin energía y sin aplicar fuerza al eje. Presentar el brazo
   para dejar margen de recorrido; hacer el primer posicionamiento desacoplado.
2. Aplicar el apartado 7 de la guía. No reiniciar el diagnóstico con el brazo
   acoplado si 90° no es una posición libre de bloqueo; revisar antes la geometría.
3. Explorar pasos pequeños observando cuándo traba y destraba. Detenerse si los
   candidatos exigen forzar o salir de la ventana inicial; no ampliar límites sin revisión.
4. Registrar candidatos, probar repetibilidad sin impacto y fijar solo con todo apagado.
5. Tras terminar el movimiento de cierre, apagar ambas alimentaciones y comprobar
   que el pestillo mantiene la tapa cerrada sin par continuo del servo. No evaluar
   esta condición solo por el valor de `estaAbierta()`, que refleja una orden.
6. Compartir los valores reales con el grupo para revisar contrato e integración.
   Este procedimiento no modifica automáticamente archivos ni parámetros.

**Resultado esperado:** posiciones seguras y repetibles con margen respecto de los
topes, sin esfuerzo continuo y con cierre mecánico sostenido sin alimentación.

| Posición | Ángulo candidato | Observación mecánica/margen | Verificado sin alimentación |
|---|---|---|---|
| Abierta | Pendiente | — | — |
| Cerrada | Pendiente | — | — |

**Resultado observado:** por completar. **Estado:** pendiente.
**Observaciones y evidencias:** por completar; incluir fotografía del brazo y pestillo.

## Prueba 4. Reed, imán y polaridad lógica

**Objetivo:** conocer respuesta al imán, distancia de conmutación e interpretación
de tapa real, sin dar por confirmada la convención LOW = cerrada.

**Materiales:** reed adquirido de dos terminales, imán, ESP32, USB, diagnóstico
`reed`, regla y cámara. Servo y su fuente separados para esta prueba local.

**Procedimiento:**

1. Cargar el diagnóstico y apagar USB. Conectar R1–R2 según la guía, revisar y alimentar solo por USB.
2. Observar la referencia inicial; no debe aparecer como evento de cambio.
3. Acercar y alejar lentamente el imán varias veces, manteniendo cada posición más
   de 50 ms. Registrar nivel eléctrico y estado interpretado por separado.
4. Medir con regla la separación cuando conmuta al acercar y al alejar, manteniendo
   identificadas orientación y referencias de la medida. Si no hay regla, dejar la distancia pendiente.
5. Comparar con tapa realmente abierta y cerrada. Si la convención es inversa al
   montaje real, documentarlo y avisar al grupo antes de modificar contrato o código.

**Resultado esperado:** conmutación repetible entre contacto abierto (HIGH) y a GND
(LOW), con interpretación física verificada o discrepancia identificada.

| Condición real | Orientación/distancia del imán (mm) | HIGH/LOW | Interpretación Serial | Coincide con tapa real |
|---|---|---|---|---|
| Imán lejos | — | — | — | — |
| Imán cerca | — | — | — | — |
| Tapa abierta | — | — | — | — |
| Tapa cerrada | — | — | — | — |

**Resultado observado:** por completar. **Estado:** pendiente.
**Observaciones y evidencias:** por completar; distinguir distancia de activación y liberación.

## Prueba 5. Antirrebote de aproximadamente 50 ms

**Objetivo:** comprobar el comportamiento observable de `SensorTapa`: estabilización
antes del aviso, un aviso consumido por cambio y ausencia de cambio inicial falso.

**Materiales:** montaje de 4, diagnóstico `reed`, registro Serial con sus marcas
de milisegundos; analizador lógico/osciloscopio solo si está disponible y se requiere
medir rebotes eléctricos con precisión. No es requisito para la observación básica.

**Procedimiento:**

1. Arrancar con el imán quieto. Separar el mensaje inicial de los eventos posteriores.
2. Acercar/alejar el imán y mantenerlo quieto. Registrar última transición eléctrica
   observada y mensaje de cambio confirmado; repetir con ambas transiciones.
3. Si se observan oscilaciones al borde de activación, comparar las líneas eléctricas
   con los avisos confirmados. No inventar un rebote si no aparece; anotarlo como no observado.
4. Mantener el estado estable varios segundos: no debe repetirse un aviso sin otro
   cambio confirmado. Los resúmenes periódicos no cuentan como avisos de cambio.
5. Estimar la diferencia entre marcas de tiempo de la última lectura candidata y
   confirmación. La clase debe esperar al menos 50 ms de estabilidad muestreada;
   el aviso puede llegar después según el muestreo y el tiempo de impresión.

**Resultado esperado:** sin aviso inicial ni avisos repetidos en reposo, con cambios
confirmados tras estabilidad. El cálculo usa resta sin signo para tolerar el
desbordamiento de `millis()`; un ensayo corto no demuestra haber cruzado ese desbordamiento.

**Límite del método:** la lectura eléctrica impresa y la lectura interna no se
toman exactamente en el mismo instante; Serial puede perder rebotes y añadir
retardo. Una diferencia aproximada no certifica 50 ms eléctricos exactos. Si hay
una discrepancia, registrar el log completo y revisar el método; no declarar que
el filtro falló o pasó con precisión instrumental basándose solo en una línea.

| Repetición | Transición | Última lectura observada (ms) | Aviso confirmado (ms) | Diferencia aproximada (ms) | Avisos extra |
|---|---|---|---|---|---|
| 1 | — | — | — | — | — |
| 2 | — | — | — | — | — |
| 3 | — | — | — | — | — |

**Resultado observado:** por completar. **Estado:** pendiente.
**Observaciones y evidencias:** por completar; indicar si solo se verificó comportamiento por Serial.

## Prueba 6. Treinta ciclos de apertura y cierre

**Objetivo:** comparar tapa física y `reported.tapa` en 30 ciclos completos.

**Materiales:** montaje completo, regla para distancia del imán, firmware integrado,
WiFi/AWS IoT Core, Shadow clásico del Thing correcto, acceso de consulta y cámara.
Coordinar con Adrián; Alexa no es necesaria para abrir la tapa manualmente.

**Procedimiento:**

1. Confirmar calibración, polaridad y firmware integrado que publique el reed.
2. Abrir y cerrar la tapa 30 veces, sin forzar una cerradura trabada. Cada ciclo
   contiene dos comparaciones: tapa abierta y tapa cerrada, una vez estabilizadas.
3. Comparar la realidad con `reported.tapa` en el Shadow y registrar cada mitad del
   ciclo. La meta del contrato es reporte por evento en ≤1 s; registrar retrasos,
   valores anteriores y discrepancias, sin borrarlos de la tabla.
4. Anotar distancia/orientación del imán y evidencia correlacionada con cada fila.
   No sustituir el Shadow por el monitor local para aprobar la prueba integrada.

**Resultado esperado:** 30/30 ciclos correctos (60/60 estados de tapa), sin cambios
espurios, con reportes por evento dentro del contrato.

| Ciclo | Tapa abierta: `reported.tapa` | Tapa cerrada: `reported.tapa` | Retraso/discrepancia | Evidencia |
|---|---|---|---|---|
| 1 | — | — | — | — |
| 2 | — | — | — | — |
| 3 | — | — | — | — |
| 4 | — | — | — | — |
| 5 | — | — | — | — |
| 6 | — | — | — | — |
| 7 | — | — | — | — |
| 8 | — | — | — | — |
| 9 | — | — | — | — |
| 10 | — | — | — | — |
| 11 | — | — | — | — |
| 12 | — | — | — | — |
| 13 | — | — | — | — |
| 14 | — | — | — | — |
| 15 | — | — | — | — |
| 16 | — | — | — | — |
| 17 | — | — | — | — |
| 18 | — | — | — | — |
| 19 | — | — | — | — |
| 20 | — | — | — | — |
| 21 | — | — | — | — |
| 22 | — | — | — | — |
| 23 | — | — | — | — |
| 24 | — | — | — | — |
| 25 | — | — | — | — |
| 26 | — | — | — | — |
| 27 | — | — | — | — |
| 28 | — | — | — | — |
| 29 | — | — | — | — |
| 30 | — | — | — | — |

**Resultado observado:** ciclos correctos __/30; estados correctos __/60.
**Estado:** pendiente. **Observaciones y evidencias:** por completar.

## Prueba 7. Tiempo de respuesta en diez repeticiones

**Objetivo:** medir desde el fin de la orden de voz hasta el inicio visible del
movimiento del actuador. No confundir este tiempo con el de movimiento completo.

**Materiales:** montaje calibrado, firmware integrado, WiFi/AWS, Lambda y skill
funcionales, usuario/caja vinculados y video que permita correlacionar audio/orden
y servo. Coordinar con Adrián, Mateo y Lucía.

**Procedimiento:**

1. Revisar que cada orden pida una posición distinta a la actual para que haya movimiento.
2. Grabar juntos orden y servo; elegir una referencia común visible/audible para
   el fin de la orden. Si se usa simulador, registrar su modalidad y referencia.
3. Dar diez órdenes alternadas de apertura/cierre, esperando que termine cada una.
4. Obtener del video `t0` (fin de orden) y `t1` (primer movimiento). Calcular
   `t1 − t0` y anotar resolución temporal y modalidad de prueba.
5. Registrar órdenes sin movimiento como fallos, no omitirlas ni asignarles 0 s.

**Resultado esperado:** diez respuestas correctas y tiempo máximo ≤3 s según el plan.

| Repetición | Orden | t0 (s) | t1 (s) | Diferencia (s) | Evidencia/fallo |
|---|---|---|---|---|---|
| 1 | — | — | — | — | — |
| 2 | — | — | — | — | — |
| 3 | — | — | — | — | — |
| 4 | — | — | — | — | — |
| 5 | — | — | — | — | — |
| 6 | — | — | — | — | — |
| 7 | — | — | — | — | — |
| 8 | — | — | — | — | — |
| 9 | — | — | — | — | — |
| 10 | — | — | — | — | — |

**Resultado observado:** máximo __ s; respuestas correctas __/10; resolución __ s.
**Estado:** pendiente. **Observaciones y evidencias:** por completar.

## Prueba 8. Estabilidad durante al menos diez minutos

**Objetivo:** observar reinicios, fallos y comportamiento bajo uso repetido.

**Materiales:** montaje revisado, monitor Serial, reloj y evidencia. Para ensayo
integrado: firmware de integración, AWS y vía de órdenes acordada; Alexa si se
prueba voz. Para observación local: diagnóstico adecuado, declarando su alcance.

**Procedimiento:**

1. Registrar programa cargado, alcance local/integrado y hora de inicio.
2. Mantener el circuito conectado al menos diez minutos. Ejecutar una orden segura
   cada minuto, esperando movimiento completo y sin barrido automático.
3. Observar arranques Serial, pérdida de respuesta, desconexiones, esfuerzos y otros
   comportamientos anormales. En integrado, observar también reportes por evento y
   respaldo completo cada 60 s, según el contrato.
4. Registrar incidencias con hora y evidencia. Si aparece una condición insegura,
   detener ambas alimentaciones y anotar duración real e interrupción.
5. Una ausencia de reinicios no demuestra tensión estable medida; no atribuir causas
   a una fuente o componente sin observación o medición que las sustente.

**Resultado esperado:** duración ≥10 minutos, 0 reinicios inesperados, órdenes
correctas y sin anomalías observadas. En integrado, reportes coherentes con el contrato.

| Alcance/programa | Inicio | Fin | Duración real | Órdenes correctas/emitidas | Reinicios | Fallos |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

| Hora/minuto | Orden o evento | Observación | Evidencia |
|---|---|---|---|
| — | — | — | — |
| — | — | — | — |

**Resultado observado:** por completar. **Estado:** pendiente.
**Observaciones y evidencias:** por completar; no presentar un ensayo local como validación integrada.

## Prueba 9. Recuperación tras desconexión y sincronización del Shadow

**Objetivo:** comprobar que al recuperar conectividad el dispositivo obtenga su
Shadow y aplique una orden pendiente, sin que el ESP32 escriba `desired`.

**Materiales:** montaje calibrado, firmware integrado con reconexión y Shadow,
WiFi de prueba, AWS IoT Core y responsable de AWS; Lambda/Alexa para emitir una
orden pendiente por el flujo del proyecto. Acceso de consulta al Shadow y logs.

**Procedimiento, con Adrián:**

1. Confirmar Thing `caja-enigmas-NN`, región `us-east-1`, calibración y lectura
   real de tapa. Guardar Shadow inicial completo y estado físico observado.
2. Interrumpir solo la conectividad del ESP32 desde el punto de acceso de prueba,
   sin mover cables energizados ni cambiar certificados, permisos o recursos AWS.
3. Con el ESP32 desconectado, pedir mediante Lambda/Alexa la posición contraria a
   la actual. La Lambda escribe `desired.cerradura`; el último `reported` puede
   quedar antiguo mientras la caja no tiene conexión. No considerarlo estado físico actualizado.
4. Guardar el Shadow completo con orden pendiente. No editar `desired` desde el
   ESP32 ni desde el diagnóstico. Las acciones sobre la cuenta las realiza una
   persona del grupo según AGENTS.md; este documento no ejecuta comandos AWS.
5. Restaurar WiFi. Observar suscripciones y petición al Shadow clásico
   `$aws/things/<thingName>/shadow/get`, con respuesta en `get/accepted`; verificar
   que el firmware procesa `state.delta` si existe. El contrato también prevé
   `update/delta` para órdenes recibidas con conexión.
6. Comprobar físicamente el movimiento y que el ESP32 publique `reported.cerradura`
   y `reported.tapa` coherentes. Cuando coincidan los estados de cerradura, no debe
   quedar un delta pendiente para ese atributo. No borrar `desired`.
7. Guardar Shadow final, logs completos relevantes, tiempos observados y video.
   El contrato no fija un máximo de reconexión: registrarlo sin inventar un umbral.
8. Un reinicio eléctrico es un ensayo adicional distinto: `CerraduraServo.iniciar()`
   ordena cerrar. Probarlo solo con arranque mecánico seguro y registrar ese cierre
   inicial por separado de la posterior sincronización.

**Resultado esperado:** reconexión y obtención del Shadow, aplicación de orden
pendiente y convergencia de `reported.cerradura` con `desired.cerradura`; tapa
reportada según el sensor real. Solo Lambda escribe `desired`, solo ESP32 `reported`.

| Etapa | Estado físico de cerradura/tapa | `desired.cerradura` | `reported.cerradura` / `reported.tapa` | Delta y evidencia |
|---|---|---|---|---|
| Con conexión, antes del corte | — | — | — | — |
| Sin conexión, con orden pendiente | — | — | — | — |
| Después de recuperar conexión | — | — | — | — |

**Resultado observado:** por completar; desconexión __ s, recuperación observada __ s.
**Estado:** pendiente. **Observaciones y evidencias:** por completar.

El flujo de recuperación sigue el contrato local y la documentación de
[intercambio de estado de Device Shadow, AWS](https://docs.aws.amazon.com/iot/latest/developerguide/device-shadow-data-flow.html).
No se revisó ni modificó la cuenta AWS durante la preparación de estos procedimientos.
