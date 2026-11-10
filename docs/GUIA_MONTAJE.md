# Montaje y diagnósticos del prototipo

El [informe](../INFORME.md) presenta los resultados finales. Esta guía conserva
el detalle práctico del montaje de mesa entregado y de los programas de
diagnóstico, sin duplicar sus conclusiones.

## 1. Montaje realizado

El equipo confirmó el montaje de la
[fotografía](evidencias/MontajeDeComponentes.jpg), basado en el
[circuito SVG](diagramas/circuito.svg): ESP32 DOIT DevKit V1, SG90, sensor
magnético de dos contactos e imán, protoboard, Dupont y USB de datos.
No hay carcasa ni pestillo acoplado; el servo se mueve sin carga de bloqueo.

| Terminal | Conexión documentada |
|---|---|
| USB del ESP32 | Computadora; única alimentación del montaje probado. |
| SG90 naranja | GPIO18. |
| SG90 rojo | VIN del ESP32 alimentado por USB. |
| SG90 marrón | GND de la fila inferior del ESP32. |
| Reed, cable 1 | a50; puente b50 hacia GPIO4. |
| Reed, cable 2 | a52; puente b52 hacia GND superior. |

a50/b50 forman un contacto; a52/b52, otro separado. Ambos GND comparten
referencia. El SVG no es un mapa físico de pines: las etiquetas de la placa
identifican los terminales. El sensor usa `INPUT_PULLUP`: LOW con imán cerca
representa tapa cerrada y HIGH con imán lejos, abierta. Los colores descritos
corresponden al montaje comunicado; no sustituyen la identificación del ejemplar.

Los [parámetros](../firmware/include/ConfiguracionHardware.h) son GPIO18,
GPIO4 y posiciones solicitadas de 45° cerrada / 135° abierta. Son consignas
del código, no una medición angular ni calibración de un pestillo. El firmware
integrado ordena cerrar al iniciar y mantiene PWM; no hace `detach()` automático.

## 2. Alimentación alternativa para una integración mecánica

La fuente regulada externa de 5 V y el capacitor no se instalaron en el
ensayo fotografiado. El contrato los conserva como alternativa para un montaje
con mayor demanda de corriente. Los pasos siguientes describen esa alternativa;
no se presentan como conexiones realizadas ni como tensión/corriente medidas.

Con USB y fuente desconectados, servo sin carga y eje libre:

| Paso | Conexión o revisión de la alternativa externa |
|---|---|
| S1 | Negativo de fuente identificada a GND del ESP32. |
| S2 | GND del servo a la referencia común. |
| S3 | Positivo externo al positivo del servo; separado de VIN, 3V3, GPIO y positivo USB. |
| S4, opcional | Capacitor + al positivo de alimentación del servo. |
| S5, opcional | Capacitor − a GND; comprobar polaridad y ausencia de cortocircuito. |
| S6 | Señal del servo a GPIO18; el GPIO no alimenta el motor. |

Se recomienda 470–1000 µF con tensión nominal superior a 5 V, preferiblemente
16 V. Esa tensión nominal no es la alimentación: se aplica la tensión de 5 V
del circuito. Si no se instala, se omiten S4 y S5 y se registra su ausencia.
El capacitor no reemplaza una fuente adecuada. No descargarlo con un
cortocircuito; verificar que no conserve tensión antes de manipularlo.

Identificar salida, regulación, polaridad y corriente declaradas del adaptador
y del servo. La inspección visual y los colores no miden tensión ni continuidad.
Esta última se mide sin energía. Utilizar instrumento y ayuda competente si
hay dudas; no abrir fuentes, manipular 220 V ni cortar cables de alimentación.
El criterio de corriente se obtiene de la documentación del ejemplar utilizado.

## 3. Diagnóstico del servo

Los programas están en [firmware/pruebas](../firmware/pruebas/README.md).
Cada carga reemplaza el firmware de la placa; no mezcla diagnósticos con la
aplicación integrada. Se cargan con los periféricos separados y luego se
desconecta la alimentación antes de cablear. Los comandos son una referencia
de operación, no acciones ejecutadas durante la revisión documental.

```powershell
pio run -d firmware/pruebas -e servo
pio run -d firmware/pruebas -e servo -t upload --upload-port COMx
pio device monitor -d firmware/pruebas -e servo --port COMx
```

El monitor usa 115200 baudios y envío de línea con Enter. Cerrar el monitor
antes de otra carga; seleccionar el puerto de la placa correcta.

| Comando | Comportamiento real del diagnóstico |
|---|---|
| Arranque | PWM inactivo; sin barrido ni movimiento automático. |
| `iniciar` | Activa PWM y solicita 90° de referencia, sin definir abierta/cerrada. Repetirlo activo no mueve. |
| `+` / `-` | Cambia 1°. |
| Entero | Acepta 45°–135°, con diferencia máxima de 5° y al menos 300 ms desde el movimiento anterior. |
| `estado` / `ayuda` | Muestra el último ángulo solicitado y el estado de PWM o la ayuda. |

El primer posicionamiento puede ser amplio: se realiza sin pestillo ni carga.
El mapeo de pulsos es el predeterminado de ESP32Servo, como en `CerraduraServo`.
El ángulo mostrado es una solicitud, no una medición del eje. La ventana limita
la exploración y no demuestra topes físicos seguros de cualquier SG90.
Ante atasco, calentamiento anormal o reinicios, detener y revisar sin energía.
Esperar que termine el movimiento antes del apagado normal. No recablear
energizado ni ordenar movimiento mientras una de las alimentaciones esté ausente.

Para acoplar un pestillo en una extensión: revisar la geometría sin energía,
explorar posiciones progresivas, evitar topes, fijar sin forzar y comprobar que
el cierre se sostenga sin par continuo. No usar 90° con un mecanismo acoplado
sin verificar recorrido libre; tampoco ampliar la ventana sin revisar el servo.
La configuración se concentra en `ConfiguracionHardware.h` y cualquier cambio
se coordina conforme a los contratos.

## 4. Diagnóstico del reed

Separar servo y su alimentación para la prueba aislada. Cargar `reed`, apagar
USB y realizar las conexiones: **R1**, un contacto a GND; **R2**, el otro a
GPIO4. No se alimenta el contacto seco desde 3V3 ni 5 V.

```powershell
pio run -d firmware/pruebas -e reed
pio run -d firmware/pruebas -e reed -t upload --upload-port COMx
pio device monitor -d firmware/pruebas -e reed --port COMx
```

El diagnóstico reutiliza `SensorTapa`: muestra lectura inicial, transiciones
muestreadas, cambios confirmados y resumen cada segundo, con marcas de
milisegundos. La referencia inicial no genera aviso. `huboCambio()` se consume
una vez; el filtro exige 50 ms de estabilidad muestreada y usa resta sin signo.
Serial puede omitir rebotes y añadir retardo, por lo que no mide con precisión
todos los rebotes eléctricos. El resumen de un segundo del diagnóstico no es
el respaldo de 60 s de la aplicación integrada, ni publica en AWS.

La fijación de imán y sensor a una caja futura debe conservar la interpretación
LOW/HIGH y proteger el componente de golpes y tensión en los cables. Los
[protocolos de medición](PRUEBAS_FISICAS.md) describen cómo registrar distancia,
repetibilidad y tiempos sin sustituirlos por resultados esperados.
