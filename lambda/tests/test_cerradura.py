"""Pruebas de consultas y comandos mediante el dispatcher real del SDK."""

import unittest
from unittest.mock import MagicMock, call

from botocore.exceptions import ClientError

from apoyo import crear_lambda, evento_alexa, voz
from servicios.repositorio_vinculaciones import RepositorioVinculaciones
from servicios.servicio_registro import ServicioRegistro
from servicios.servicio_shadow import ServicioShadow


class TestCerradura(unittest.TestCase):
    def setUp(self):
        self.repo = MagicMock(spec=RepositorioVinculaciones)
        self.registro = MagicMock(spec=ServicioRegistro)
        self.shadow = MagicMock(spec=ServicioShadow)
        self.repo.obtener.return_value = {"thingName": "caja-enigmas-01"}
        self.shadow.leer_estado.return_value = {
            "reported": {"cerradura": "cerrada"},
        }
        self.invocar = crear_lambda(self.repo, self.registro, self.shadow)

    def solicitar(self, intent, usuario="usuario-01"):
        return self.invocar(evento_alexa(intent, usuario), None)

    def test_consultar_ambos_estados_reportados(self):
        for estado in ("abierta", "cerrada"):
            with self.subTest(estado=estado):
                self.shadow.leer_estado.return_value = {
                    "reported": {"cerradura": estado},
                    "desired": {"cerradura": estado},
                }
                respuesta = self.solicitar("ConsultarCerraduraIntent")
                self.assertIn(f"está {estado}", voz(respuesta))
                self.assertNotIn("todavía no confirmó", voz(respuesta))
                self.assertFalse(respuesta["response"]["shouldEndSession"])
        self.shadow.pedir_cerradura.assert_not_called()

    def test_detectar_apertura_y_cierre_pendientes(self):
        casos = (
            ("cerrada", "abierta", "apertura"),
            ("abierta", "cerrada", "cierre"),
        )
        for reportado, deseado, accion in casos:
            with self.subTest(deseado=deseado):
                self.shadow.leer_estado.reset_mock()
                self.shadow.leer_estado.return_value = {
                    "reported": {"cerradura": reportado},
                    "desired": {"cerradura": deseado},
                }
                mensaje = voz(self.solicitar("ConsultarCerraduraIntent"))
                self.assertIn(f"está {reportado}", mensaje)
                self.assertIn(f"no confirmó la orden de {accion}", mensaje)
                self.shadow.leer_estado.assert_called_once_with(
                    "caja-enigmas-01"
                )
        self.shadow.leer_reported.assert_not_called()

    def test_reported_sin_desired_no_es_orden_pendiente(self):
        mensaje = voz(self.solicitar("ConsultarCerraduraIntent"))
        self.assertIn("está cerrada", mensaje)
        self.assertNotIn("no confirmó", mensaje)

    def test_desired_sin_reported_no_confirma_estado_fisico(self):
        self.shadow.leer_estado.return_value = {
            "desired": {"cerradura": "abierta"},
        }
        mensaje = voz(self.solicitar("ConsultarCerraduraIntent"))
        self.assertIn("No tengo información reportada", mensaje)
        self.assertIn("no confirmó la orden de apertura", mensaje)
        self.assertNotIn("está abierta", mensaje)

    def test_shadow_sin_informacion_de_cerradura(self):
        self.shadow.leer_estado.return_value = {}
        mensaje = voz(self.solicitar("ConsultarCerraduraIntent"))
        self.assertIn("No tengo información reportada", mensaje)
        self.assertNotIn("no confirmó", mensaje)

    def test_no_reproducir_valores_fuera_del_contrato(self):
        self.shadow.leer_estado.return_value = {
            "reported": {"cerradura": "<break/>dato-ajeno"},
            "desired": {"cerradura": "invalida"},
        }
        mensaje = voz(self.solicitar("ConsultarCerraduraIntent"))
        self.assertIn("No tengo información reportada", mensaje)
        self.assertNotIn("dato-ajeno", mensaje)
        self.assertNotIn("invalida", mensaje)

    def test_intents_sin_vinculacion_no_acceden_al_shadow(self):
        self.repo.obtener.return_value = None
        for intent in ("ConsultarCerraduraIntent", "AbrirCerraduraIntent",
                       "CerrarCerraduraIntent"):
            with self.subTest(intent=intent):
                mensaje = voz(self.solicitar(intent))
                self.assertIn("no tienes una caja vinculada", mensaje)
                self.assertIn("vincula mi caja", mensaje)
        self.shadow.leer_estado.assert_not_called()
        self.shadow.pedir_cerradura.assert_not_called()

    def test_intents_sin_usuario_no_acceden_a_dynamodb(self):
        for intent in ("ConsultarCerraduraIntent", "AbrirCerraduraIntent",
                       "CerrarCerraduraIntent"):
            with self.subTest(intent=intent):
                mensaje = voz(self.solicitar(intent, usuario=None))
                self.assertIn("No pude identificar", mensaje)
        self.repo.obtener.assert_not_called()
        self.shadow.leer_estado.assert_not_called()
        self.shadow.pedir_cerradura.assert_not_called()

    def test_abrir_y_cerrar_solo_envian_orden(self):
        for intent, estado, verbo in (
            ("AbrirCerraduraIntent", "abierta", "abrir"),
            ("CerrarCerraduraIntent", "cerrada", "cerrar"),
        ):
            with self.subTest(intent=intent):
                self.shadow.pedir_cerradura.reset_mock()
                mensaje = voz(self.solicitar(intent))
                self.shadow.pedir_cerradura.assert_called_once_with(
                    "caja-enigmas-01", estado
                )
                self.assertIn(f"Envié la orden para {verbo}", mensaje)
                self.assertIn("comprobar si la caja la confirmó", mensaje)
                self.assertNotIn(f"está {estado}", mensaje)
        self.shadow.leer_estado.assert_not_called()
        self.shadow.leer_reported.assert_not_called()

    def test_dos_usuarios_resuelven_su_propia_caja_en_cada_peticion(self):
        self.repo.obtener.side_effect = lambda usuario: {
            "thingName": {
                "usuario-01": "caja-enigmas-01",
                "usuario-02": "caja-enigmas-02",
            }[usuario],
        }
        for usuario in ("usuario-01", "usuario-02"):
            self.solicitar("ConsultarCerraduraIntent", usuario)
            self.solicitar("AbrirCerraduraIntent", usuario)
            self.solicitar("CerrarCerraduraIntent", usuario)
        self.shadow.leer_estado.assert_has_calls([
            call("caja-enigmas-01"), call("caja-enigmas-02"),
        ])
        self.assertEqual(self.shadow.pedir_cerradura.call_args_list, [
            call("caja-enigmas-01", "abierta"),
            call("caja-enigmas-01", "cerrada"),
            call("caja-enigmas-02", "abierta"),
            call("caja-enigmas-02", "cerrada"),
        ])
        self.assertEqual(self.repo.obtener.call_args_list, [
            call("usuario-01"), call("usuario-01"), call("usuario-01"),
            call("usuario-02"), call("usuario-02"), call("usuario-02"),
        ])

    def test_error_de_aws_no_anuncia_orden_enviada_ni_estado(self):
        error = ClientError({"Error": {
            "Code": "UnauthorizedException", "Message": "Fallo simulado",
        }}, "UpdateThingShadow")
        self.shadow.pedir_cerradura.side_effect = error
        self.shadow.leer_estado.side_effect = error
        for intent in ("AbrirCerraduraIntent", "CerrarCerraduraIntent",
                       "ConsultarCerraduraIntent"):
            with self.subTest(intent=intent):
                with self.assertLogs("manejadores.errores", level="ERROR"):
                    mensaje = voz(self.solicitar(intent))
                self.assertIn("No pude completar", mensaje)
                self.assertNotIn("Envié", mensaje)
                self.assertNotIn("está cerrada", mensaje)


if __name__ == "__main__":
    unittest.main()
