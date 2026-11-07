
from botocore.exceptions import ClientError


class ServicioRegistro:
    def __init__(self, cliente_iot):
        self.cliente_iot = cliente_iot

    def existe_thing(self, thing_name):
        try:
            self.cliente_iot.describe_thing(
                thingName=thing_name
            )
            return True

        except ClientError as error:
            codigo = error.response["Error"]["Code"]

            if codigo == "ResourceNotFoundException":
                return False

            raise
