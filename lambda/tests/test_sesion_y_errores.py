"""Respuestas del SDK, fin de sesión y ausencia de datos privados en logs."""

import unittest
from unittest.mock import MagicMock

from botocore.exceptions import ClientError

from apoyo import crear_lambda, evento_alexa, voz
from manejadores.errores import GlobalExceptionHandler
from servicios.repositorio_vinculaciones import RepositorioVinculaciones
from servicios.servicio_registro import ServicioRegistro
from servicios.servicio_shadow import ServicioShadow


class TestSesionYErrores(unittest.TestCase):
    def setUp(self):
        self.repo = MagicMock(spec=RepositorioVinculaciones)
        self.registro = MagicMock(spec=ServicioRegistro)
        self.shadow = MagicMock(spec=ServicioShadow)
        self.repo.obtener.return_value = None
        self.invocar = crear_lambda(self.repo, self.registro, self.shadow)

    def solicitar(self, intent):
        return self.invocar(evento_alexa(intent), None)

    def test_help_explica_vinculacion_consultas_y_control(self):
        respuesta = self.solicitar("AMAZON.HelpIntent")
        for palabra in ("vincular", "cuatro dígitos", "tapa", "cerradura",
                        "abrir", "cerrar", "desvincular", "cambiar"):
            self.assertIn(palabra, voz(respuesta))
        self.assertFalse(respuesta["response"]["shouldEndSession"])
        self.repo.obtener.assert_not_called()
        self.shadow.pedir_cerradura.assert_not_called()

    def test_cancel_y_stop_finalizan_sin_modificar_la_caja(self):
        for intent in ("AMAZON.CancelIntent", "AMAZON.StopIntent"):
            with self.subTest(intent=intent):
                respuesta = self.solicitar(intent)
                self.assertIn("Hasta luego", voz(respuesta))
                self.assertTrue(respuesta["response"]["shouldEndSession"])
                self.assertNotIn("reprompt", respuesta["response"])
        self.repo.obtener.assert_not_called()
        self.repo.eliminar.assert_not_called()
        self.shadow.pedir_cerradura.assert_not_called()

    def test_fallback_ofrece_ayuda_y_mantiene_la_sesion(self):
        respuesta = self.solicitar("AMAZON.FallbackIntent")
        self.assertIn("No entendí", voz(respuesta))
        self.assertIn("vincular", voz(respuesta))
        self.assertFalse(respuesta["response"]["shouldEndSession"])
        self.assertIn("reprompt", respuesta["response"])
        self.repo.obtener.assert_not_called()

    def test_navigate_home_finaliza_si_se_recibe_directamente(self):
        respuesta = self.solicitar("AMAZON.NavigateHomeIntent")
        self.assertIn("Hasta luego", voz(respuesta))
        self.assertTrue(respuesta["response"]["shouldEndSession"])
        self.repo.obtener.assert_not_called()

    def test_session_ended_no_devuelve_voz_tarjeta_ni_directivas(self):
        respuesta = self.invocar(evento_alexa(
            tipo="SessionEndedRequest"
        ), None)
        self.assertEqual(respuesta["response"], {})
        self.repo.obtener.assert_not_called()
        self.shadow.pedir_cerradura.assert_not_called()

    def test_launch_se_despacha_por_tipo_de_solicitud(self):
        respuesta = self.invocar(evento_alexa(tipo="LaunchRequest"), None)
        self.assertIn("Bienvenido", voz(respuesta))
        self.repo.obtener.assert_called_once_with("usuario-01")

    def test_error_inesperado_no_expone_mensaje_ni_evento(self):
        self.repo.obtener.side_effect = RuntimeError(
            "SECRETO_FICTICIO_EN_EXCEPCION"
        )
        evento = evento_alexa(tipo="LaunchRequest", usuario="USUARIO_PRIVADO")
        with self.assertLogs("manejadores.errores", level="ERROR") as logs:
            respuesta = self.invocar(evento, None)
        self.assertIn("No pude completar", voz(respuesta))
        self.assertIn("categoria=ErrorInterno", " ".join(logs.output))
        for marcador in ("SECRETO_FICTICIO", "USUARIO_PRIVADO",
                         "TOKEN_FICTICIO", "Traceback"):
            self.assertNotIn(marcador, str(respuesta) + str(logs.output))
        self.assertFalse(respuesta["response"]["shouldEndSession"])

    def test_error_aws_registra_solo_codigo_y_operacion_permitidos(self):
        self.repo.obtener.side_effect = ClientError({
            "Error": {
                "Code": "AccessDeniedException",
                "Message": "CREDENCIAL_FICTICIA código 0000 usuario privado",
            },
            "ResponseMetadata": {
                "RequestId": "ID_PRIVADO",
                "HTTPHeaders": {"authorization": "TOKEN_PRIVADO"},
            },
        }, "GetItem")
        with self.assertLogs("manejadores.errores", level="ERROR") as logs:
            respuesta = self.invocar(evento_alexa(tipo="LaunchRequest"), None)
        salida = " ".join(logs.output)
        self.assertIn("categoria=AccessDeniedException", salida)
        self.assertIn("operacion=GetItem", salida)
        for marcador in ("CREDENCIAL_FICTICIA", "0000", "ID_PRIVADO",
                         "TOKEN_PRIVADO", "TOKEN_FICTICIO", "usuario-01"):
            self.assertNotIn(marcador, salida + voz(respuesta))

    def test_codigos_y_operaciones_aws_desconocidos_no_se_registran(self):
        self.repo.obtener.side_effect = ClientError({"Error": {
            "Code": "CODIGO_PRIVADO", "Message": "MENSAJE_PRIVADO",
        }}, "OPERACION_PRIVADA")
        with self.assertLogs("manejadores.errores", level="ERROR") as logs:
            respuesta = self.invocar(evento_alexa(tipo="LaunchRequest"), None)
        salida = " ".join(logs.output)
        self.assertIn("categoria=ErrorAWS", salida)
        self.assertIn("operacion=NoIdentificada", salida)
        self.assertNotIn("PRIVAD", salida + voz(respuesta))

    def test_intent_desconocido_llega_al_manejador_global(self):
        with self.assertLogs("manejadores.errores", level="ERROR"):
            respuesta = self.solicitar("IntentAjenoAlModelo")
        self.assertIn("No pude completar", voz(respuesta))
        self.repo.obtener.assert_not_called()
        self.shadow.pedir_cerradura.assert_not_called()

    def test_manejador_global_acepta_excepciones(self):
        manejador = GlobalExceptionHandler(logger=MagicMock())
        self.assertTrue(manejador.can_handle(None, ValueError()))

    def test_error_al_finalizar_sesion_no_genera_voz(self):
        logger = MagicMock()
        entrada = MagicMock()
        entrada.request_envelope.request.object_type = "SessionEndedRequest"
        respuesta = GlobalExceptionHandler(logger).handle(
            entrada, RuntimeError("DETALLE_PRIVADO")
        )
        self.assertIs(respuesta, entrada.response_builder.response)
        entrada.response_builder.speak.assert_not_called()
        entrada.response_builder.ask.assert_not_called()
        logger.error.assert_called_once_with(
            "Solicitud fallida: categoria=%s operacion=%s",
            "ErrorInterno", "NoIdentificada",
        )


if __name__ == "__main__":
    unittest.main()
