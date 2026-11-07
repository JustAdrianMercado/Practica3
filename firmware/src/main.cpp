// Caja de los Enigmas - objeto inteligente.
// Sincroniza su estado con el Device Shadow de AWS IoT Core: mueve el servo de la cerradura
// segun las ordenes del delta y reporta la cerradura, la tapa (reed switch) y el codigo de
// vinculacion. Por Serial acepta comandos de prueba (escribir "ayuda").

#include <Arduino.h>
#include <string.h>

#include "CerraduraServo.h"
#include "CodigoVinculacion.h"
#include "ConexionAwsIot.h"
#include "ConexionWifi.h"
#include "ConfiguracionHardware.h"
#include "ConsolaSerial.h"
#include "EstadoShadow.h"
#include "SensorTapa.h"

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

constexpr char VersionFirmware[] = "0.2.0";
constexpr unsigned long IntervaloReportePeriodicoMs = 60000UL;  // Respaldo (contratos, sec. 3).
constexpr size_t TamanoReporte = 256;

ConexionWifi conexionWifi(NombreRedWifi, ClaveRedWifi);
ConexionAwsIot conexionAws(conexionWifi, EndpointAwsIot, PuertoAwsIot, NombreThing,
                           CertificadoCaAmazon, CertificadoDispositivo, ClavePrivadaDispositivo);
CerraduraServo cerraduraServo(PinServoCerradura, AnguloCerraduraCerradaGrados,
                              AnguloCerraduraAbiertaGrados);
SensorTapa sensorTapa(PinReedTapa);
CodigoVinculacion codigoVinculacion;
EstadoShadow estadoShadow(codigoVinculacion.texto(), VersionFirmware);
ConsolaSerial consola;

ConexionAwsIot::MensajeShadow mensajeRecibido;  // Global: 2 KB fuera de la pila de loop().
unsigned long ultimoReporteMs = 0;

// --- Actuador y sensor ---------------------------------------------------------------------

void moverCerradura(EstadoCerradura estadoPedido) {
    if (estadoPedido == EstadoCerradura::Abierta) {
        cerraduraServo.abrir();
    } else {
        cerraduraServo.cerrar();
    }
    estadoShadow.establecerCerradura(estadoPedido);
    Serial.print(F("Cerradura: "));
    Serial.println(EstadoShadow::textoCerradura(estadoPedido));
}

EstadoTapa leerEstadoTapa() {
    return sensorTapa.estaAbierta() ? EstadoTapa::Abierta : EstadoTapa::Cerrada;
}

void actualizarTapa() {
    sensorTapa.actualizar();
    if (!sensorTapa.huboCambio()) {
        return;
    }
    const EstadoTapa estadoTapa = leerEstadoTapa();
    estadoShadow.establecerTapa(estadoTapa);  // Se reporta en esta misma vuelta del loop().
    Serial.print(F("Tapa: "));
    Serial.println(EstadoShadow::textoTapa(estadoTapa));
}

// --- Ordenes del Shadow ----------------------------------------------------------------------

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
    Serial.print(F("Orden del Shadow: "));
    moverCerradura(orden.estadoPedido);
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

// --- Reportes --------------------------------------------------------------------------------

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

// --- Consola de prueba -----------------------------------------------------------------------

void mostrarAyuda() {
    Serial.println(F("Comandos: abrir, cerrar, estado, codigo, ayuda."));
    Serial.println(F("Con conexion a AWS, el desired del Shadow manda: puede revertir abrir/cerrar."));
}

void mostrarEstado() {
    Serial.print(F("Estado: cerradura="));
    Serial.print(EstadoShadow::textoCerradura(estadoShadow.cerradura()));
    Serial.print(F(" tapa="));
    Serial.print(EstadoShadow::textoTapa(estadoShadow.tapa()));
    Serial.print(F(" aws="));
    Serial.println(conexionAws.estaConectada() ? F("conectado") : F("desconectado"));
}

void ejecutarComando(const char* comando) {
    if (strcmp(comando, "abrir") == 0) {
        moverCerradura(EstadoCerradura::Abierta);
    } else if (strcmp(comando, "cerrar") == 0) {
        moverCerradura(EstadoCerradura::Cerrada);
    } else if (strcmp(comando, "estado") == 0) {
        mostrarEstado();
    } else if (strcmp(comando, "codigo") == 0) {
        Serial.print(F("Vinculacion: codigo de esta caja = "));
        Serial.println(codigoVinculacion.texto());
    } else {
        mostrarAyuda();
    }
}

void atenderConsola() {
    if (consola.leerComando()) {
        ejecutarComando(consola.comando());
    }
}

}  // namespace

void setup() {
    Serial.begin(115200);
    Serial.print(F("Caja de los Enigmas - SIS-234 - firmware "));
    Serial.println(VersionFirmware);

    cerraduraServo.iniciar();  // Arranca cerrada.
    sensorTapa.iniciar();
    estadoShadow.establecerCerradura(EstadoCerradura::Cerrada);
    estadoShadow.establecerTapa(leerEstadoTapa());

    codigoVinculacion.iniciar();
    Serial.print(F("Vinculacion: codigo de esta caja = "));
    Serial.println(codigoVinculacion.texto());

    conexionWifi.iniciar();
    conexionAws.iniciar();
    mostrarAyuda();
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
    actualizarTapa();
    atenderConsola();
    solicitarReportePeriodico();
    publicarReporteSiHaceFalta();
}
