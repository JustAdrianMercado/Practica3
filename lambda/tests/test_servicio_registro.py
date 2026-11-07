
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from botocore.exceptions import ClientError

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1])
)

from servicios.servicio_registro import ServicioRegistro


class TestServicioRegistro(unittest.TestCase):

    def setUp(self):
        self.cliente = MagicMock()
        self.servicio = ServicioRegistro(self.cliente)

    def test_thing_existente(self):
        self.cliente.describe_thing.return_value = {
            "thingName": "caja-enigmas-01"
        }

        resultado = self.servicio.existe_thing(
            "caja-enigmas-01"
        )

        self.assertTrue(resultado)

        self.cliente.describe_thing.assert_called_once_with(
            thingName="caja-enigmas-01"
        )

    def test_thing_inexistente(self):
        self.cliente.describe_thing.side_effect = ClientError(
            {
                "Error": {
                    "Code": "ResourceNotFoundException",
                    "Message": "Thing no encontrado"
                }
            },
            "DescribeThing"
        )

        resultado = self.servicio.existe_thing(
            "caja-enigmas-99"
        )

        self.assertFalse(resultado)

    def test_error_permisos(self):
        self.cliente.describe_thing.side_effect = ClientError(
            {
                "Error": {
                    "Code": "AccessDeniedException",
                    "Message": "Acceso denegado"
                }
            },
            "DescribeThing"
        )

        with self.assertRaises(ClientError):
            self.servicio.existe_thing(
                "caja-enigmas-01"
            )


if __name__ == "__main__":
    unittest.main()
