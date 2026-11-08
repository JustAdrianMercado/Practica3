
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1])
)

from servicios.repositorio_vinculaciones import (
    RepositorioVinculaciones
)


class TestRepositorioVinculaciones(unittest.TestCase):

    def setUp(self):
        self.tabla = MagicMock()
        self.repo = RepositorioVinculaciones(self.tabla)

    def test_obtener_usuario_vinculado(self):
        self.tabla.get_item.return_value = {
            "Item": {
                "userId": "usuario-01",
                "thingName": "caja-enigmas-01"
            }
        }

        resultado = self.repo.obtener("usuario-01")

        self.assertEqual(
            resultado["thingName"],
            "caja-enigmas-01"
        )

    def test_usuario_sin_vinculacion(self):
        self.tabla.get_item.return_value = {}

        resultado = self.repo.obtener("usuario-02")

        self.assertIsNone(resultado)

    def test_guardar_vinculacion(self):
        self.repo.guardar(
            "usuario-01",
            "caja-enigmas-01"
        )

        argumentos = self.tabla.put_item.call_args.kwargs
        item = argumentos["Item"]

        self.assertEqual(item["userId"], "usuario-01")
        self.assertEqual(
            item["thingName"],
            "caja-enigmas-01"
        )
        self.assertIn("fechaVinculacion", item)

    def test_eliminar_vinculacion(self):
        self.repo.eliminar("usuario-01")

        self.tabla.delete_item.assert_called_once_with(
            Key={"userId": "usuario-01"}
        )


if __name__ == "__main__":
    unittest.main()
