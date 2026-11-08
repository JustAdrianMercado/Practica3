
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1])
)

from manejadores.consultar_tapa import (
    ConsultarTapaIntentHandler
)


class TestConsultarTapa(unittest.TestCase):

    def setUp(self):
        self.repo = MagicMock()
        self.shadow = MagicMock()
        self.entrada = MagicMock()

        self.entrada.request_envelope.context.system.user.user_id = (
            "usuario-01"
        )

        builder = self.entrada.response_builder
        builder.speak.return_value = builder
        builder.ask.return_value = builder

        self.manejador = ConsultarTapaIntentHandler(
            self.repo,
            self.shadow
        )

    def obtener_mensaje(self):
        self.manejador.handle(self.entrada)

        return (
            self.entrada.response_builder
            .speak.call_args.args[0]
        )

    def test_tapa_abierta(self):
        self.repo.obtener.return_value = {
            "thingName": "caja-enigmas-01"
        }
        self.shadow.leer_reported.return_value = {
            "tapa": "abierta"
        }

        mensaje = self.obtener_mensaje()

        self.assertIn("abierta", mensaje)
        self.shadow.leer_reported.assert_called_once_with(
            "caja-enigmas-01"
        )

    def test_tapa_cerrada(self):
        self.repo.obtener.return_value = {
            "thingName": "caja-enigmas-01"
        }
        self.shadow.leer_reported.return_value = {
            "tapa": "cerrada"
        }

        mensaje = self.obtener_mensaje()

        self.assertIn("cerrada", mensaje)

    def test_usuario_sin_vinculacion(self):
        self.repo.obtener.return_value = None

        mensaje = self.obtener_mensaje()

        self.assertIn("Primero debes vincular", mensaje)
        self.shadow.leer_reported.assert_not_called()

    def test_estado_desconocido(self):
        self.repo.obtener.return_value = {
            "thingName": "caja-enigmas-01"
        }
        self.shadow.leer_reported.return_value = {}

        mensaje = self.obtener_mensaje()

        self.assertIn("No tengo información", mensaje)


if __name__ == "__main__":
    unittest.main()
