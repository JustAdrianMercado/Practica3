
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1])
)

from manejadores.lanzamiento import LaunchRequestHandler


class TestLaunchRequestHandler(unittest.TestCase):

    def setUp(self):
        self.repositorio = MagicMock()
        self.manejador = LaunchRequestHandler(
            self.repositorio
        )

        self.handler_input = MagicMock()
        self.handler_input.request_envelope.context.system.user.user_id = (
            "usuario-01"
        )

        builder = self.handler_input.response_builder
        builder.speak.return_value = builder
        builder.ask.return_value = builder

    def test_usuario_vinculado(self):
        self.repositorio.obtener.return_value = {
            "thingName": "caja-enigmas-01"
        }

        self.manejador.handle(self.handler_input)

        self.repositorio.obtener.assert_called_once_with(
            "usuario-01"
        )

        mensaje = (
            self.handler_input.response_builder
            .speak.call_args.args[0]
        )

        self.assertIn("caja-enigmas-01", mensaje)

    def test_usuario_sin_vinculacion(self):
        self.repositorio.obtener.return_value = None

        self.manejador.handle(self.handler_input)

        mensaje = (
            self.handler_input.response_builder
            .speak.call_args.args[0]
        )

        self.assertIn("no tienes una caja vinculada", mensaje)


if __name__ == "__main__":
    unittest.main()
