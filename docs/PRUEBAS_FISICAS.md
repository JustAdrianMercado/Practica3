# Protocolos complementarios de medición física

El [informe final](../INFORME.md) conserva las comprobaciones manuales y sus
resultados cualitativos. Este archivo reúne métodos reproducibles para una
caracterización instrumental; no es una bitácora de ensayos ejecutados.
Las cantidades de los procedimientos son criterios del plan original,
no cantidades observadas. Los espacios de un registro real se completan con
datos obtenidos, sin copiar resultados esperados como observaciones.

Consultar el [montaje](GUIA_MONTAJE.md) y los [contratos](contratos.md).
Antes de recablear, desconectar USB y fuente externa si se utiliza. No
alimentar el servo desde GPIO/3V3 ni unir positivos USB y externo. La prueba
de componentes no representa automáticamente la integración con AWS.

## Datos y fuentes de un registro

Un registro identifica fecha, hora/zona, responsable, commit y firmware
realmente cargado, programa (diagnóstico o integración), Thing si aplica,
alimentación declarada, instrumentos, capacitor y fotografía del cableado.
Conserva entrada, resultado esperado, observación, fallo y archivo de evidencia.
Los [anexos](../INFORME.md#82-fotografías-y-evidencias) catalogan las imágenes
existentes; no se publican códigos reales, usuarios, tokens ni credenciales.

## 1. Alimentación y polaridad

**Alcance:** fuente externa, si se adopta para una integración mecánica.
No describe la alimentación VIN del montaje fotografiado como una fuente externa.

1. Identificar modelo, tensión/regulación, corriente y polaridad en fuente y servo.
2. Inspeccionar adaptador, cables y aislamiento sin abrir fuentes ni cortar cables.
3. Si corresponde, medir tensión y polaridad con instrumento y ayuda adecuados,
   con la fuente separada del circuito; registrar valor y método. Una etiqueta
   no equivale a una medición y la continuidad se comprueba sin energía.
4. Revisar S1–S6 de la guía: GND común, positivos separados y capacitor correcto
   o ausente. La revisión inicial no demuestra estabilidad bajo carga.

**Criterio:** alimentación identificada y compatible, polaridad inequívoca y
cableado coherente. El registro distingue información declarada de valores
medidos, sin suponer disponibilidad de multímetro.

## 2. Movimiento del servo sin carga

Con montaje revisado, eje libre y diagnóstico `servo` identificado:

1. Comprobar PWM inactivo al iniciar; enviar `estado` e `iniciar` para solicitar 90°.
2. Usar `+`/`-` y pasos de hasta 5° dentro de 45°–135°, separados al menos 300 ms.
3. Registrar orden y ángulo solicitado frente al movimiento observado y anomalías.
4. Detener ante atasco, calentamiento o reinicios; esperar el fin del movimiento
   antes de un apagado normal y recablear únicamente sin energía.

**Criterio:** respuesta visible a órdenes válidas, sin esfuerzo anormal; no se
confunde el número impreso con una medición angular. El equipo confirmó giro
sin carga, pero no se conserva una serie instrumental de este procedimiento.

## 3. Calibración de un mecanismo acoplado

Este protocolo corresponde a una extensión con caja/pestillo, fuera del
montaje de mesa entregado.

1. Revisar geometría y soporte sin energía y sin forzar el eje.
2. Presentar el brazo desacoplado; verificar que el posicionamiento de referencia
   deje recorrido libre antes de acoplarlo.
3. Explorar progresivamente posiciones que traben/destraben con margen; no ampliar
   la ventana del diagnóstico ni buscar topes sin revisar el ejemplar.
4. Registrar ángulos candidatos, repetibilidad y fotografía de brazo y pestillo.
5. Comprobar el cierre sostenido después de apagar, sin par continuo ni esfuerzo
   sobre un engranaje trabado. `estaAbierta()` refleja una orden y no prueba bloqueo.
6. Coordinar cambios de parámetros y contratos; el arranque integrado ordena cerrar.

## 4. Reed, imán y distancia

Con diagnóstico `reed`, servo separado y conexiones R1–R2 revisadas:

1. Guardar la referencia inicial y distinguirla de un cambio.
2. Acercar/retirar el imán manteniendo cada condición más de 50 ms; registrar
   HIGH/LOW y la interpretación del programa por separado.
3. Medir distancia al activar y liberar, indicando orientación y referencias.
4. Comparar con la posición física de la tapa si se usa una caja acoplada.
5. Si la interpretación se invierte, documentarla antes de cambiar contrato/código.

**Criterio:** correspondencia repetible con el contacto y la representación de
tapa. La comprobación manual del equipo registra LOW cerca / HIGH lejos;
no contiene distancias medidas ni una estadística de repetibilidad.

## 5. Antirrebote

1. Mantener el imán quieto al iniciar; no debe producir un falso evento inicial.
2. Cambiar de condición y registrar la última lectura candidata muestreada y el
   aviso confirmado; repetir ambas transiciones.
3. En reposo no deben repetirse avisos consumibles; los resúmenes periódicos no
   son eventos nuevos.
4. Estimar la diferencia entre marcas de milisegundos y anotar resolución del método.

**Criterio del código:** al menos 50 ms de estabilidad muestreada y un aviso
por cambio confirmado. Serial no captura necesariamente todos los rebotes y
añade retardo. Un ensayo corto tampoco demuestra haber cruzado el desbordamiento
de `millis()`; el cálculo usa resta sin signo para tolerarlo.

## 6. Repetibilidad del sensor — PN02

El plan original propone 30 ciclos completos: 60 comparaciones de estado.
Para cada ciclo registrar apertura y cierre, `reported.tapa`, discrepancia,
retardo, distancia/orientación del imán y evidencia. Comparar la condición
física con el Shadow del firmware integrado, no solo con Serial. Las órdenes
de tapa no deben forzar una cerradura acoplada.

**Criterio declarado:** cero discrepancias en la serie y reporte por evento
conforme al objetivo. No se atribuyen esos ciclos al ensayo cualitativo del equipo.

## 7. Respuesta extremo a extremo — PN03

El plan propone diez órdenes alternadas, con dispositivo integrado, usuario
vinculado y video que correlacione orden y servo.

1. Cada orden solicita una posición distinta; esperar que termine la anterior.
2. Registrar `t0`, fin de la orden, y `t1`, inicio visible del movimiento.
3. Calcular `t1 - t0`, promedio, máximo y resolución temporal; declarar si se usó
   voz o texto en el simulador.
4. Conservar órdenes sin movimiento como fallos; no omitirlas ni asignarles cero.

**Criterio declarado:** máximo de 3 s. No se sustituye por Duration de Lambda,
duración de unittest o timestamps del Shadow sin referencia común de la orden.

## 8. Estabilidad y frecuencia — PN01 / PN04

El protocolo original define al menos diez minutos con órdenes cada minuto:

1. Identificar programa, versión, alcance local/integrado e inicio/fin.
2. Registrar cada orden, reinicio, bloqueo, desconexión y anomalía con su evidencia.
3. En integrado, observar eventos y respaldo completo; contrastar el objetivo de
   hasta 1 s por cambio y el parámetro de 60 s de respaldo con publicaciones reales.
4. Anotar interrupciones y duración efectiva; una observación local no acredita
   estabilidad de AWS, y ausencia de reinicios no mide estabilidad eléctrica.

**Criterio declarado:** sin reinicios/bloqueos en el intervalo y reportes coherentes.
El equipo confirmó estabilidad cualitativa, sin una serie temporal registrada.

## 9. Reconexión y estado solicitado fuera de línea — PN05

El plan definía tres cortes WiFi y tres de Internet manteniendo WiFi. Las
cantidades no se atribuyen a las comprobaciones realizadas, cuyo resultado
confirmado es recuperación automática al restablecer la red.

Para un registro dirigido de sincronización:

1. Guardar estado inicial completo, versión del Shadow y observación física.
2. Interrumpir conectividad desde el punto de acceso, sin alterar certificados,
   permisos ni recursos; no mover cables energizados.
3. Desde Alexa solicitar el estado opuesto y conservar el Shadow con `desired`
   distinto de `reported`; no considerar el dato antiguo como estado actual medido.
4. Restaurar la red, observar MQTT, suscripciones y solicitud `shadow/get`.
5. Correlacionar `get/accepted` y `state.delta`, movimiento y reporte del firmware.
6. Guardar Shadow final, logs y video; no borrar `desired` desde la ESP32.

El criterio es recuperar conexión y converger al estado solicitado. El contrato
no fija un máximo de reconexión: se registra el tiempo sin inventar un umbral.
Un reinicio eléctrico es otro ensayo: el firmware ordena cerrar al iniciar.
Las acciones en AWS las realiza una persona del equipo según AGENTS.md; este
protocolo no ejecuta consultas, publicaciones ni escrituras en la cuenta.
