
import json


class ServicioShadow:
    """Acceso al Shadow clásico mediante un cliente boto3 inyectado."""

    def __init__(self, cliente_iot):
        self.cliente_iot = cliente_iot

    def leer_estado(self, thing_name):
        """Lee desired y reported juntos, en una única versión del Shadow."""
        respuesta = self.cliente_iot.get_thing_shadow(
            thingName=thing_name
        )
        documento = self._leer_documento(respuesta)
        estado = documento.get("state", {})
        if not isinstance(estado, dict):
            raise ValueError("El estado del Shadow debe ser un objeto.")
        for seccion in ("reported", "desired"):
            if seccion in estado and not isinstance(estado[seccion], dict):
                raise ValueError("Las secciones del Shadow deben ser objetos.")
        return estado

    def leer_reported(self, thing_name):
        """Conserva la interfaz de vinculación y consulta de tapa."""
        return self.leer_estado(thing_name).get("reported", {})

    def pedir_cerradura(self, thing_name, estado):
        if estado not in ("abierta", "cerrada"):
            raise ValueError(
                "El estado debe ser 'abierta' o 'cerrada'"
            )

        documento = {
            "state": {
                "desired": {
                    "cerradura": estado
                }
            }
        }

        respuesta = self.cliente_iot.update_thing_shadow(
            thingName=thing_name,
            payload=json.dumps(documento).encode("utf-8")
        )

        return self._leer_documento(respuesta)

    @staticmethod
    def _leer_documento(respuesta):
        payload = respuesta["payload"]
        try:
            documento = json.loads(payload.read())
        finally:
            payload.close()
        if not isinstance(documento, dict):
            raise ValueError("El documento Shadow debe ser un objeto.")
        return documento
