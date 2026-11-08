"""Punto de entrada y composición de dependencias del backend de Alexa."""

import os

import boto3

from ask_sdk_core.skill_builder import SkillBuilder

from manejadores.lanzamiento import LaunchRequestHandler
from servicios.repositorio_vinculaciones import (
    RepositorioVinculaciones
)
from servicios.servicio_shadow import ServicioShadow
from servicios.servicio_registro import ServicioRegistro
from manejadores.vincular_caja import VincularCajaIntentHandler
from manejadores.desvincular_caja import (
    DesvincularCajaIntentHandler
)
from manejadores.consultar_tapa import (
    ConsultarTapaIntentHandler
)
from manejadores.consultar_cerradura import ConsultarCerraduraIntentHandler
from manejadores.controlar_cerradura import (
    AbrirCerraduraIntentHandler,
    CerrarCerraduraIntentHandler,
)
from manejadores.errores import GlobalExceptionHandler
from manejadores.sesion import (
    HelpIntentHandler,
    CancelOrStopIntentHandler,
    FallbackIntentHandler,
    NavigateHomeIntentHandler,
    SessionEndedRequestHandler,
)


def crear_skill(repositorio, servicio_registro, servicio_shadow,
                prefijo="caja-enigmas-"):
    """Registra todos los manejadores con servicios reemplazables en tests."""
    skill_builder = SkillBuilder()
    skill_builder.add_request_handler(LaunchRequestHandler(repositorio))
    skill_builder.add_request_handler(
        VincularCajaIntentHandler(
            repositorio, servicio_registro, servicio_shadow, prefijo
        )
    )
    skill_builder.add_request_handler(
        DesvincularCajaIntentHandler(repositorio)
    )
    skill_builder.add_request_handler(
        ConsultarTapaIntentHandler(repositorio, servicio_shadow)
    )
    skill_builder.add_request_handler(
        ConsultarCerraduraIntentHandler(repositorio, servicio_shadow)
    )
    skill_builder.add_request_handler(
        AbrirCerraduraIntentHandler(repositorio, servicio_shadow)
    )
    skill_builder.add_request_handler(
        CerrarCerraduraIntentHandler(repositorio, servicio_shadow)
    )
    skill_builder.add_request_handler(HelpIntentHandler())
    skill_builder.add_request_handler(CancelOrStopIntentHandler())
    skill_builder.add_request_handler(FallbackIntentHandler())
    skill_builder.add_request_handler(NavigateHomeIntentHandler())
    skill_builder.add_request_handler(SessionEndedRequestHandler())
    skill_builder.add_exception_handler(GlobalExceptionHandler())
    return skill_builder


# 1. Configuracion de AWS
REGION = "us-east-1"

TABLA = os.environ.get(
    "TABLA_VINCULACIONES",
    "CajaEnigmasVinculaciones"
)

IOT_ENDPOINT = os.environ.get("IOT_ENDPOINT")


# 2. Conexion a DynamoDB
dynamodb = boto3.resource(
    "dynamodb",
    region_name=REGION
)

tabla = dynamodb.Table(TABLA)

repositorio = RepositorioVinculaciones(tabla)


# 3. Conexion al Device Shadow
cliente_shadow = None
servicio_shadow = None

if IOT_ENDPOINT:
    cliente_shadow = boto3.client(
        "iot-data",
        region_name=REGION,
        endpoint_url=IOT_ENDPOINT
    )

    servicio_shadow = ServicioShadow(cliente_shadow)


# 4. Conexion al registro de Things
cliente_registro = boto3.client(
    "iot",
    region_name=REGION
)

servicio_registro = ServicioRegistro(
    cliente_registro
)


# 5. Registrar manejadores de Alexa
sb = crear_skill(
    repositorio,
    servicio_registro,
    servicio_shadow,
    os.environ.get("PREFIJO_THING", "caja-enigmas-")
)
# 6. Punto de entrada de AWS Lambda
lambda_handler = sb.lambda_handler()
