"""Comandos de voz que solo modifican desired.cerradura en el Shadow."""

from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name

from manejadores.identidad import obtener_user_id
from textos import REPREGUNTA, SIN_USUARIO, SIN_VINCULACION


class CambiarCerraduraIntentHandler(AbstractRequestHandler):
    """Comportamiento común de apertura y cierre con servicios inyectados."""

    def __init__(self, repositorio, servicio_shadow, nombre_intent, estado):
        self.repositorio = repositorio
        self.shadow = servicio_shadow
        self.nombre_intent = nombre_intent
        self.estado = estado

    def can_handle(self, handler_input):
        return is_intent_name(self.nombre_intent)(handler_input)

    def handle(self, handler_input):
        user_id = obtener_user_id(handler_input)
        if not user_id:
            mensaje = SIN_USUARIO
        else:
            vinculacion = self.repositorio.obtener(user_id)
            if not vinculacion:
                mensaje = SIN_VINCULACION
            else:
                self.shadow.pedir_cerradura(
                    vinculacion["thingName"], self.estado
                )
                accion = "abrir" if self.estado == "abierta" else "cerrar"
                mensaje = (
                    f"Envié la orden para {accion} la cerradura. "
                    "Consulta su estado para comprobar si la caja "
                    "la confirmó."
                )

        return (
            handler_input.response_builder
            .speak(mensaje)
            .ask(REPREGUNTA)
            .response
        )


class AbrirCerraduraIntentHandler(CambiarCerraduraIntentHandler):
    def __init__(self, repositorio, servicio_shadow):
        super().__init__(
            repositorio, servicio_shadow, "AbrirCerraduraIntent", "abierta"
        )


class CerrarCerraduraIntentHandler(CambiarCerraduraIntentHandler):
    def __init__(self, repositorio, servicio_shadow):
        super().__init__(
            repositorio, servicio_shadow, "CerrarCerraduraIntent", "cerrada"
        )
