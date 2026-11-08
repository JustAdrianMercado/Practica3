
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name

from manejadores.identidad import obtener_user_id


class ConsultarTapaIntentHandler(AbstractRequestHandler):

    def __init__(self, repositorio, servicio_shadow):
        self.repositorio = repositorio
        self.shadow = servicio_shadow

    def can_handle(self, handler_input):
        return is_intent_name(
            "ConsultarTapaIntent"
        )(handler_input)

    def handle(self, handler_input):
        user_id = obtener_user_id(handler_input)

        if not user_id:
            mensaje = "No pude identificar tu usuario de Alexa."
        else:
            vinculacion = self.repositorio.obtener(user_id)

            if not vinculacion:
                mensaje = (
                    "Todavía no tienes una caja vinculada. "
                    "Primero debes vincular tu caja."
                )
            else:
                thing_name = vinculacion["thingName"]
                reported = self.shadow.leer_reported(
                    thing_name
                )

                estado = reported.get("tapa")

                if estado == "abierta":
                    mensaje = "La tapa de tu caja está abierta."
                elif estado == "cerrada":
                    mensaje = "La tapa de tu caja está cerrada."
                else:
                    mensaje = (
                        "No tengo información actualizada "
                        "sobre el estado de la tapa."
                    )

        return (
            handler_input.response_builder
            .speak(mensaje)
            .ask("¿Deseas consultar algo más?")
            .response
        )
