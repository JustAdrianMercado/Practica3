"""Consulta del estado reportado y de las órdenes sin confirmar."""

from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name

from manejadores.identidad import obtener_user_id
from textos import REPREGUNTA, SIN_USUARIO, SIN_VINCULACION


class ConsultarCerraduraIntentHandler(AbstractRequestHandler):
    """Resuelve la caja del usuario sin confundir desired con reported."""

    def __init__(self, repositorio, servicio_shadow):
        self.repositorio = repositorio
        self.shadow = servicio_shadow

    def can_handle(self, handler_input):
        return is_intent_name("ConsultarCerraduraIntent")(handler_input)

    def handle(self, handler_input):
        user_id = obtener_user_id(handler_input)
        if not user_id:
            mensaje = SIN_USUARIO
        else:
            vinculacion = self.repositorio.obtener(user_id)
            if not vinculacion:
                mensaje = SIN_VINCULACION
            else:
                estado = self.shadow.leer_estado(vinculacion["thingName"])
                reportado = estado.get("reported", {}).get("cerradura")
                deseado = estado.get("desired", {}).get("cerradura")

                if reportado in ("abierta", "cerrada"):
                    mensaje = (
                        "Según el último reporte, la cerradura de tu caja "
                        f"está {reportado}."
                    )
                else:
                    mensaje = (
                        "No tengo información reportada sobre el estado "
                        "de la cerradura."
                    )

                # Una sola lectura permite comparar la misma versión.
                if deseado in ("abierta", "cerrada") and deseado != reportado:
                    accion = "apertura" if deseado == "abierta" else "cierre"
                    mensaje += (
                        " La caja todavía no confirmó la orden de "
                        f"{accion}."
                    )

        return (
            handler_input.response_builder
            .speak(mensaje)
            .ask(REPREGUNTA)
            .response
        )
