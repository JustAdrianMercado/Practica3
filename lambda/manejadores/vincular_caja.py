
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name, get_slot

from manejadores.identidad import obtener_user_id


class VincularCajaIntentHandler(AbstractRequestHandler):

    def __init__(self, repositorio, servicio_registro,
                 servicio_shadow, prefijo):
        self.repositorio = repositorio
        self.registro = servicio_registro
        self.shadow = servicio_shadow
        self.prefijo = prefijo

    def can_handle(self, handler_input):
        return is_intent_name(
            "VincularCajaIntent"
        )(handler_input)

    def handle(self, handler_input):
        def responder(mensaje):
            return (
                handler_input.response_builder
                .speak(mensaje)
                .ask("¿Qué deseas hacer?")
                .response
            )

        user_id = obtener_user_id(handler_input)

        numero_slot = get_slot(handler_input, "numeroCaja")
        codigo_slot = get_slot(handler_input, "codigo")

        numero = numero_slot.value if numero_slot else None
        codigo = codigo_slot.value if codigo_slot else None

        if not user_id:
            return responder(
                "No pude identificar tu usuario de Alexa."
            )

        if not numero or not codigo:
            return responder(
                "Necesito el número de caja y su "
                "código de vinculación."
            )

        # Validar el identificador de la caja
        try:
            numero_int = int(numero.strip())
        except (AttributeError, TypeError, ValueError):
            return responder("El número de caja no es válido.")

        if not 1 <= numero_int <= 99:
            return responder(
                "El número de caja debe estar entre 1 y 99."
            )

        # Rechazar datos inválidos antes de llamar a AWS.
        codigo_ingresado = codigo.strip() if isinstance(codigo, str) else ""
        if not (
            codigo_ingresado.isascii()
            and codigo_ingresado.isdigit()
            and len(codigo_ingresado) == 4
        ):
            return responder("El código debe tener cuatro dígitos.")

        thing_name = f"{self.prefijo}{numero_int:02d}"

        # Verificar existencia en AWS IoT Core
        if not self.registro.existe_thing(thing_name):
            return responder(
                "La caja indicada no existe en AWS IoT Core."
            )

        # Consultar el código del Shadow
        reported = self.shadow.leer_reported(thing_name)
        codigo_real = reported.get("codigoVinculacion")

        # El contrato exige string: no convertir números del Shadow a texto.
        if (
            not isinstance(codigo_real, str)
            or codigo_ingresado != codigo_real
        ):
            return responder(
                "El código de vinculación es incorrecto."
            )

        # Persistir la vinculación
        self.repositorio.guardar(user_id, thing_name)

        return responder(
            f"Tu caja número {numero_int} "
            "fue vinculada correctamente."
        )
