
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1])
)

from manejadores.vincular_caja import (
    VincularCajaIntentHandler
)


class TestVincularCaja(unittest.TestCase):

    def setUp(self):
        self.repo = MagicMock()
        self.registro = MagicMock()
        self.shadow = MagicMock()
        self.entrada = MagicMock()

        self.entrada.request_envelope.context.system.user.user_id = (
            "usuario-01"
        )

        builder = self.entrada.response_builder
        builder.speak.return_value = builder
        builder.ask.return_value = builder

        self.manejador = VincularCajaIntentHandler(
            self.repo,
            self.registro,
            self.shadow,
            "caja-enigmas-"
        )

        self.registro.existe_thing.return_value = True
        self.shadow.leer_reported.return_value = {
            "codigoVinculacion": "0000"
        }

    def ejecutar(self, numero="1", codigo="0000"):
        def slot_simulado(handler_input, nombre):
            valor = numero if nombre == "numeroCaja" else codigo
            if valor is None:
                return None
            return MagicMock(value=valor)

        with patch(
            "manejadores.vincular_caja.get_slot",
            side_effect=slot_simulado
        ):
            self.manejador.handle(self.entrada)

        return (
            self.entrada.response_builder
            .speak.call_args.args[0]
        )

    def test_vinculacion_correcta(self):
        mensaje = self.ejecutar()

        self.registro.existe_thing.assert_called_once_with(
            "caja-enigmas-01"
        )
        self.repo.guardar.assert_called_once_with(
            "usuario-01", "caja-enigmas-01"
        )
        self.assertIn("correctamente", mensaje)

    def test_codigo_incorrecto(self):
        mensaje = self.ejecutar(codigo="9999")

        self.assertIn("incorrecto", mensaje)
        self.repo.guardar.assert_not_called()

    def test_thing_inexistente(self):
        self.registro.existe_thing.return_value = False

        mensaje = self.ejecutar()

        self.assertIn("no existe", mensaje)
        self.repo.guardar.assert_not_called()

    def test_faltan_datos(self):
        mensaje = self.ejecutar(numero=None)

        self.assertIn("Necesito", mensaje)
        self.repo.guardar.assert_not_called()

    def test_numero_invalido(self):
        mensaje = self.ejecutar(numero="abc")

        self.assertIn("no es válido", mensaje)
        self.repo.guardar.assert_not_called()

    def test_codigo_con_formato_invalido(self):
        mensaje = self.ejecutar(codigo="123")

        self.assertIn("cuatro dígitos", mensaje)
        self.repo.guardar.assert_not_called()


if __name__ == "__main__":
    unittest.main()
