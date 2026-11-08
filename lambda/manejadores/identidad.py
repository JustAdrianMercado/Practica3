"""Lectura defensiva de la identidad de Alexa definida en los contratos."""


def obtener_user_id(handler_input):
    """Devuelve el userId de context.System o None, sin recurrir a session."""
    valor = handler_input
    for atributo in ("request_envelope", "context", "system", "user",
                     "user_id"):
        valor = getattr(valor, atributo, None)
    if isinstance(valor, str) and valor.strip():
        return valor
    return None
