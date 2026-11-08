"""Eventos de Alexa y composición para pruebas sin conexiones a AWS."""

import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# El módulo de producción compone clientes durante el arranque. Se simulan
# antes de importarlo para impedir consultas de credenciales o conexiones.
with (
    patch.dict(os.environ, {
        "IOT_ENDPOINT": "https://iot.example.invalid",
        "TABLA_VINCULACIONES": "CajaEnigmasVinculaciones",
        "PREFIJO_THING": "caja-enigmas-",
    }),
    patch("boto3.resource"),
    patch("boto3.client"),
):
    from lambda_function import crear_skill


def crear_lambda(repositorio, registro, shadow):
    return crear_skill(repositorio, registro, shadow).lambda_handler()


def evento_alexa(intent=None, usuario="usuario-01", slots=None,
                 tipo="IntentRequest"):
    """El usuario de sesión difiere para verificar el uso de context.System."""
    aplicacion = {"applicationId": "amzn1.ask.skill.prueba-local"}
    solicitud = {
        "type": tipo,
        "requestId": "solicitud-prueba",
        "timestamp": "2026-11-07T12:00:00Z",
        "locale": "es-US",
    }
    if tipo == "IntentRequest":
        solicitud["intent"] = {
            "name": intent,
            "confirmationStatus": "NONE",
            "slots": {
                nombre: {"name": nombre, "value": valor}
                for nombre, valor in (slots or {}).items()
            },
        }
    elif tipo == "SessionEndedRequest":
        solicitud["reason"] = "USER_INITIATED"

    return {
        "version": "1.0",
        "session": {
            "new": True,
            "sessionId": "sesion-prueba",
            "application": aplicacion,
            "user": {"userId": "usuario-de-sesion"},
            "attributes": {},
        },
        "context": {
            "System": {
                "application": aplicacion,
                "user": {"userId": usuario},
                "device": {
                    "deviceId": "dispositivo-simulado",
                    "supportedInterfaces": {},
                },
                "apiEndpoint": "https://api.amazonalexa.com",
                "apiAccessToken": "TOKEN_FICTICIO",
            },
        },
        "request": solicitud,
    }


def voz(respuesta):
    return respuesta["response"].get("outputSpeech", {}).get("ssml", "")
