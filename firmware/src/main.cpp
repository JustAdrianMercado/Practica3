// Caja de los Enigmas - objeto inteligente.
// Sincroniza su estado con el Device Shadow de AWS IoT Core: reporta cerradura, tapa y codigo de
// vinculacion, y aplica las ordenes que llegan en el delta.
// Mientras no se integre CerraduraServo, la cerradura es simulada: la orden se aplica al estado.

#include <Arduino.h>

#include "CodigoVinculacion.h"
#include "ConexionAwsIot.h"
#include "ConexionWifi.h"
#include "EstadoShadow.h"

#if __has_include("ConfiguracionWifi.h")
#include "ConfiguracionWifi.h"
#else
#include "ConfiguracionWifi.ejemplo.h"
#endif

#if __has_include("ConfiguracionAws.h")
#include "ConfiguracionAws.h"
#else
#include "ConfiguracionAws.ejemplo.h"
#endif

namespace {

constexpr char VersionFirmware[] = "0.1.0";
constexpr unsigned long IntervaloReportePeriodicoMs = 60000UL;  // Respaldo (contratos, sec. 3).
constexpr size_t TamanoReporte = 256;

ConexionWifi conexionWifi(NombreRedWifi, ClaveRedWifi);
ConexionAwsIot conexionAws(conexionWifi, EndpointAwsIot, PuertoAwsIot, NombreThing,
                           CertificadoCaAmazon, CertificadoDispositivo, ClavePrivadaDispositivo);
CodigoVinculacion codigoVinculacion;
EstadoShadow estadoShadow(codigoVinculacion.texto(), VersionFirmware);

ConexionAwsIot::MensajeShadow mensajeRecibido;  // Global: 2 KB fuera de la pila de loop().
unsigned long ultimoReporteMs = 0;

void aplicarOrdenCerradura(const OrdenCerradura& orden) {
    if (!orden.estaPresente) {
        return;
    }
    if (!orden.esValida) {
        // Contrato: no mover nada y volver a reportar el estado real.
        Serial.println(F("Orden: valor de cerradura invalido; se reporta el estado real."));
        estadoShadow.solicitarReporte();
        return;
    }
    Serial.print(F("Orden: cerradura -> "));
    Serial.println(EstadoShadow::textoCerradura(orden.estadoPedido));
    estadoShadow.establecerCerradura(orden.estadoPedido);  // Aqui se movera CerraduraServo.
    // Reportar aunque ya estuviera asi: el delta indica que la nube tiene otro valor.
    estadoShadow.solicitarReporte();
}

void procesarMensaje(const ConexionAwsIot::MensajeShadow& mensaje) {
    OrdenCerradura orden;
    bool sePudoLeer = false;
    if (mensaje.tipo == ConexionAwsIot::TipoMensaje::Delta) {
        sePudoLeer = EstadoShadow::leerOrdenDelta(mensaje.contenido, orden);
    } else {
        sePudoLeer = EstadoShadow::leerOrdenDocumentoCompleto(mensaje.contenido, orden);
    }
    if (!sePudoLeer) {
        Serial.println(F("Shadow: mensaje con JSON invalido; se ignora."));
        return;
    }
    aplicarOrdenCerradura(orden);
}

void publicarReporteSiHaceFalta() {
    if (!estadoShadow.hayCambiosSinReportar() || !conexionAws.estaConectada()) {
        return;
    }
    char documento[TamanoReporte];
    if (!estadoShadow.escribirReporte(documento, sizeof(documento))) {
        Serial.println(F("Shadow: el reporte no entra en el buffer."));
        return;
    }
    if (conexionAws.publicarActualizacion(documento)) {
        estadoShadow.confirmarReporte();
        ultimoReporteMs = millis();
        Serial.print(F("Shadow: reportado "));
        Serial.println(documento);
    }
}

void solicitarReportePeriodico() {
    // La resta sin signo sigue funcionando cuando millis() se desborda.
    if (millis() - ultimoReporteMs >= IntervaloReportePeriodicoMs) {
        estadoShadow.solicitarReporte();
    }
}

}  // namespace

void setup() {
    Serial.begin(115200);
    Serial.print(F("Caja de los Enigmas - SIS-234 - firmware "));
    Serial.println(VersionFirmware);

    codigoVinculacion.iniciar();
    Serial.print(F("Vinculacion: codigo de esta caja = "));
    Serial.println(codigoVinculacion.texto());
    conexionWifi.iniciar();
    conexionAws.iniciar();
}

void loop() {
    conexionWifi.actualizar();
    conexionAws.actualizar();

    if (conexionAws.seAcabaDeConectar()) {
        estadoShadow.solicitarReporte();
    }
    while (conexionAws.tomarMensaje(mensajeRecibido)) {
        procesarMensaje(mensajeRecibido);
    }
    solicitarReportePeriodico();
    publicarReporteSiHaceFalta();
}
