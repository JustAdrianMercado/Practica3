"""Respuesta global y logging de categorías sin datos de la solicitud."""

import logging

from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type
from botocore.exceptions import ClientError

from textos import ERROR_GENERAL, REPREGUNTA


LOGGER = logging.getLogger(__name__)
CODIGOS_AWS = frozenset({
    "AccessDeniedException", "UnauthorizedException",
    "ResourceNotFoundException", "ThrottlingException",
    "ServiceUnavailableException", "InternalFailureException",
    "ProvisionedThroughputExceededException", "RequestLimitExceeded",
    "ConflictException",
})
OPERACIONES_AWS = frozenset({
    "DescribeThing", "GetThingShadow", "UpdateThingShadow",
    "GetItem", "PutItem", "DeleteItem",
})


class GlobalExceptionHandler(AbstractExceptionHandler):
    """No registra eventos, códigos de vinculación, tokens ni userId."""

    def __init__(self, logger=None):
        self.logger = logger if logger is not None else LOGGER

    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        categoria = "ErrorInterno"
        operacion = "NoIdentificada"
        if isinstance(exception, ClientError):
            codigo = exception.response.get("Error", {}).get("Code")
            categoria = codigo if codigo in CODIGOS_AWS else "ErrorAWS"
            if exception.operation_name in OPERACIONES_AWS:
                operacion = exception.operation_name

        # Solo valores de listas permitidas: ni str(exception) ni traceback
        # son seguros, pues pueden incluir identificadores y datos privados.
        self.logger.error(
            "Solicitud fallida: categoria=%s operacion=%s",
            categoria, operacion,
        )
        if is_request_type("SessionEndedRequest")(handler_input):
            return handler_input.response_builder.response

        return (
            handler_input.response_builder
            .speak(ERROR_GENERAL)
            .ask(REPREGUNTA)
            .response
        )
