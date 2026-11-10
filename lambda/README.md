# Lambda `caja-enigmas-skill`

Backend de Alexa a cargo de Mateo Rojas, con runtime objetivo **Python 3.12**
y región **us-east-1**. Ver el [plan](../docs/planificacion/03-mateo-lambda.md),
los [contratos](../docs/contratos.md) y la
[contribución técnica para el informe](INFORME_TECNICO.md).

**Paquete definitivo preparado el 09/11/2026:**
[`caja-enigmas-skill.zip`](caja-enigmas-skill.zip) está **listo para subir a
AWS**, con las fuentes actuales y 76 pruebas aprobadas en Python 3.12.10,
también sobre el ZIP extraído con dependencias aisladas. El paquete anterior
se conservó como respaldo. Ver tamaños, SHA-256, comprobaciones y pasos de
carga manual en [DESPLIEGUE_FINAL.md](DESPLIEGUE_FINAL.md).
La Lambda y Alexa ya tuvieron pruebas reales según lo informado por Mateo;
este ZIP requiere la regresión real después de cargarlo. La prueba física
con ESP32 y servo sigue pendiente.

Entregables: [auditoría y evidencias](AUDITORIA_FINAL.md),
[aporte para INFORME.md](APORTE_INFORME.md) y
[guía de defensa](GUIA_DEFENSA.md).

## Comportamiento

| Solicitud | Resultado |
|---|---|
| `LaunchRequest` | Bienvenida y orientación según la vinculación. |
| `VincularCajaIntent` | Valida `numeroCaja` (1–99), existencia del Thing y `codigo` de cuatro dígitos contra `reported.codigoVinculacion`. Guarda o reemplaza la vinculación. |
| `DesvincularCajaIntent` | Elimina únicamente la vinculación del usuario identificado. |
| `ConsultarTapaIntent` | Consulta `reported.tapa`. |
| `ConsultarCerraduraIntent` | Informa el último `reported.cerradura`; avisa si `desired.cerradura` válido difiere o aún no existe confirmación reportada. |
| `AbrirCerraduraIntent` / `CerrarCerraduraIntent` | Escriben únicamente `desired.cerradura = "abierta"` / `"cerrada"`. Confirman el envío, sin afirmar que el servo se movió. |
| `AMAZON.HelpIntent` / `AMAZON.FallbackIntent` | Ayuda en español y nueva oportunidad de hablar. |
| `AMAZON.CancelIntent` / `AMAZON.StopIntent` | Despedida y cierre de sesión, sin modificar la caja. |
| `AMAZON.NavigateHomeIntent` | Cierre defensivo si se recibe este intent directamente. |
| `SessionEndedRequest` | Respuesta vacía, sin voz, tarjetas ni directivas. |
| Excepciones durante el despacho | Respuesta genérica en español y logging de categoría/operación permitidas. |

Los intents que consultan o controlan una caja usan
`context.System.user.userId` para resolver su `thingName` en DynamoDB en cada
petición. No hay una caja fija ni una vinculación compartida en memoria.
`desired` y `reported` se comparan en **una única lectura** del Shadow clásico,
sin `shadowName`. Una actualización aceptada por AWS no confirma el movimiento
del actuador; esa confirmación corresponde al ESP32 mediante `reported`.

`AMAZON.NavigateHomeIntent` figura en los contratos, pero Alexa normalmente lo
procesa en dispositivos con pantalla para salir de la skill. El manejador
defensivo conserva ese cierre para pruebas con eventos JSON; no se debe usar
como una bienvenida. Ver la [referencia oficial de intents](https://developer.amazon.com/en-US/docs/alexa/custom-skills/standard-built-in-intents.html#amazon-navigatehomeintent).

## Estructura e inyección de dependencias

```text
lambda/
  lambda_function.py         crear_skill(...), clientes AWS y lambda_handler
  textos.py                  Respuestas compartidas de los manejadores nuevos
  manejadores/
    lanzamiento.py           LaunchRequestHandler
    identidad.py             obtener_user_id desde context.System.user
    vincular_caja.py          VincularCajaIntentHandler
    desvincular_caja.py       DesvincularCajaIntentHandler
    consultar_tapa.py         ConsultarTapaIntentHandler
    consultar_cerradura.py    ConsultarCerraduraIntentHandler
    controlar_cerradura.py    Clase común y manejadores de apertura/cierre
    sesion.py                 Help, Cancel/Stop, Fallback, NavigateHome, fin
    errores.py                GlobalExceptionHandler
  servicios/
    repositorio_vinculaciones.py   obtener, guardar, eliminar
    servicio_registro.py           existe_thing
    servicio_shadow.py             leer_estado, leer_reported, pedir_cerradura
  requirements.txt
  tests/                     unittest; AWS simulado con mocks
  INFORME_TECNICO.md          Arquitectura, clases, secuencias y permisos
  AUDITORIA_FINAL.md          RF/RNF, evidencias y entrega por Git
  APORTE_INFORME.md           Secciones listas para integrar con Lucía
  GUIA_DEFENSA.md             Clases, métodos y explicación individual
```

`crear_skill(repositorio, servicio_registro, servicio_shadow, prefijo)` registra
todos los manejadores en `SkillBuilder`. Los servicios reciben una tabla o un
cliente de boto3 por constructor. `leer_estado` agrega la lectura conjunta de
las secciones del Shadow y `leer_reported` conserva su interfaz anterior.
Los payloads de respuesta se cierran después de leerlos, incluso si el JSON es
inválido. Los errores de AWS se propagan hasta el manejador global.

El logging propio registra exclusivamente categorías y operaciones de listas
permitidas. No registra la solicitud completa, `userId`, slots, códigos de
vinculación, tokens, mensajes de excepción ni tracebacks. No habilitar logging
de depuración de boto3/botocore para guardar evidencias.

## Dependencias y configuración

[requirements.txt](requirements.txt) declara `ask-sdk-core>=1.19,<2` y
`boto3>=1.34,<2`; sus dependencias transitivas incluyen `ask-sdk-model` y
`botocore`. No se agregaron nuevas dependencias de ejecución.

| Variable | Valor previsto |
|---|---|
| `TABLA_VINCULACIONES` | `CajaEnigmasVinculaciones` (también es el valor por defecto). |
| `PREFIJO_THING` | `caja-enigmas-` (también es el valor por defecto). |
| `IOT_ENDPOINT` | `https://<endpoint-datos-ATS>.iot.us-east-1.amazonaws.com` del grupo. Obligatoria para operaciones de Shadow. |

El handler de AWS es **`lambda_function.lambda_handler`**. Los clientes se
reutilizan durante la vida del entorno de Lambda y usan `us-east-1`. En AWS,
boto3 obtiene autorización del rol de ejecución; no se incluyen access keys ni
un perfil personal en el paquete. El perfil `caja-enigmas` se reserva para la
CLI local cuando esté disponible.

## Pruebas locales

Desde la raíz del repositorio, con las dependencias instaladas:

```powershell
py -3.12 -m pip install -r lambda/requirements.txt
py -3.12 -m unittest discover -s lambda/tests -v
py -3.12 -m compileall -q lambda/lambda_function.py lambda/textos.py lambda/manejadores lambda/servicios lambda/tests
```

Resultado de la auditoría: **76 pruebas aprobadas** (67 anteriores conservadas
y 9 regresiones nuevas); `compileall` terminó sin errores. Entorno ejecutado:
Python **3.12.10**, `ask-sdk-core` **1.19.0**, `ask-sdk-model` **1.82.0**,
`boto3` y `botocore` **1.43.126**. La suite también pasó con las dependencias
del paquete Linux x86_64 aisladas de las bibliotecas globales, ejecutando los
tests en Windows. Los `SyntaxWarning` del SDK de Alexa no fueron errores.

Las pruebas nuevas incluyen despacho y serialización reales del SDK de Alexa,
clientes AWS simulados, dos usuarios y cajas, sustitución y eliminación de
vinculaciones, ceros iniciales en códigos, códigos incorrectos, Things
inexistentes, slots incompletos, estados desconocidos y pendientes, fallas de
DynamoDB/IoT y ausencia de datos privados en logs. Los clientes de arranque
también se sustituyen por mocks antes de importar `lambda_function.py`.
**No se invoca la Lambda de AWS, el simulador de Alexa ni el ESP32.**
Esto describe la suite automatizada. Las pruebas reales de Alexa comunicadas
por Mateo se registran por separado en el informe técnico y en la auditoría;
no se vuelven a afirmar como ejecutadas por esta sesión.

## Empaquetado local para subir manualmente

El paquete verificado y sus versiones fijadas están documentados en
[DESPLIEGUE_FINAL.md](DESPLIEGUE_FINAL.md) y
[requirements-despliegue.txt](requirements-despliegue.txt). La receta
siguiente permite preparar otro ZIP; los rangos de `requirements.txt`
pueden resolver versiones diferentes de las verificadas en el definitivo.

Estos pasos preparan un ZIP nuevo; no despliegan. Ejemplo para **x86_64** en
Python 3.12, desde la raíz del repositorio. La marca de tiempo permite conservar
el ZIP y el directorio de dependencias anteriores. No reutilizar los módulos
de aplicación de `paquete/`, que corresponden al código anterior a la auditoría.
Verificar la arquitectura en la consola; para arm64 se necesita otro paquete.

```powershell
Set-Location lambda
$marca = Get-Date -Format 'yyyyMMdd-HHmmss'
$directorioPaquete = Join-Path (Get-Location).Path ('paquete\' + $marca)
$archivoZip = Join-Path (Get-Location).Path ('caja-enigmas-skill-' + $marca + '.zip')
if ((Test-Path -LiteralPath $directorioPaquete) -or (Test-Path -LiteralPath $archivoZip)) {
    throw 'El destino ya existe; elige otra marca sin sobrescribirlo.'
}
[System.IO.Directory]::CreateDirectory($directorioPaquete) | Out-Null
py -3.12 -m pip install -r requirements.txt -t $directorioPaquete --platform manylinux2014_x86_64 --implementation cp --python-version 3.12 --only-binary=:all: --no-compile
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

El ZIP debe contener `lambda_function.py`, `textos.py`, `manejadores/`,
`servicios/` y las dependencias **en su raíz**, sin un directorio `paquete/`
envolvente. No copiar `tests/`, documentación, archivos privados ni
configuraciones de credenciales. `paquete/` y los ZIP ya están ignorados por
Git. La receta conserva licencias y módulos `docs/*.py` de boto3/botocore
necesarios en ejecución. Antes de subir, inspeccionar el contenido, verificar
las fuentes y repetir los tests con las dependencias elegidas. La auditoría
del 07/11 no generó un ZIP nuevo; la preparación definitiva del 09/11
reconstruyó y verificó `caja-enigmas-skill.zip`, conservando el anterior.
Las versiones resueltas pueden cambiar dentro de los rangos de
`requirements.txt`; registrarlas al
preparar el paquete final. AWS recomienda empaquetar también boto3 para evitar
mezclar versiones del runtime con dependencias locales.
[Guía oficial de paquetes Python](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html).

La actualización con estas correcciones se hace **a mano desde la consola** de
Lambda en `us-east-1`, función `caja-enigmas-skill`, pestaña Code, Upload from,
archivo ZIP, conservando el handler indicado. Este trabajo no subió código ni
modificó recursos de AWS.

## Permisos e integración pendientes

La revisión estática de
[politica-rol-lambda.json](../config/aws/politica-rol-lambda.json) y
[tabla-vinculaciones.json](../config/aws/tabla-vinculaciones.json) es coherente
con los servicios implementados. **No se verificaron los permisos efectivos,
el código desplegado ni el disparador:** esta revisión se limita al
repositorio, sin ejecutar comandos AWS. Ver el detalle y los pasos de consola en la
[revisión técnica](INFORME_TECNICO.md#revisión-de-permisos-y-configuración).

Con Lucía: comprobar el Skill ID, el disparador Alexa Skills Kit con
verificación activada y el ARN del endpoint para América; completar el modelo
`es-US` y exportarlo a `config/alexa/modelo-interaccion.es-US.json`. Este
archivo está presente y se verificó su compatibilidad con el backend en la
preparación definitiva del 09/11. La skill y el disparador ya están configurados
según Mateo; falta adjuntar sus evidencias y confirmar la verificación del
Skill ID sobre el endpoint efectivo. Ambos slots de vinculación deben ser
obligatorios y usar delegación automática del diálogo (`delegationStrategy`
`ALWAYS` para ese intent): el backend no emite `Dialog.Delegate`, sino que
responde con orientación si faltan datos. Ver la
[delegación de diálogo de Alexa](https://developer.amazon.com/en-US/docs/alexa/custom-skills/delegate-dialog-to-alexa.html).
La confirmación
de desvinculación es opcional y no está implementada: el manejador existente
elimina la vinculación inmediatamente.

Con Adrián y Santiago: comprobar el reporte real del firmware, el código de
cuatro dígitos, el movimiento del servo, la confirmación en `reported`, la
reconexión con una orden pendiente y el tiempo de extremo a extremo. Con Lucía
y Mateo: probar RF4–RF9 en el simulador, dos usuarios y el caso de caja
desconectada, y adjuntar evidencias al informe. Las pruebas con mocks no
demuestran estos resultados físicos ni los requisitos no funcionales.
