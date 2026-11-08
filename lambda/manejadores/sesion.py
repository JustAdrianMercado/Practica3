"""Intents integrados y fin de sesión sin efectos sobre la caja."""

from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name, is_request_type

from textos import AYUDA, REPREGUNTA


class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        return (
            handler_input.response_builder
            .speak(AYUDA)
            .ask(REPREGUNTA)
            .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (
            is_intent_name("AMAZON.CancelIntent")(handler_input)
            or is_intent_name("AMAZON.StopIntent")(handler_input)
        )

    def handle(self, handler_input):
        return (
            handler_input.response_builder
            .speak("Hasta luego.")
            .set_should_end_session(True)
            .response
        )


class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        return (
            handler_input.response_builder
            .speak("No entendí esa petición. " + AYUDA)
            .ask(REPREGUNTA)
            .response
        )


class NavigateHomeIntentHandler(CancelOrStopIntentHandler):
    """Cierre defensivo: normalmente Alexa procesa este intent de pantalla."""

    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.NavigateHomeIntent")(handler_input)


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # Alexa no admite voz, tarjetas ni directivas al finalizar sesión.
        return handler_input.response_builder.response
