# Plan de Adrián Mercado — Repositorio, AWS IoT y firmware de conectividad

**Rama:** `feat/firmware-aws` (la It. 0 va directo a `main`) · **Archivos a tu cargo:** estructura del repo, `.gitignore`, `README.md`, `docs/contratos.md`, `firmware/platformio.ini`, `firmware/src/main.cpp`, `ConexionWifi.*`, `ConexionAwsIot.*`, `EstadoShadow.*`, `CodigoVinculacion.*`, `config/aws/politica-iot.json` · Ver los acuerdos en [00-resumen.md](00-resumen.md).

Sos el responsable de que el ESP32 se comunique con AWS IoT Core y de integrar el firmware con las clases de Santiago.

## Iteración 0 — jue 06 / vie 07 (mañana): base del repo y conexión con AWS

**Repositorio (a `main`, para que los demás arranquen):**
1. Estructura: `firmware/`, `lambda/`, `config/alexa/`, `config/aws/`, `docs/` (con `diagramas/`, `evidencias/` y `consigna/`).
2. `.gitignore` basado en el de PracticaMQTT, ampliado con `firmware/include/ConfiguracionAws.h`, `firmware/include/ConfiguracionWifi.h`, `*.pem.key`, `*-certificate.pem.crt` y `certificados-privados/`.
3. Importar `ConexionWifi.h/.cpp` **sin cambios** y `ConfiguracionWifi.ejemplo.h`.
4. Crear la plantilla **`ConfiguracionAws.ejemplo.h`**, con el endpoint, el nombre del Thing, AmazonRootCA1, el certificado y la clave privada como *raw string literals* vacíos.
5. `platformio.ini` con `espressif32@7.0.1` y `framework-arduinoespressif32@3.20017.0` (como en Practica2), y como dependencias `256dpi/MQTT@2.5.2`, `bblanchon/ArduinoJson@^7` y `madhephaestus/ESP32Servo`.
6. `main.cpp` mínimo que solo conecta el WiFi. Comprobar que `pio run` compila con las plantillas.
7. **`docs/contratos.md`**: los acuerdos del resumen, con los datos de Santiago (pines y alimentación). Pedir el OK de los cuatro.
8. **`INFORME.md`** con las secciones del §4.2 y el responsable de cada una (junto con Lucía).
9. Copiar la consigna en `docs/consigna/` y actualizar el `README.md`.

**AWS (consola, cuenta del grupo):**
1. Crear una alerta de facturación (Billing → Budgets, presupuesto de 1 USD) y trabajar en **us-east-1**.
2. Crear usuarios IAM para Santiago, Mateo y Lucía con acceso a la consola, sin access keys.
3. IoT Core: crear la política `CajaEnigmasPolitica` y el Thing `caja-enigmas-01` con un certificado autogenerado. Bajar el certificado, la clave privada y AmazonRootCA1 a una carpeta **fuera de Git**.
4. Guardar el JSON de la política en `config/aws/politica-iot.json`. Mínimo privilegio: `iot:Connect` con el client id igual al Thing, `iot:Publish`/`iot:Receive` sobre `$aws/things/${iot:Connection.Thing.ThingName}/shadow/*` e `iot:Subscribe` sobre el topicfilter equivalente.
5. Anotar el endpoint de datos (IoT Core → Settings) y pasárselo a Mateo.

**Conexión (adelanto de la It. 1):** primera versión de `ConexionAwsIot` que se conecta con mTLS y publica un `reported` fijo.

**Listo cuando:** el repo compila, `git ls-files` no muestra secretos y la consola de IoT muestra el Shadow de `caja-enigmas-01` con los datos publicados por la placa.

## Iteración 1 — vie 07: objeto inteligente completo (RF1–RF3)

- **`ConexionAwsIot`**, adaptada de `ConexionMqtt` de PracticaMQTT. Hacer un commit que la importe tal cual y otro que la adapte, para que el historial muestre el cambio.
  - Se conservan: `prepararHora()` (NTP antes de TLS), `cerrarConexion()`, el loop no bloqueante, la validación del payload y la regla de **no publicar desde el callback** (marca de pendiente).
  - Cambian:
    - `setCACert` + `setCertificate` + `setPrivateKey`, sin usuario ni clave;
    - client id igual al nombre del Thing;
    - buffer de unos 2048 B;
    - reintento cada ~5 s.
  - Temas: suscribirse a `$aws/things/<thing>/shadow/update/delta` y `/get/accepted`; publicar en `/update` y `/get`.
  - **Al conectar o reconectar, publicar en `/get`**: si hay un `desired` pendiente, se aplica. Es un RNF de la consigna.
- **`EstadoShadow`**: arma el JSON de `reported` y lee el `delta` con ArduinoJson. Si es lógica pura, sin Arduino, después se puede probar en la PC.
- **`CodigoVinculacion`**: genera 4 dígitos con `esp_random()` en el primer arranque, los guarda con `Preferences` (NVS) y los muestra por Serial al iniciar.
- **`main.cpp`**:
  - Une `ConexionWifi`, `ConexionAwsIot`, `CerraduraServo` y `SensorTapa`.
  - Reporta por evento (`huboCambio()` del sensor y cada movimiento del servo) y cada 60 s como respaldo.
  - Comandos Serial de depuración: `abrir`, `cerrar`, `estado` y `codigo`, adaptados del lector acotado del `main.cpp` de PracticaMQTT.
- Revisar el PR de Santiago e integrar.

**Listo cuando:**
- se cambia `desired.cerradura` en la consola y el servo se mueve, y `reported` queda igual que `desired`, sin `delta`;
- con el WiFi apagado se cambia `desired`, se restaura la red y el cambio se aplica solo.

## Iteración 2 — sáb 08: soporte a la integración

- Crear `caja-enigmas-02` (segundo Thing) para que Mateo y Lucía prueben la vinculación con dos cajas. Puede ser un Thing sin placa, cuyo Shadow se edita a mano.
- Ayudar a Mateo con los permisos de `iot-data` y a probar la cadena completa.
- **Optimizar la latencia:** `WiFi.setSleep(false)`, como en Practica2, para que el `delta` llegue rápido.

## Iteración 3 — dom 09: pruebas de RNF del firmware

| Prueba | Procedimiento |
|---|---|
| Reconexión WiFi | 3 cortes del WiFi (apagar el hotspot); medir el tiempo hasta volver a estar conectado y comprobar que se aplica el `desired` pendiente. |
| Reconexión MQTT | Bloquear Internet manteniendo el WiFi, 3 veces. |
| Frecuencia de reporte | Contar las publicaciones durante 10 min en el cliente de pruebas MQTT de la consola y verificar ≤1 s en los eventos y 60 s en el periódico. Justificar el consumo dentro de la capa gratuita. |
| Estabilidad | ≥10 min (junto con Santiago). |

## Iteración 4 — lun 09 / mar 10: informe y entrega

- Redactar en `INFORME.md`: el **diagrama de arquitectura**, la **especificación del Shadow** (`desired`, `reported`, `delta`), el **diagrama de clases del firmware**, la estructura del código del firmware y la **configuración de AWS IoT** (Thing, certificados y política justificada, sin secretos).
- Exportar `config/aws/politica-iot.json` y crear la plantilla de configuración del objeto.
- Revisar que el repo no tenga secretos y que el enlace sea accesible para el docente.

## Para la defensa: qué repasar de los demás

- Las clases de Santiago (antirrebote y ángulos del servo) y el circuito.
- La Lambda de Mateo: cómo resuelve el `userId`, cómo valida el Thing y el código, y los permisos del rol IAM.
- La skill de Lucía: intents, slots y cómo se conecta con la Lambda.
