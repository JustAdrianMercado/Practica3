# Diagnósticos individuales del hardware

Programas de diagnóstico separados del firmware integrado. El equipo confirmó
el funcionamiento manual de servo y reed en el prototipo de mesa; no se atribuye
a estos programas un ensayo concreto sin identificar el firmware utilizado.
Ver los resultados y fotografías en [INFORME.md](../../INFORME.md).

Este proyecto tiene su propio `platformio.ini`. El entorno `servo` compila solo
`servo/main.cpp`; `reed` compila `reed/main.cpp` y el `SensorTapa.cpp` original.
Cada entorno incluye un único `setup()` y `loop()`. El proyecto principal sigue
usando `firmware/src` y su configuración no se modifica.

## Preparación para un diagnóstico aislado

- Revisar la fuente externa regulada de **5 V**, su polaridad y el cableado antes
  de conectar el SG90. No alimentarlo desde GPIO ni desde 3V3.
- Compartir GND de la fuente del servo con GND del ESP32. Señal en GPIO18.
- Verificar las etiquetas, especificaciones y conexiones de la fuente y del servo;
  si no permiten confirmar la alimentación y la polaridad, no conectarlo todavía.
  Esta guía no presupone que haya un multímetro disponible.
- Hacer la primera prueba del servo sin carga y sin el brazo conectado a la
  cerradura. Mantener el mecanismo separado durante la exploración inicial.
- Conectar el reed de dos contactos entre GPIO4 y GND: la clase activa
  `INPUT_PULLUP`. Si se utiliza un módulo con electrónica adicional, revisar su
  conexión antes de aplicar esta guía.

## Compilar desde la raíz del repositorio

```powershell
pio run -d firmware/pruebas -e servo
pio run -d firmware/pruebas -e reed
pio run -d firmware -e caja
```

Si `pio` no está en PATH, usar el ejecutable instalado, por ejemplo:

```powershell
& "$env:USERPROFILE/.platformio/penv/Scripts/platformio.exe" run -d firmware/pruebas -e servo
```

## Ejecutar posteriormente, con el montaje revisado

Los siguientes comandos **cargan firmware**: se dejan como instrucciones para
la prueba física futura; no se han ejecutado como parte de esta implementación.
Cerrar el monitor antes de cargar el otro diagnóstico. Si hay varios puertos,
especificar el del ESP32 mediante `--upload-port` y `--port`, respectivamente.

```powershell
pio run -d firmware/pruebas -e servo -t upload
pio device monitor -d firmware/pruebas -e servo
```

Para el reed:

```powershell
pio run -d firmware/pruebas -e reed -t upload
pio device monitor -d firmware/pruebas -e reed
```

El monitor usa 115200 baudios y envía la línea al pulsar Enter. Cargar un
diagnóstico reemplaza el programa que esté en la placa; no combina ambos.

## Servo: exploración manual de ángulos

Al arrancar no se conecta el PWM ni se ordena movimiento. Con la instalación
revisada, escribir `iniciar` y Enter: activa PWM y solicita **90° como referencia
de prueba**, no como posición de apertura o cierre. La posición física anterior
es desconocida: este primer posicionamiento puede producir un movimiento amplio,
por eso se realiza sin carga y sin conexión a la cerradura.

| Comando | Acción |
|---|---|
| `iniciar` | Activar PWM y solicitar 90°; repetirlo mientras está activo no mueve nada. |
| `+` / `-` | Aumentar o reducir un grado. |
| Un entero, por ejemplo `92` | Solicitar ese ángulo si difiere como máximo 5° del anterior. |
| `estado` | Mostrar si el PWM está activo y el último ángulo solicitado. |
| `ayuda` | Recordar comandos. |

Empezar con `+` y `-`, observando cada movimiento. El programa rechaza órdenes
separadas por menos de 300 ms, entradas inválidas y ángulos fuera de **45°–135°**.
Esa ventana limita la exploración inicial; no representa los topes físicos
verificados ni define ángulos definitivos para la cerradura. No intentar forzar
los topes; interrumpir la alimentación si se observa atasco o esfuerzo mecánico.

Se utiliza el mismo mapeo predeterminado de pulsos de ESP32Servo que utiliza
`CerraduraServo`. El ángulo mostrado es el solicitado, no una medición del eje.
No hay barridos, movimientos repetitivos ni desconexión inmediata del PWM.
Mientras está activo, el servo sigue recibiendo PWM.

Anotar ángulos candidatos y observaciones. La calibración definitiva requiere
revisar después la geometría del pestillo y comprobar que el cierre pueda
sostenerse sin depender del servo energizado. Si hace falta explorar fuera de
la ventana inicial, revisar antes el servo concreto y su recorrido admisible.

## Reed: contacto, polaridad y antirrebote

El diagnóstico reutiliza `SensorTapa` sin duplicar su antirrebote de 50 ms.
Muestra la lectura inicial, cada transición eléctrica observada, cada cambio
confirmado y un resumen cada segundo. Las líneas incluyen tiempo en milisegundos.

- `LOW`: contacto eléctrico cerrado hacia GND.
- `HIGH`: contacto eléctrico abierto, elevado por `INPUT_PULLUP`.
- La interpretación de tapa es **provisional**: LOW = cerrada, HIGH = abierta.
  La lectura eléctrica instantánea puede diferir del estado confirmado durante
  el antirrebote.

Acercar y alejar el imán y anotar qué nivel aparece en cada caso. Compararlo con
la posición real prevista de la tapa para confirmar o corregir la convención
con el grupo. La referencia inicial no debe generar un evento de cambio.
Observar que los cambios confirmados solo aparezcan tras 50 ms sin variaciones
detectadas. Serial muestra las transiciones muestreadas, no garantiza capturar
todos los rebotes eléctricos; su impresión también consume tiempo.

El equipo confirmó LOW con imán cerca y HIGH con imán lejos. No registró
distancias ni mediciones instrumentales de antirrebote; el resumen Serial
permite observar el comportamiento muestreado, con las limitaciones descritas.
