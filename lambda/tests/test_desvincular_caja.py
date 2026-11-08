
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1])
)

from manejadores.desvincular_caja import (
    DesvincularCajaIntentHandler
)


class TestDesvincularCaja(unittest.TestCase):

    def setUp(self):
        self.repositorio = MagicMock()

        self.manejador = DesvincularCajaIntentHandler(
            self.repositorio
        )

        self.entrada = MagicMock()
        self.entrada.request_envelope.context.system.user.user_id = (
            "usuario-01"
        )

        builder = self.entrada.response_builder
        builder.speak.return_value = builder
        builder.ask.return_value = builder

    def obtener_mensaje(self):
        self.manejador.handle(self.entrada)

        return (
            self.entrada.response_builder
            .speak.call_args.args[0]
        )

    def test_desvincular_usuario(self):
        self.repositorio.obtener.return_value = {
            "thingName": "caja-enigmas-01"
        }

        mensaje = self.obtener_mensaje()

        self.repositorio.eliminar.assert_called_once_with(
            "usuario-01"
        )

        self.assertIn("correctamente", mensaje)

    def test_usuario_sin_vinculacion(self):
        self.repositorio.obtener.return_value = None

        mensaje = self.obtener_mensaje()

        self.repositorio.eliminar.assert_not_called()

        self.assertIn(
            "no tienes ninguna caja vinculada",
            mensaje
        )

    def test_usuario_sin_identificador(self):
        self.entrada.request_envelope.context.system.user.user_id = (
            None
        )

        mensaje = self.obtener_mensaje()

        self.repositorio.obtener.assert_not_called()
        self.repositorio.eliminar.assert_not_called()

        self.assertIn("No pude identificar", mensaje)


if __name__ == "__main__":
    unittest.main()
