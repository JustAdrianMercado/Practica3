
import sys
import json
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1])
)

from servicios.servicio_shadow import ServicioShadow


class TestServicioShadow(unittest.TestCase):

    def setUp(self):
        self.cliente = MagicMock()
        self.servicio = ServicioShadow(self.cliente)

    def test_leer_reported(self):
        documento = {
            "state": {
                "reported": {
                    "tapa": "cerrada",
                    "cerradura": "cerrada"
                }
            }
        }

        self.cliente.get_thing_shadow.return_value = {
            "payload": BytesIO(
                json.dumps(documento).encode()
            )
        }

        resultado = self.servicio.leer_reported(
            "caja-enigmas-01"
        )

        self.assertEqual(resultado["tapa"], "cerrada")
        self.assertEqual(resultado["cerradura"], "cerrada")

    def test_shadow_sin_reported(self):
        self.cliente.get_thing_shadow.return_value = {
            "payload": BytesIO(b'{"state": {}}')
        }

        resultado = self.servicio.leer_reported(
            "caja-enigmas-01"
        )

        self.assertEqual(resultado, {})

    def test_abrir_cerradura(self):
        self.cliente.update_thing_shadow.return_value = {
            "payload": BytesIO(b'{"state": {}}')
        }

        self.servicio.pedir_cerradura(
            "caja-enigmas-01", "abierta"
        )

        argumentos = (
            self.cliente.update_thing_shadow.call_args.kwargs
        )

        documento = json.loads(argumentos["payload"])

        self.assertEqual(
            documento["state"]["desired"]["cerradura"],
            "abierta"
        )

    def test_cerrar_cerradura(self):
        self.cliente.update_thing_shadow.return_value = {
            "payload": BytesIO(b'{"state": {}}')
        }

        self.servicio.pedir_cerradura(
            "caja-enigmas-01", "cerrada"
        )

        argumentos = (
            self.cliente.update_thing_shadow.call_args.kwargs
        )

        documento = json.loads(argumentos["payload"])

        self.assertEqual(
            documento["state"]["desired"]["cerradura"],
            "cerrada"
        )

    def test_estado_invalido(self):
        with self.assertRaises(ValueError):
            self.servicio.pedir_cerradura(
                "caja-enigmas-01", "rota"
            )

        self.cliente.update_thing_shadow.assert_not_called()


if __name__ == "__main__":
    unittest.main()
