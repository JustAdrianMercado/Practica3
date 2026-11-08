"""Regresiones de contratos, identidad, SSML y errores de red."""

import unittest
from unittest.mock import MagicMock
from xml.etree import ElementTree

from botocore.exceptions import EndpointConnectionError, ReadTimeoutError

from apoyo import crear_lambda, evento_alexa, voz
from servicios.repositorio_vinculaciones import RepositorioVinculaciones
from servicios.servicio_registro import ServicioRegistro
from servicios.servicio_shadow import ServicioShadow


class TestAuditoria(unittest.TestCase):
    def setUp(self):
        self.repo = MagicMock(spec=RepositorioVinculaciones)
        self.registro = MagicMock(spec=ServicioRegistro)
        self.shadow = MagicMock(spec=ServicioShadow)
        self.repo.obtener.return_value = None
        self.registro.existe_thing.return_value = True
        self.shadow.leer_reported.return_value = {
            "codigoVinculacion": "4821",
        }
        self.invocar = crear_lambda(self.repo, self.registro, self.shadow)

    def solicitudes_de_caja(self):
        yield evento_alexa(tipo="LaunchRequest")
        for intent in ("VincularCajaIntent", "DesvincularCajaIntent",
                       "ConsultarTapaIntent", "ConsultarCerraduraIntent",
                       "AbrirCerraduraIntent", "CerrarCerraduraIntent"):
            yield evento_alexa(intent, slots={
                "numeroCaja": "1", "codigo": "4821",
            })

    def comprobar_identidad_ausente(self, evento):
        respuesta = self.invocar(evento, None)
        self.assertIn("No pude identificar", voz(respuesta))
        self.repo.obtener.assert_not_called()
        self.repo.guardar.assert_not_called()
        self.repo.eliminar.assert_not_called()
        self.registro.existe_thing.assert_not_called()
        self.shadow.leer_reported.assert_not_called()
        self.shadow.leer_estado.assert_not_called()
        self.shadow.pedir_cerradura.assert_not_called()

    def test_sin_contexto_no_usa_usuario_de_sesion(self):
        for evento in self.solicitudes_de_caja():
            with self.subTest(solicitud=evento["request"]):
                evento.pop("context")
                self.comprobar_identidad_ausente(evento)

    def test_contexto_sin_system_o_user_no_llama_a_aws(self):
        for campo in ("System", "user"):
            for evento in self.solicitudes_de_caja():
                with self.subTest(campo=campo, solicitud=evento["request"]):
                    if campo == "System":
                        evento["context"].pop("System")
                    else:
                        evento["context"]["System"].pop("user")
                    self.comprobar_identidad_ausente(evento)

    def test_usuario_vacio_no_llama_a_aws(self):
        for usuario in (None, "", "   "):
            for evento in self.solicitudes_de_caja():
                with self.subTest(usuario=usuario,
                                  solicitud=evento["request"]):
                    evento["context"]["System"]["user"]["userId"] = usuario
                    self.comprobar_identidad_ausente(evento)

    def test_bienvenida_escapa_nombre_leido_de_dynamodb(self):
        self.repo.obtener.return_value = {
            "thingName": "caja-enigmas-01 & <dato>ajeno</dato>",
        }
        respuesta = self.invocar(evento_alexa(tipo="LaunchRequest"), None)
        ssml = voz(respuesta)
        raiz = ElementTree.fromstring(ssml)
        self.assertIsNone(raiz.find("dato"))
        self.assertIn("&amp;", ssml)
        self.assertIn("&lt;dato&gt;", ssml)

    def test_codigo_del_shadow_debe_ser_string(self):
        self.shadow.leer_reported.return_value = {
            "codigoVinculacion": 4821,
        }
        respuesta = self.invocar(evento_alexa("VincularCajaIntent", slots={
            "numeroCaja": "1", "codigo": "4821",
        }), None)
        self.assertIn("incorrecto", voz(respuesta))
        self.repo.guardar.assert_not_called()

    def test_codigo_invalido_no_consulta_aws(self):
        for codigo in ("123", "１２３４", "12a4", "    "):
            with self.subTest(codigo=codigo):
                respuesta = self.invocar(evento_alexa(
                    "VincularCajaIntent", slots={
                        "numeroCaja": "1", "codigo": codigo,
                    }
                ), None)
                self.assertIn("cuatro dígitos", voz(respuesta))
                self.registro.existe_thing.assert_not_called()
                self.shadow.leer_reported.assert_not_called()
                self.repo.guardar.assert_not_called()

    def test_codigo_valido_con_ceros_iniciales_sigue_funcionando(self):
        self.shadow.leer_reported.return_value = {
            "codigoVinculacion": "0421",
        }
        respuesta = self.invocar(evento_alexa("VincularCajaIntent", slots={
            "numeroCaja": "2", "codigo": " 0421 ",
        }), None)
        self.assertIn("correctamente", voz(respuesta))
        self.repo.guardar.assert_called_once_with(
            "usuario-01", "caja-enigmas-02"
        )

    def test_desvincular_sin_caja_incluye_ayuda(self):
        respuesta = self.invocar(evento_alexa("DesvincularCajaIntent"), None)
        self.assertIn("no tienes ninguna caja vinculada", voz(respuesta))
        self.assertIn("vincula mi caja", voz(respuesta))
        self.repo.eliminar.assert_not_called()

    def test_error_de_red_no_se_expone_en_voz_o_logs(self):
        self.repo.obtener.return_value = {"thingName": "caja-enigmas-01"}
        for error in (
            EndpointConnectionError(endpoint_url="https://privado.example"),
            ReadTimeoutError(endpoint_url="https://privado.example"),
        ):
            with self.subTest(error=type(error).__name__):
                self.shadow.leer_reported.side_effect = error
                with self.assertLogs(
                    "manejadores.errores", level="ERROR"
                ) as logs:
                    respuesta = self.invocar(
                        evento_alexa("ConsultarTapaIntent"), None
                    )
                self.assertIn("No pude completar", voz(respuesta))
                self.assertNotIn("privado.example", voz(respuesta))
                self.assertNotIn("privado.example", str(logs.output))
                self.shadow.pedir_cerradura.assert_not_called()


if __name__ == "__main__":
    unittest.main()
