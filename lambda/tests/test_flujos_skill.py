"""Flujos con servicios reales y boto3 simulado, sin Alexa ni hardware real."""

import json
import unittest
from datetime import datetime
from io import BytesIO
from unittest.mock import MagicMock

from botocore.exceptions import ClientError

from apoyo import crear_lambda, evento_alexa, voz
from servicios.repositorio_vinculaciones import RepositorioVinculaciones
from servicios.servicio_registro import ServicioRegistro
from servicios.servicio_shadow import ServicioShadow


class TestFlujosSkill(unittest.TestCase):
    def setUp(self):
        self.items = {}
        self.estados = {
            "caja-enigmas-01": {"reported": {
                "tapa": "cerrada", "cerradura": "cerrada",
                "codigoVinculacion": "0000",
            }},
            "caja-enigmas-02": {"reported": {
                "tapa": "abierta", "cerradura": "abierta",
                "codigoVinculacion": "0421",
            }},
        }
        self.tabla = MagicMock()
        self.tabla.get_item.side_effect = self.obtener_item
        self.tabla.put_item.side_effect = self.guardar_item
        self.tabla.delete_item.side_effect = self.eliminar_item
        self.iot = MagicMock()
        self.iot.get_thing_shadow.side_effect = self.leer_shadow
        self.iot.update_thing_shadow.side_effect = self.escribir_shadow
        self.registro = MagicMock()
        self.registro.describe_thing.side_effect = self.describir_thing
        self.invocar = crear_lambda(
            RepositorioVinculaciones(self.tabla),
            ServicioRegistro(self.registro),
            ServicioShadow(self.iot),
        )

    def obtener_item(self, Key, ConsistentRead):
        self.assertTrue(ConsistentRead)
        item = self.items.get(Key["userId"])
        return {"Item": item.copy()} if item else {}

    def guardar_item(self, Item):
        self.items[Item["userId"]] = Item.copy()
        return {}

    def eliminar_item(self, Key):
        self.items.pop(Key["userId"], None)
        return {}

    def describir_thing(self, thingName):
        if thingName not in self.estados:
            raise ClientError({"Error": {
                "Code": "ResourceNotFoundException",
                "Message": "Thing inexistente de prueba",
            }}, "DescribeThing")
        return {"thingName": thingName}

    def leer_shadow(self, thingName):
        return {"payload": BytesIO(json.dumps({
            "state": self.estados[thingName],
        }).encode("utf-8"))}

    def escribir_shadow(self, thingName, payload):
        documento = json.loads(payload)
        self.assertEqual(set(documento["state"]), {"desired"})
        self.estados[thingName]["desired"] = documento["state"]["desired"]
        # No se simula el servo: reported conserva su estado anterior.
        return self.leer_shadow(thingName)

    def solicitar(self, intent, usuario="usuario-01", slots=None):
        return self.invocar(evento_alexa(intent, usuario, slots), None)

    def vincular(self, usuario="usuario-01", numero="1", codigo="0000"):
        return self.solicitar("VincularCajaIntent", usuario, {
            "numeroCaja": numero, "codigo": codigo,
        })

    def test_dos_usuarios_vinculan_consultan_y_controlan_sus_cajas(self):
        self.assertIn("correctamente", voz(self.vincular()))
        self.assertIn("correctamente", voz(self.vincular(
            "usuario-02", "2", "0421"
        )))
        self.assertIn("cerrada", voz(self.solicitar("ConsultarTapaIntent")))
        self.assertIn("abierta", voz(self.solicitar(
            "ConsultarTapaIntent", "usuario-02"
        )))
        self.solicitar("AbrirCerraduraIntent")
        self.solicitar("CerrarCerraduraIntent", "usuario-02")
        argumentos = self.iot.update_thing_shadow.call_args_list
        self.assertEqual(
            [llamada.kwargs["thingName"] for llamada in argumentos],
            ["caja-enigmas-01", "caja-enigmas-02"],
        )
        self.assertIn("no confirmó la orden de apertura", voz(
            self.solicitar("ConsultarCerraduraIntent")
        ))
        self.assertIn("no confirmó la orden de cierre", voz(
            self.solicitar("ConsultarCerraduraIntent", "usuario-02")
        ))
        self.assertEqual(self.items["usuario-01"]["thingName"],
                         "caja-enigmas-01")
        self.assertEqual(self.items["usuario-02"]["thingName"],
                         "caja-enigmas-02")
        self.assertNotIn("usuario-de-sesion", self.items)

    def test_cambiar_vinculacion_reemplaza_la_caja_del_usuario(self):
        self.vincular()
        self.vincular(numero="2", codigo="0421")
        self.solicitar("AbrirCerraduraIntent")
        self.assertEqual(len(self.items), 1)
        item = self.items["usuario-01"]
        self.assertEqual(item["thingName"], "caja-enigmas-02")
        fecha = datetime.fromisoformat(item["fechaVinculacion"])
        self.assertEqual(fecha.utcoffset().total_seconds(), 0)
        self.assertEqual(
            self.iot.update_thing_shadow.call_args.kwargs["thingName"],
            "caja-enigmas-02",
        )

    def test_desvincular_no_afecta_al_otro_usuario(self):
        self.vincular()
        self.vincular("usuario-02", "2", "0421")
        respuesta = self.solicitar("DesvincularCajaIntent")
        self.assertIn("desvinculada correctamente", voz(respuesta))
        self.assertNotIn("usuario-01", self.items)
        self.assertIn("usuario-02", self.items)
        self.assertIn("no tienes una caja vinculada", voz(
            self.solicitar("AbrirCerraduraIntent")
        ))
        self.iot.update_thing_shadow.assert_not_called()
        self.tabla.delete_item.assert_called_once_with(
            Key={"userId": "usuario-01"}
        )

    def test_codigo_incorrecto_conserva_la_vinculacion_anterior(self):
        self.vincular()
        anterior = self.items["usuario-01"].copy()
        self.tabla.put_item.reset_mock()
        mensaje = voz(self.vincular(numero="2", codigo="9999"))
        self.assertIn("incorrecto", mensaje)
        self.assertEqual(self.items["usuario-01"], anterior)
        self.tabla.put_item.assert_not_called()

    def test_thing_inexistente_no_lee_shadow_ni_guarda(self):
        mensaje = voz(self.vincular(numero="99"))
        self.assertIn("no existe", mensaje)
        self.registro.describe_thing.assert_called_once_with(
            thingName="caja-enigmas-99"
        )
        self.iot.get_thing_shadow.assert_not_called()
        self.tabla.put_item.assert_not_called()

    def test_slots_incompletos_y_numero_fuera_de_rango_no_guardan(self):
        for slots, esperado in (
            ({"numeroCaja": "1"}, "Necesito"),
            ({"numeroCaja": "0", "codigo": "0000"}, "entre 1 y 99"),
            ({"numeroCaja": "100", "codigo": "0000"}, "entre 1 y 99"),
        ):
            with self.subTest(slots=slots):
                respuesta = self.solicitar("VincularCajaIntent", slots=slots)
                mensaje = voz(respuesta)
                self.assertIn(esperado, mensaje)
        self.registro.describe_thing.assert_not_called()
        self.tabla.put_item.assert_not_called()

    def test_caja_sin_codigo_reportado_no_permite_vincular(self):
        self.estados["caja-enigmas-01"] = {"reported": {}}
        self.assertIn("incorrecto", voz(self.vincular()))
        self.tabla.put_item.assert_not_called()

    def test_errores_del_registro_y_shadow_no_persisten_vinculacion(self):
        for cliente, metodo, operacion in (
            (self.registro, "describe_thing", "DescribeThing"),
            (self.iot, "get_thing_shadow", "GetThingShadow"),
        ):
            with self.subTest(operacion=operacion):
                original = getattr(cliente, metodo).side_effect
                getattr(cliente, metodo).side_effect = ClientError({"Error": {
                    "Code": "AccessDeniedException",
                    "Message": "Permiso denegado de prueba",
                }}, operacion)
                with self.assertLogs("manejadores.errores", level="ERROR"):
                    respuesta = self.vincular()
                self.assertIn("No pude completar", voz(respuesta))
                self.tabla.put_item.assert_not_called()
                getattr(cliente, metodo).side_effect = original

    def test_errores_de_dynamodb_tienen_respuesta_global(self):
        self.items["usuario-01"] = {
            "userId": "usuario-01", "thingName": "caja-enigmas-01",
        }
        for metodo, operacion, intent in (
            ("get_item", "GetItem", "ConsultarCerraduraIntent"),
            ("put_item", "PutItem", "VincularCajaIntent"),
            ("delete_item", "DeleteItem", "DesvincularCajaIntent"),
        ):
            with self.subTest(operacion=operacion):
                original = getattr(self.tabla, metodo).side_effect
                getattr(self.tabla, metodo).side_effect = ClientError({
                    "Error": {
                        "Code": "ProvisionedThroughputExceededException",
                        "Message": "Error de tabla simulado",
                    },
                }, operacion)
                with self.assertLogs("manejadores.errores", level="ERROR"):
                    respuesta = self.solicitar(intent, slots={
                        "numeroCaja": "1", "codigo": "0000",
                    })
                self.assertIn("No pude completar", voz(respuesta))
                self.assertIn("usuario-01", self.items)
                getattr(self.tabla, metodo).side_effect = original


if __name__ == "__main__":
    unittest.main()
