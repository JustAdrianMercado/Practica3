
from datetime import datetime, timezone


class RepositorioVinculaciones:
    def __init__(self, tabla):
        self.tabla = tabla

    def obtener(self, user_id):
        respuesta = self.tabla.get_item(
            Key={"userId": user_id},
            ConsistentRead=True
        )
        return respuesta.get("Item")

    def guardar(self, user_id, thing_name):
        fecha = datetime.now(timezone.utc).isoformat()

        self.tabla.put_item(
            Item={
                "userId": user_id,
                "thingName": thing_name,
                "fechaVinculacion": fecha
            }
        )

    def eliminar(self, user_id):
        self.tabla.delete_item(
            Key={"userId": user_id}
        )
