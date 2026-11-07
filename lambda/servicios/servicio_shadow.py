
import json


class ServicioShadow:
    def __init__(self, cliente_iot):
        self.cliente_iot = cliente_iot

    def leer_reported(self, thing_name):
        respuesta = self.cliente_iot.get_thing_shadow(
            thingName=thing_name
        )

        documento = json.loads(
            respuesta["payload"].read()
        )

        return documento.get(
            "state", {}
        ).get("reported", {})

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

        return json.loads(
            respuesta["payload"].read()
        )
