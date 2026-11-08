"""Bienvenida según la identidad y la vinculación del usuario."""

from xml.sax.saxutils import escape

from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type

from manejadores.identidad import obtener_user_id
from textos import SIN_USUARIO


class LaunchRequestHandler(AbstractRequestHandler):
    def __init__(self, repositorio):
        self.repositorio = repositorio

    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        user_id = obtener_user_id(handler_input)

        vinculacion = self.repositorio.obtener(user_id) if user_id else None

        if not user_id:
            mensaje = SIN_USUARIO
        elif vinculacion:
            thing_name = escape(vinculacion["thingName"])
            mensaje = (
                "Bienvenido a Caja de los Enigmas. "
                f"Tu caja {thing_name} está vinculada. "
                "Puedes consultar la tapa o controlar "
                "la cerradura."
            )
        else:
            mensaje = (
                "Bienvenido a Caja de los Enigmas. "
                "Todavía no tienes una caja vinculada. "
                "Puedes decir: vincula mi caja número uno "
                "con el código de vinculación."
            )

        return (
            handler_input.response_builder
            .speak(mensaje)
            .ask("¿Qué deseas hacer?")
            .response
        )
