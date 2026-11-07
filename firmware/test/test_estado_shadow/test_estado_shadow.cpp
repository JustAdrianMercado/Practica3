// Pruebas de EstadoShadow en la PC: lectura de ordenes del Shadow y armado del reporte.
// Ejecutar desde firmware/: pio test -e pruebas

#include <unity.h>

#include <string.h>

#include "EstadoShadow.h"

namespace {

constexpr char CodigoDePrueba[] = "4821";
constexpr char VersionDePrueba[] = "0.1.0";

}  // namespace

void setUp() {}
void tearDown() {}

// --- Lectura del delta -----------------------------------------------------------------------

void test_delta_con_cerradura_abierta_es_orden_valida() {
    const char delta[] =
        R"({"version":17,"timestamp":1794088381,"state":{"cerradura":"abierta"},)"
        R"("metadata":{"cerradura":{"timestamp":1794088381}}})";
    OrdenCerradura orden;
    TEST_ASSERT_TRUE(EstadoShadow::leerOrdenDelta(delta, orden));
    TEST_ASSERT_TRUE(orden.estaPresente);
    TEST_ASSERT_TRUE(orden.esValida);
    TEST_ASSERT_TRUE(orden.estadoPedido == EstadoCerradura::Abierta);
}

void test_delta_con_cerradura_cerrada_es_orden_valida() {
    OrdenCerradura orden;
    TEST_ASSERT_TRUE(EstadoShadow::leerOrdenDelta(R"({"state":{"cerradura":"cerrada"}})", orden));
    TEST_ASSERT_TRUE(orden.esValida);
    TEST_ASSERT_TRUE(orden.estadoPedido == EstadoCerradura::Cerrada);
}

void test_delta_sin_cerradura_no_trae_orden() {
    OrdenCerradura orden;
    TEST_ASSERT_TRUE(EstadoShadow::leerOrdenDelta(R"({"state":{"nivel":2}})", orden));
    TEST_ASSERT_FALSE(orden.estaPresente);
}

void test_delta_con_valor_desconocido_es_invalido() {
    OrdenCerradura orden;
    TEST_ASSERT_TRUE(EstadoShadow::leerOrdenDelta(R"({"state":{"cerradura":"medio"}})", orden));
    TEST_ASSERT_TRUE(orden.estaPresente);
    TEST_ASSERT_FALSE(orden.esValida);
}

void test_delta_con_valor_que_no_es_texto_es_invalido() {
    OrdenCerradura orden;
    TEST_ASSERT_TRUE(EstadoShadow::leerOrdenDelta(R"({"state":{"cerradura":1}})", orden));
    TEST_ASSERT_TRUE(orden.estaPresente);
    TEST_ASSERT_FALSE(orden.esValida);
}

void test_json_mal_formado_no_se_puede_leer() {
    OrdenCerradura orden;
    TEST_ASSERT_FALSE(EstadoShadow::leerOrdenDelta(R"({"state":{"cerradura":)", orden));
    TEST_ASSERT_FALSE(EstadoShadow::leerOrdenDelta(nullptr, orden));
}

// --- Lectura del documento completo (get/accepted) -------------------------------------------

void test_documento_completo_con_delta_pendiente_trae_la_orden() {
    const char documento[] =
        R"({"state":{"desired":{"cerradura":"abierta"},)"
        R"("reported":{"cerradura":"cerrada","tapa":"cerrada"},)"
        R"("delta":{"cerradura":"abierta"}},"metadata":{},"version":19})";
    OrdenCerradura orden;
    TEST_ASSERT_TRUE(EstadoShadow::leerOrdenDocumentoCompleto(documento, orden));
    TEST_ASSERT_TRUE(orden.esValida);
    TEST_ASSERT_TRUE(orden.estadoPedido == EstadoCerradura::Abierta);
}

void test_documento_completo_sin_delta_no_trae_orden() {
    const char documento[] =
        R"({"state":{"desired":{"cerradura":"cerrada"},"reported":{"cerradura":"cerrada"}}})";
    OrdenCerradura orden;
    TEST_ASSERT_TRUE(EstadoShadow::leerOrdenDocumentoCompleto(documento, orden));
    TEST_ASSERT_FALSE(orden.estaPresente);
}

void test_documento_completo_ignora_desired_fuera_del_delta() {
    // desired.cerradura ya coincide con reported: no hay que mover nada.
    const char documento[] = R"({"state":{"desired":{"cerradura":"abierta"},"delta":{}}})";
    OrdenCerradura orden;
    TEST_ASSERT_TRUE(EstadoShadow::leerOrdenDocumentoCompleto(documento, orden));
    TEST_ASSERT_FALSE(orden.estaPresente);
}

// --- Reporte -------------------------------------------------------------------------------

void test_reporte_inicial_tiene_el_formato_del_contrato() {
    EstadoShadow estado(CodigoDePrueba, VersionDePrueba);
    char documento[256];
    TEST_ASSERT_TRUE(estado.escribirReporte(documento, sizeof(documento)));
    TEST_ASSERT_EQUAL_STRING(
        R"({"state":{"reported":{"cerradura":"cerrada","tapa":"cerrada",)"
        R"("codigoVinculacion":"4821","firmware":"0.1.0"}}})",
        documento);
}

void test_reporte_refleja_los_cambios_de_estado() {
    EstadoShadow estado(CodigoDePrueba, VersionDePrueba);
    estado.establecerCerradura(EstadoCerradura::Abierta);
    estado.establecerTapa(EstadoTapa::Abierta);
    char documento[256];
    TEST_ASSERT_TRUE(estado.escribirReporte(documento, sizeof(documento)));
    TEST_ASSERT_NOT_NULL(strstr(documento, R"("cerradura":"abierta")"));
    TEST_ASSERT_NOT_NULL(strstr(documento, R"("tapa":"abierta")"));
}

void test_reporte_que_no_entra_se_rechaza_sin_escribir_de_mas() {
    EstadoShadow estado(CodigoDePrueba, VersionDePrueba);
    char documento[20];
    TEST_ASSERT_FALSE(estado.escribirReporte(documento, sizeof(documento)));
}

// --- Cambios pendientes de reportar -----------------------------------------------------------

void test_el_primer_reporte_siempre_esta_pendiente() {
    EstadoShadow estado(CodigoDePrueba, VersionDePrueba);
    TEST_ASSERT_TRUE(estado.hayCambiosSinReportar());
}

void test_confirmar_el_reporte_limpia_los_cambios() {
    EstadoShadow estado(CodigoDePrueba, VersionDePrueba);
    estado.confirmarReporte();
    TEST_ASSERT_FALSE(estado.hayCambiosSinReportar());
}

void test_repetir_el_mismo_estado_no_genera_cambios() {
    EstadoShadow estado(CodigoDePrueba, VersionDePrueba);
    estado.confirmarReporte();
    estado.establecerCerradura(EstadoCerradura::Cerrada);
    estado.establecerTapa(EstadoTapa::Cerrada);
    TEST_ASSERT_FALSE(estado.hayCambiosSinReportar());
}

void test_cambiar_la_tapa_genera_un_cambio() {
    EstadoShadow estado(CodigoDePrueba, VersionDePrueba);
    estado.confirmarReporte();
    estado.establecerTapa(EstadoTapa::Abierta);
    TEST_ASSERT_TRUE(estado.hayCambiosSinReportar());
}

void test_solicitar_reporte_lo_deja_pendiente_aunque_nada_cambie() {
    EstadoShadow estado(CodigoDePrueba, VersionDePrueba);
    estado.confirmarReporte();
    estado.solicitarReporte();
    TEST_ASSERT_TRUE(estado.hayCambiosSinReportar());
}

int main() {
    UNITY_BEGIN();
    RUN_TEST(test_delta_con_cerradura_abierta_es_orden_valida);
    RUN_TEST(test_delta_con_cerradura_cerrada_es_orden_valida);
    RUN_TEST(test_delta_sin_cerradura_no_trae_orden);
    RUN_TEST(test_delta_con_valor_desconocido_es_invalido);
    RUN_TEST(test_delta_con_valor_que_no_es_texto_es_invalido);
    RUN_TEST(test_json_mal_formado_no_se_puede_leer);
    RUN_TEST(test_documento_completo_con_delta_pendiente_trae_la_orden);
    RUN_TEST(test_documento_completo_sin_delta_no_trae_orden);
    RUN_TEST(test_documento_completo_ignora_desired_fuera_del_delta);
    RUN_TEST(test_reporte_inicial_tiene_el_formato_del_contrato);
    RUN_TEST(test_reporte_refleja_los_cambios_de_estado);
    RUN_TEST(test_reporte_que_no_entra_se_rechaza_sin_escribir_de_mas);
    RUN_TEST(test_el_primer_reporte_siempre_esta_pendiente);
    RUN_TEST(test_confirmar_el_reporte_limpia_los_cambios);
    RUN_TEST(test_repetir_el_mismo_estado_no_genera_cambios);
    RUN_TEST(test_cambiar_la_tapa_genera_un_cambio);
    RUN_TEST(test_solicitar_reporte_lo_deja_pendiente_aunque_nada_cambie);
    return UNITY_END();
}
