// Caja de los Enigmas - objeto inteligente (Iteracion 0: esqueleto de punta a punta).
// Se conecta a AWS IoT Core, publica un estado reportado fijo y muestra por Serial los mensajes
// del Shadow. Servo, reed switch y codigo de vinculacion se agregan en la Iteracion 1.

#include <Arduino.h>

#include "ConexionAwsIot.h"
#include "ConexionWifi.h"

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

constexpr char VersionFirmware[] = "0.0.1";
constexpr unsigned long IntervaloReporteMs = 60000UL;  // Reporte periodico de respaldo.

ConexionWifi conexionWifi(NombreRedWifi, ClaveRedWifi);
ConexionAwsIot conexionAws(conexionWifi, EndpointAwsIot, PuertoAwsIot, NombreThing,
                           CertificadoCaAmazon, CertificadoDispositivo, ClavePrivadaDispositivo);
ConexionAwsIot::MensajeShadow mensaje;  // Global: 2 KB fuera de la pila de loop().
unsigned long ultimoReporteMs = 0;

// Estado provisional hasta integrar CerraduraServo, SensorTapa y CodigoVinculacion.
void publicarReporte() {
    char documento[192];
    snprintf(documento, sizeof(documento),
             "{\"state\":{\"reported\":{\"cerradura\":\"cerrada\",\"tapa\":\"cerrada\","
             "\"codigoVinculacion\":\"0000\",\"firmware\":\"%s\"}}}",
             VersionFirmware);
    if (conexionAws.publicarActualizacion(documento)) {
        ultimoReporteMs = millis();
        Serial.print(F("Shadow: reportado "));
        Serial.println(documento);
    }
}

void mostrarMensaje(const ConexionAwsIot::MensajeShadow& recibido) {
    if (recibido.tipo == ConexionAwsIot::TipoMensaje::Delta) {
        Serial.print(F("Shadow: delta recibido "));
    } else {
        Serial.print(F("Shadow: documento completo "));
    }
    Serial.println(recibido.contenido);
}

}  // namespace

void setup() {
    Serial.begin(115200);
    Serial.println(F("Caja de los Enigmas - SIS-234 - Iteracion 0"));
    conexionWifi.iniciar();
    conexionAws.iniciar();
}

void loop() {
    conexionWifi.actualizar();
    conexionAws.actualizar();

    if (conexionAws.seAcabaDeConectar()) {
        publicarReporte();
    }
    while (conexionAws.tomarMensaje(mensaje)) {
        mostrarMensaje(mensaje);
    }
    // La resta sin signo sigue funcionando cuando millis() se desborda.
    if (conexionAws.estaConectada() && millis() - ultimoReporteMs >= IntervaloReporteMs) {
        publicarReporte();
    }
}
