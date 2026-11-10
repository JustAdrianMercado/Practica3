# Configuración de la cuenta de AWS y de AWS IoT Core

Referencia de la configuración inicial desde la consola web, conservada de la
Iteración 0. El estado de la implementación y sus evidencias se documentan en
el [informe final](../INFORME.md). Las políticas amplias sugeridas para usuarios
en el apartado 2 no constituyen una evaluación de sus permisos efectivos ni
describen los permisos del rol de ejecución de Lambda.

Todo se configura en **us-east-1 (N. Virginia)**. Las capturas compartidas
ocultan el ID de cuenta y el contenido de los certificados.

## 1. Alerta de facturación

1. Billing and Cost Management → **Budgets** → *Create budget* → plantilla **Zero spend budget** (o *Monthly cost budget* de 1 USD).
2. Poner los correos del grupo para los avisos.

## 2. Usuarios IAM para el grupo

1. IAM → **Users** → *Create user*: `santiago`, `mateo` y `lucia`, con *Provide user access to the AWS Management Console* y una contraseña temporal.
2. Permisos para la práctica: adjuntar `AWSIoTFullAccess`, `AWSLambda_FullAccess`, `AmazonDynamoDBFullAccess`, `IAMFullAccess` (Mateo crea el rol de la Lambda) y `CloudWatchLogsReadOnlyAccess`. Son permisos amplios para trabajar rápido. El informe los documenta y explica cuáles serían los mínimos (§3.2 de la consigna).
3. **No crear access keys.** Pasarle a cada integrante su URL de inicio de sesión (IAM → Dashboard → *Sign-in URL*).

## 3. Política de IoT

1. IoT Core → Security → **Policies** → *Create policy* → nombre `CajaEnigmasPolitica`.
2. Pestaña *JSON*: pegar [config/aws/politica-iot.json](../config/aws/politica-iot.json) y reemplazar `<ID_CUENTA>` por el ID de 12 dígitos de la cuenta, **solo en la consola**. En el repo queda el marcador.
3. La política solo deja que un dispositivo se conecte con el client id igual al nombre de su Thing y que use los temas de **su propio** Shadow.

## 4. Thing y certificado

1. IoT Core → Manage → All devices → **Things** → *Create things* → *Create single thing*.
2. Nombre: `caja-enigmas-01`. Shadow: **Unnamed shadow (classic)**.
3. Certificado: **Auto-generate a new certificate**.
4. Asociar la política `CajaEnigmasPolitica`.
5. **Descargar los archivos ahora**, porque la clave privada no se puede volver a bajar:
   - `xxxx-certificate.pem.crt` (certificado del dispositivo);
   - `xxxx-private.pem.key` (clave privada, **secreta**);
   - `AmazonRootCA1.pem` (CA pública de Amazon).
6. Guardarlos en `certificados-privados/` en la raíz del repo; esa carpeta está en `.gitignore`. Comprobar con `git status` que no aparezcan.
7. Repetir los pasos 1–5 con `caja-enigmas-02`, que se usa para probar la vinculación con dos cajas. Puede no tener placa: su Shadow se edita a mano.

## 5. Endpoint de datos

IoT Core → **Settings** → *Device data endpoint*: `xxxxxxxx-ats.iot.us-east-1.amazonaws.com`.
- Copiarlo en `firmware/include/ConfiguracionAws.h` (`EndpointAwsIot`).
- Pasárselo a Mateo para la variable `IOT_ENDPOINT` de la Lambda, con el prefijo `https://`.

## 6. Configurar el firmware

1. `Copy-Item firmware/include/ConfiguracionAws.ejemplo.h firmware/include/ConfiguracionAws.h`.
2. Pegar en él el endpoint y el contenido de los tres PEM, cada uno entre `R"PEM(` y `)PEM"`.
3. Lo mismo con `ConfiguracionWifi.ejemplo.h` → `ConfiguracionWifi.h`.

## 7. Comprobar el Shadow sin placa

IoT Core → **MQTT test client**:
- Suscribirse a `$aws/things/caja-enigmas-01/shadow/#`.
- Publicar en `$aws/things/caja-enigmas-01/shadow/update`:

  ```json
  { "state": { "reported": { "cerradura": "cerrada", "tapa": "cerrada", "codigoVinculacion": "0000", "firmware": "0.0.0" } } }
  ```

- En Things → `caja-enigmas-01` → *Device Shadows* → *Classic Shadow* debe verse el documento. Si se edita `desired.cerradura`, en el test client aparece el mensaje en `update/delta`.
