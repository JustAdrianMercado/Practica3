
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name

from manejadores.identidad import obtener_user_id


class DesvincularCajaIntentHandler(AbstractRequestHandler):

    def __init__(self, repositorio):
        self.repositorio = repositorio

    def can_handle(self, handler_input):
        return is_intent_name(
            "DesvincularCajaIntent"
        )(handler_input)

    def handle(self, handler_input):
        user_id = obtener_user_id(handler_input)

        if not user_id:
            mensaje = (
                "No pude identificar tu usuario de Alexa."
            )
        else:
            vinculacion = self.repositorio.obtener(user_id)

            if vinculacion is None:
                mensaje = (
                    "Todavía no tienes ninguna caja vinculada. "
                    "Puedes decir: vincula mi caja uno con el código "
                    "de cuatro dígitos."
                )
            else:
                self.repositorio.eliminar(user_id)
                mensaje = (
                    "Tu caja fue desvinculada correctamente."
                )

        return (
            handler_input.response_builder
            .speak(mensaje)
            .ask("¿Deseas hacer algo más?")
            .response
        )
