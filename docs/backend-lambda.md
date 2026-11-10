# Backend Lambda: auditoría, paquete y mantenimiento

Documentación técnica complementaria del [informe principal](../INFORME.md).
Consolida los registros de auditoría y despliegue aportados por **Mateo Rojas**;
las explicaciones de arquitectura, clases, secuencias y resultados están en el
informe. Las cifras del paquete son resultados históricos del 09/11/2026,
no una reconstrucción realizada al reorganizar esta documentación.

## 1. Procedencia y evolución

| Fecha / referencia | Hecho registrado |
|---|---|
| Auditoría del 07/11 | Se conservaron las 67 pruebas anteriores y se añadieron nueve regresiones en `test_auditoria.py`; 76 pruebas aprobadas con Python 3.12.10. |
| Referencias de aquella auditoría | `origin/main` local `747c917` y `HEAD` `7643840`; describen esa revisión histórica, no el estado remoto actual. |
| Preparación del 09/11 | Se reconstruyó el paquete con las fuentes revisadas en `47de880`, conservando el ZIP anterior. |
| Captura 04 | Ejecución de `$LATEST` con el mismo hash del paquete definitivo. No identifica por sí sola el intent ni el endpoint de Alexa. |
| Revisión de integración del 10/11 | El informe registra runtime Python 3.12, x86_64, handler y endpoint de Alexa sin alias; el hash observado coincide con el paquete documentado. |
| Revisión documental final | 76 pruebas locales aprobadas con Python 3.13.15 y los paquetes fijados; cero intentos de red durante la suite. Es una ejecución diferente de la histórica con Python 3.12.10. |

La atribución de cambios se conserva en el historial Git, en el apartado 8.4 del
informe y en la [planificación original](planificacion/00-resumen.md).

## 2. Hallazgos corregidos en el desarrollo

| Hallazgo reproducido | Corrección y comprobación conservadas |
|---|---|
| Identidad incompleta de Alexa | `obtener_user_id` recorre defensivamente `context.System.user`; no usa `session.user` como alternativa ni consulta AWS sin identidad. Tres métodos de test recorren múltiples solicitudes y contextos ausentes/vacíos. |
| Código reportado numérico | Se exige string y se conservan ceros iniciales; las regresiones rechazan un entero y aceptan el código ficticio `0421`. |
| Formato de código inválido consultaba AWS | Validación previa de cuatro dígitos ASCII; códigos cortos, Unicode, alfanuméricos y blancos no llaman al registro ni al Shadow. |
| Texto dinámico sin escape en SSML | La bienvenida escapa XML; el test verifica que el nombre leído no introduzca etiquetas. |
| Desvinculación sin orientación | Si no hay relación, se explica cómo vincular sin ejecutar `DeleteItem`. |
| Documentación de runtime y configuración desactualizada | Se distinguió Python 3.12 de AWS de los intérpretes usados en las revisiones locales; las evidencias se describen según su fecha. |
| Compresión indiscriminada del directorio | La receta selecciona fuentes y dependencias, excluye tests y lanzadores Windows y valida el contenido del ZIP. |

Las regresiones están en [test_auditoria.py](../lambda/tests/test_auditoria.py).
Los flujos de [test_flujos_skill.py](../lambda/tests/test_flujos_skill.py)
mantienen servicios reales con boto3 simulado: comprueban dos usuarios, cambio
y eliminación aislados. Los subtests no se cuentan como pruebas adicionales.

El backend no configura explícitamente timeouts ni reintentos de boto3.
La auditoría histórica registró conexión/lectura de 60 s y `retries=None` en
`Config()`; no deben confundirse con el timeout de 3 s de la función registrado
en la revisión de integración. Un timeout del runtime no puede recuperarse
desde el manejador global. El presupuesto de tiempo extremo a extremo se
analiza en el informe sin atribuirle valores experimentales inexistentes.

La desvinculación es inmediata, sin confirmación adicional; Stop/Cancel cierran
la conversación sin revertir una orden escrita. `NavigateHomeIntent` conserva
un cierre defensivo si llega directamente al backend. Las consultas devuelven
el último reporte, sin comprobar conectividad ni antigüedad. El código de cuatro
dígitos no tiene límite de intentos y no implementa Account Linking/OAuth.

## 3. Registro del paquete definitivo

| Dato | Resultado histórico del 09/11 |
|---|---|
| Artefacto local, excluido de Git | `lambda/caja-enigmas-skill.zip` |
| Ruta original de construcción | `M:\IOT\practica3\Practica3\lambda\caja-enigmas-skill.zip` |
| Tamaño comprimido | 18 245 491 bytes (17,40 MiB). |
| Tamaño descomprimido | 26 213 967 bytes. |
| Contenido | 2 851 archivos, sin rutas duplicadas; CRC correcto mediante `ZipFile.testzip()`. |
| SHA-256 hexadecimal | `60cf2ee785a03375b7b365eef36f80bb4e60615143376d3f1d3c5ecaa2b46bd7` |
| SHA-256 base64 | `YM8u54WgM3W3s2Xu82+Au05gYVFDN20/HTxeyqK0a9c=` |
| Destino | Python 3.12, Linux x86_64; handler `lambda_function.lambda_handler`. |
| Fuentes | 16 archivos de producción idénticos a las fuentes auditadas. |
| Dependencias | 14 distribuciones; 2 821 archivos coincidentes en tamaño y SHA-256 con los registros de instalación. Los `RECORD` se regeneraron para el contenido conservado. |
| Respaldo anterior | `caja-enigmas-skill.anterior-a3c6c6261a3e.zip`, 18 248 513 bytes. |
| SHA-256 del respaldo | `a3c6c6261a3ec30a63736bc993a852b7fb4c86d6d7107b8703d42cf27eb39111` |

Los módulos actualizados respecto del paquete anterior fueron
`consultar_cerradura.py`, `consultar_tapa.py`, `controlar_cerradura.py`,
`desvincular_caja.py`, `identidad.py`, `lanzamiento.py` y `vincular_caja.py`.
Las fuentes nuevas se tomaron de `lambda/`, sin reutilizar esas copias antiguas
de `paquete/`. Las versiones exactas de las 14 distribuciones se conservan en
[requirements-despliegue.txt](../lambda/requirements-despliegue.txt), mientras
[requirements.txt](../lambda/requirements.txt) declara los rangos de desarrollo.

La validación histórica comprobó dos binarios ELF x86_64 de `charset_normalizer`
para CPython 3.12, con etiquetas `manylinux_2_17_x86_64`,
`manylinux2014_x86_64` y `manylinux_2_28_x86_64`. Sus referencias llegaban a
`GLIBC_2.14`, frente a glibc 2.34 del destino Amazon Linux 2023. Las demás
distribuciones eran wheels sin binarios específicos de plataforma. Fue una
inspección estática: no se ejecutaron esos binarios Linux en Windows.

Se repitieron las 76 pruebas sobre el ZIP extraído con `-I -S -B` y se comprobó
el origen de los módulos. Una comprobación adicional importó el handler con
clientes boto3 reales, validó parámetros contra los modelos de botocore y usó
`Stubber` para el despacho de `LaunchRequest` y la lectura DynamoDB. Se
registraron cero intentos de red y 23 `SyntaxWarning` del SDK, sin fallos de
la suite. Esos avisos pertenecen a aquel entorno Python 3.12.10.

El paquete mantuvo permisos POSIX `0644`, licencias, metadatos y módulos
`docs/*.py` de los SDK. Se excluyeron tests, documentación del proyecto,
bytecode, cachés, lanzadores Windows y archivos privados. Las únicas CA
incluidas eran públicas: 126 de `botocore/cacert.pem` y 118 de
`certifi/cacert.pem`. El análisis incluyó modelos `.json.gz`; los identificadores
terminados en `EXAMPLE` de modelos oficiales RDS/STS se clasificaron como
ejemplos del SDK, sin alterar sus archivos. No se registraron secretos del
proyecto en ese paquete.

Los registros originales de aquella validación eran archivos locales ignorados
bajo `lambda/paquete/validacion-20261109T142019Z/`: `auditoria.json`,
`contenido-zip.json`, `pruebas-zip.log`, `suite-aislado.json`,
`arranque-aislado.json` y `revalidacion-tras-apagado.json`. Esta última
comprobó nuevamente CRC, hashes de los 2 851 archivos, las 16 fuentes,
los 13 archivos de tests y las 14 versiones. Sus nombres se conservan como
procedencia histórica, sin enlaces a artefactos privados ausentes del repositorio.

## 4. Empaquetado reproducible de referencia

Desde la raíz del repositorio, con Python 3.12 disponible. La receta procede
del README original de Mateo; usa el archivo de versiones fijadas, genera
destinos nuevos y conserva los anteriores. Está dirigida a x86_64 y no debe
reutilizarse para arm64. Preparar un paquete es una operación local distinta
de desplegarlo. Esta reorganización documental no ejecuta la receta.

```powershell
Set-Location lambda
$marca = Get-Date -Format 'yyyyMMdd-HHmmss'
$directorioPaquete = Join-Path (Get-Location).Path ('paquete\' + $marca)
$archivoZip = Join-Path (Get-Location).Path ('caja-enigmas-skill-' + $marca + '.zip')
if ((Test-Path -LiteralPath $directorioPaquete) -or (Test-Path -LiteralPath $archivoZip)) {
    throw 'El destino ya existe; elige otra marca sin sobrescribirlo.'
}
[System.IO.Directory]::CreateDirectory($directorioPaquete) | Out-Null
py -3.12 -m pip install -r requirements-despliegue.txt -t $directorioPaquete --platform manylinux2014_x86_64 --implementation cp --python-version 3.12 --only-binary=:all: --no-compile
if ($LASTEXITCODE -ne 0) { throw 'Falló la instalación de dependencias.' }
foreach ($modulo in @('manejadores', 'servicios')) {
    $destinoModulo = Join-Path $directorioPaquete $modulo
    [System.IO.Directory]::CreateDirectory($destinoModulo) | Out-Null
    Copy-Item -Path (Join-Path $modulo '*.py') -Destination $destinoModulo
}
Copy-Item -LiteralPath .\lambda_function.py, .\textos.py -Destination $directorioPaquete

# Probar las dependencias elegidas sin usar los paquetes globales de Python.
$probarDependencias = @'
from pathlib import Path
import sys
import unittest
backend, dependencias = (Path(p).resolve() for p in sys.argv[1:])
sys.path[:0] = [str(backend), str(dependencias)]
suite = unittest.defaultTestLoader.discover(str(backend / 'tests'))
resultado = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not resultado.wasSuccessful())
'@
py -3.12 -I -S -B -c $probarDependencias (Get-Location).Path $directorioPaquete
if ($LASTEXITCODE -ne 0) { throw 'Fallaron los tests con las dependencias elegidas.' }

# Filtrar el ZIP evita incluir tests o lanzadores .exe traídos por pip.
# Las dos CA públicas del SDK fueron autorizadas; no son certificados del Thing.
$crearZip = @'
import hashlib
from pathlib import Path
import stat
import sys
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

raiz, salida = (Path(p).resolve() for p in sys.argv[1:])
ca_publicas = {'botocore/cacert.pem', 'certifi/cacert.pem'}
prohibidas = {'.csv', '.key', '.p12', '.pfx', '.jks', '.keystore',
              '.crt', '.cer', '.der', '.pem', '.exe', '.pyd', '.dll',
              '.pyc', '.pyo', '.tmp'}
with ZipFile(salida, 'x', ZIP_DEFLATED, compresslevel=9) as archivo:
    for ruta in sorted(raiz.rglob('*')):
        if ruta.is_symlink():
            raise ValueError('No se admiten enlaces simbólicos')
        if not ruta.is_file():
            continue
        relativa = ruta.relative_to(raiz)
        nombre = relativa.as_posix()
        partes = tuple(p.lower() for p in relativa.parts)
        hoja = partes[-1]
        if partes[0] == 'bin' or any(p in {
            'tests', 'test', '__pycache__', '.git', '.aws',
            'certificados-privados', 'examples'
        } for p in partes):
            continue
        if hoja.startswith(('.env', 'test_', 'config.local', 'secrets.')):
            continue
        if hoja in {'credentials', 'credentials.json', 'direct_url.json',
                    'examples-1.json', 'examples-1.json.gz'}:
            continue
        if relativa.suffix.lower() in prohibidas and nombre not in ca_publicas:
            continue
        licencia = any(p.endswith('.dist-info') for p in partes) and (
            'licenses' in partes or hoja.startswith(('license', 'notice'))
        )
        if not licencia and (relativa.suffix.lower() in {'.md', '.rst'}
                             or hoja.startswith('readme')):
            continue
        info = ZipInfo.from_file(ruta, arcname=nombre)
        info.create_system = 3
        info.external_attr = (stat.S_IFREG | 0o644) << 16
        info.compress_type = ZIP_DEFLATED
        archivo.writestr(info, ruta.read_bytes())
with ZipFile(salida) as archivo:
    assert archivo.testzip() is None
    nombres = set(archivo.namelist())
    assert {'lambda_function.py', 'textos.py', 'manejadores/identidad.py',
            'servicios/servicio_shadow.py', 'boto3/__init__.py',
            'ask_sdk_core/__init__.py'} <= nombres
    assert not any(n.startswith('paquete/') for n in nombres)
    fuentes = [Path('lambda_function.py'), Path('textos.py')]
    fuentes += list(Path('manejadores').glob('*.py'))
    fuentes += list(Path('servicios').glob('*.py'))
    assert all(archivo.read(p.as_posix()) == p.read_bytes() for p in fuentes)
    assert salida.stat().st_size < 50 * 1024**2
    assert sum(i.file_size for i in archivo.infolist()) < 250 * 1024**2
print(salida)
print('Bytes:', salida.stat().st_size)
print('SHA256:', hashlib.sha256(salida.read_bytes()).hexdigest())
'@
py -3.12 -c $crearZip $directorioPaquete $archivoZip
if ($LASTEXITCODE -ne 0) { throw 'Falló el empaquetado; no subir ese archivo.' }
py -3.12 -m zipfile -l $archivoZip
Set-Location ..
```

El ZIP contiene `lambda_function.py`, `textos.py`, `manejadores/`, `servicios/`
y dependencias en la raíz, sin carpeta envolvente. Se conservan licencias y
módulos de documentación del SDK usados en ejecución. Las dos CA públicas
autorizadas no son certificados del Thing. Antes de una actualización manual,
se comparan fuentes, dependencias, contenido, CRC y hash del nuevo artefacto.

## 5. Referencia de configuración y comprobación manual

Las configuraciones funcionales se explican en los apartados 3.3–3.5 del
[informe](../INFORME.md). Los recursos se administran manualmente desde la
consola, en `us-east-1`; estos pasos son una referencia de mantenimiento.

1. Lambda → `caja-enigmas-skill`: identificar la versión o alias efectivo,
   Python 3.12, x86_64 y `lambda_function.lambda_handler`.
2. Revisar `TABLA_VINCULACIONES`, `PREFIJO_THING` e `IOT_ENDPOINT`; el último
   utiliza `https://` y el endpoint de datos ATS del grupo.
3. Revisar el rol real, su confianza en `lambda.amazonaws.com`, políticas
   activas, límites y permisos de CloudWatch Logs. La política de invocación
   ASK es distinta del rol de ejecución.
4. En DynamoDB, contrastar partición `userId` String, sin sort key y capacidad
   on-demand. Los atributos guardados son `thingName` y fecha UTC `+00:00`.
5. Para una nueva carga, usar Code → Upload from → .zip file. Conservar
   respaldo, esperar la actualización y contrastar el hash del artefacto.
6. En Alexa, contrastar el ARN de Endpoint y la condición del Skill ID del
   disparador. Si se usa un alias, comprobar su versión efectiva; actualizar
   `$LATEST` por sí solo no cambia un alias.
7. Para pruebas de consola, construir eventos con identidad en
   `context.System.user.userId`; [apoyo.py](../lambda/tests/apoyo.py) contiene
   ejemplos ficticios completos de `LaunchRequest`, `IntentRequest` y
   `SessionEndedRequest`. El simulador y los slots de voz son otra comprobación.

| Escenario de regresión de mantenimiento | Criterio observable |
|---|---|
| Usuario sin relación, slots incompletos y número/código inválidos | Orientación o rechazo; sin una nueva orden ni sustitución indebida de la relación. |
| Thing inexistente y código incorrecto | Rechazo; la relación anterior se conserva. |
| Vincular y volver en otra sesión | Mismo `thingName` persistente; fecha UTC al guardar. |
| Consultar tapa y cerradura | Último `reported`, dato desconocido si falta y advertencia si la orden difiere. |
| Abrir/cerrar y dispositivo desconectado | Solo cambia `desired`; distinguir recepción, reporte y movimiento observado. |
| Dos usuarios, reemplazo y desvinculación | Resolver cada petición de forma aislada; eliminar solo la relación elegida. |
| Help/Fallback/Cancel/Stop/NavigateHome/SessionEnded | Ayuda, cierre o respuesta vacía según la solicitud; sin revertir órdenes anteriores. |
| CloudWatch | Correlacionar versión, `Duration`, `Billed Duration`, `Max Memory Used` e `Init Duration` cuando exista. No confundir duración Lambda con tiempo de voz a servo. |

Las capturas históricas están catalogadas en el apartado 8.2 del informe:
código (01–02), disparador (03), ejecución/hash (04), relación almacenada (05),
Shadow (06) y logs del 07/11 (07). El catálogo conserva los límites de cada
evidencia y no atribuye un intent ni un movimiento físico a una captura que
no los muestra.

## 6. Referencias técnicas del material original

Se conservan las referencias oficiales utilizadas en los aportes de Mateo:

- [paquete de despliegue](https://docs.aws.amazon.com/lambda/latest/api/API_GetFunctionConfiguration.html#lambda-GetFunctionConfiguration-response-CodeSha256).
- [configuración de boto3](https://docs.aws.amazon.com/boto3/latest/guide/configuration.html).
- [logs de Lambda](https://docs.aws.amazon.com/lambda/latest/dg/python-logging.html).
- [guía oficial de paquetes Lambda](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html).
- [identificadores de ejemplo](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-keys-admin-managed.html).
- [delegación de diálogo de Alexa](https://developer.amazon.com/en-US/docs/alexa/custom-skills/delegate-dialog-to-alexa.html).
- [convención de handlers](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html).
- [procedimiento oficial](https://docs.aws.amazon.com/lambda/latest/dg/configuration-function-zip.html).
- [GetThingShadow](https://docs.aws.amazon.com/boto3/latest/reference/services/iot-data/client/get_thing_shadow.html).
- [UpdateThingShadow](https://docs.aws.amazon.com/boto3/latest/reference/services/iot-data/client/update_thing_shadow.html).
- [SDK de Alexa](https://developer.amazon.com/en-US/docs/alexa/alexa-skills-kit-sdk-for-python/develop-your-first-skill.html).
- [referencia de autorización de IoT](https://docs.aws.amazon.com/service-authorization/latest/reference/list_iot.html).
- [política administrada oficial](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSLambdaBasicExecutionRole.html).
- [guía oficial de integración](https://developer.amazon.com/en-US/docs/alexa/custom-skills/host-a-custom-skill-as-an-aws-lambda-function.html).
- [semántica oficial](https://developer.amazon.com/en-US/docs/alexa/custom-skills/standard-built-in-intents.html#amazon-navigatehomeintent).

Para comparar invocaciones, identificar frías/calientes y correlacionar versión, solicitud y marcas temporales, sin activar DEBUG de boto3 ni registrar eventos privados.

Para documentar una regresión se conservan fecha, versión probada, responsable,
entrada, observación y archivo de evidencia. Cuando intervengan usuarios A/B,
se utilizan seudónimos estables y copias con datos privados ocultos; no se
exportan CSV con identificadores personales. La política completa del rol,
la de invocación y el endpoint efectivo se contrastan por separado, sin
inferirlos únicamente del estado de una captura de ejecución.
