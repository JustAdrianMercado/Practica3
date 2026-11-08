"""Extensiones del servicio con payloads y clientes de boto3 simulados."""

import json
import sys
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock

from botocore.exceptions import ClientError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from servicios.servicio_shadow import ServicioShadow


class TestEstadoShadow(unittest.TestCase):
    def setUp(self):
        self.cliente = MagicMock()
        self.servicio = ServicioShadow(self.cliente)

    def preparar_lectura(self, documento):
        payload = BytesIO(json.dumps(documento).encode("utf-8"))
        self.cliente.get_thing_shadow.return_value = {"payload": payload}
        return payload

    def test_leer_desired_y_reported_en_una_sola_peticion(self):
        estado = {
            "desired": {"cerradura": "abierta"},
            "reported": {"cerradura": "cerrada", "tapa": "cerrada"},
        }
        payload = self.preparar_lectura({"state": estado, "version": 8})
        self.assertEqual(
            self.servicio.leer_estado("caja-enigmas-02"), estado
        )
        self.cliente.get_thing_shadow.assert_called_once_with(
            thingName="caja-enigmas-02"
        )
        self.assertTrue(payload.closed)

    def test_shadow_sin_state(self):
        self.preparar_lectura({})
        self.assertEqual(self.servicio.leer_estado("caja-enigmas-01"), {})

    def test_leer_reported_conserva_su_interfaz(self):
        self.preparar_lectura({"state": {
            "desired": {"cerradura": "abierta"},
            "reported": {"codigoVinculacion": "0000", "tapa": "cerrada"},
        }})
        self.assertEqual(self.servicio.leer_reported("caja-enigmas-01"), {
            "codigoVinculacion": "0000", "tapa": "cerrada",
        })

    def test_documentos_invalidos_no_devuelven_estado_inventado(self):
        for documento in ([], {"state": None},
                          {"state": {"reported": None}},
                          {"state": {"desired": "abierta"}}):
            with self.subTest(documento=documento):
                payload = self.preparar_lectura(documento)
                with self.assertRaises(ValueError):
                    self.servicio.leer_estado("caja-enigmas-01")
                self.assertTrue(payload.closed)

    def test_payload_invalido_se_cierra_y_propaga_error(self):
        payload = BytesIO(b"documento invalido")
        self.cliente.get_thing_shadow.return_value = {"payload": payload}
        with self.assertRaises(json.JSONDecodeError):
            self.servicio.leer_estado("caja-enigmas-01")
        self.assertTrue(payload.closed)

    def test_error_de_lectura_de_aws_se_propaga(self):
        error = ClientError({"Error": {
            "Code": "ResourceNotFoundException", "Message": "Sin Shadow",
        }}, "GetThingShadow")
        self.cliente.get_thing_shadow.side_effect = error
        with self.assertRaises(ClientError) as capturado:
            self.servicio.leer_estado("caja-enigmas-01")
        self.assertIs(capturado.exception, error)

    def test_payload_de_comando_solo_contiene_desired_cerradura(self):
        for estado in ("abierta", "cerrada"):
            with self.subTest(estado=estado):
                payload = BytesIO(b'{"state": {}}')
                self.cliente.update_thing_shadow.return_value = {
                    "payload": payload,
                }
                self.assertEqual(self.servicio.pedir_cerradura(
                    "caja-enigmas-02", estado
                ), {"state": {}})
                argumentos = self.cliente.update_thing_shadow.call_args.kwargs
                self.assertEqual(set(argumentos), {"thingName", "payload"})
                self.assertEqual(argumentos["thingName"], "caja-enigmas-02")
                self.assertEqual(json.loads(argumentos["payload"]), {
                    "state": {"desired": {"cerradura": estado}},
                })
                self.assertTrue(payload.closed)

    def test_error_de_escritura_de_aws_se_propaga(self):
        error = ClientError({"Error": {
            "Code": "UnauthorizedException", "Message": "Acceso denegado",
        }}, "UpdateThingShadow")
        self.cliente.update_thing_shadow.side_effect = error
        with self.assertRaises(ClientError):
            self.servicio.pedir_cerradura("caja-enigmas-01", "abierta")


if __name__ == "__main__":
    unittest.main()
