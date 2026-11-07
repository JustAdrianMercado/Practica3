#include "EstadoShadow.h"

#include <ArduinoJson.h>
#include <string.h>

namespace {

constexpr char TextoAbierta[] = "abierta";
constexpr char TextoCerrada[] = "cerrada";

// Convierte el valor recibido del Shadow; cualquier cosa que no sea texto valido se rechaza.
bool leerTextoCerradura(const char* texto, EstadoCerradura& estado) {
    if (texto == nullptr) {
        return false;
    }
    if (strcmp(texto, TextoAbierta) == 0) {
        estado = EstadoCerradura::Abierta;
        return true;
    }
    if (strcmp(texto, TextoCerrada) == 0) {
        estado = EstadoCerradura::Cerrada;
        return true;
    }
    return false;
}

OrdenCerradura interpretarCerradura(JsonVariantConst valorRecibido) {
    OrdenCerradura orden;
    if (valorRecibido.isNull()) {
        return orden;  // El mensaje no habla de la cerradura.
    }
    orden.estaPresente = true;
    orden.esValida = leerTextoCerradura(valorRecibido.as<const char*>(), orden.estadoPedido);
    return orden;
}

// El filtro descarta los metadatos y los atributos desconocidos: ahorra memoria al leer.
bool deserializarConFiltro(const char* json, const JsonDocument& filtro,
                           JsonDocument& documento) {
    if (json == nullptr) {
        return false;
    }
    const DeserializationError error =
        deserializeJson(documento, json, DeserializationOption::Filter(filtro));
    return !error;
}

}  // namespace

EstadoShadow::EstadoShadow(const char* codigoVinculacion, const char* versionFirmware)
    : codigoVinculacion_(codigoVinculacion), versionFirmware_(versionFirmware) {}

EstadoCerradura EstadoShadow::cerradura() const {
    return cerradura_;
}

EstadoTapa EstadoShadow::tapa() const {
    return tapa_;
}

void EstadoShadow::establecerCerradura(EstadoCerradura nuevoEstado) {
    if (nuevoEstado != cerradura_) {
        cerradura_ = nuevoEstado;
        hayCambiosSinReportar_ = true;
    }
}

void EstadoShadow::establecerTapa(EstadoTapa nuevoEstado) {
    if (nuevoEstado != tapa_) {
        tapa_ = nuevoEstado;
        hayCambiosSinReportar_ = true;
    }
}

void EstadoShadow::solicitarReporte() {
    hayCambiosSinReportar_ = true;
}

bool EstadoShadow::hayCambiosSinReportar() const {
    return hayCambiosSinReportar_;
}

void EstadoShadow::confirmarReporte() {
    hayCambiosSinReportar_ = false;
}

bool EstadoShadow::escribirReporte(char* destino, size_t capacidad) const {
    if (destino == nullptr || capacidad == 0) {
        return false;
    }
    JsonDocument documento;
    JsonObject reportado = documento["state"]["reported"].to<JsonObject>();
    reportado["cerradura"] = textoCerradura(cerradura_);
    reportado["tapa"] = textoTapa(tapa_);
    reportado["codigoVinculacion"] = codigoVinculacion_;
    reportado["firmware"] = versionFirmware_;

    // measureJson no cuenta el terminador: hace falta un byte mas.
    if (measureJson(documento) >= capacidad) {
        return false;
    }
    serializeJson(documento, destino, capacidad);
    return true;
}

bool EstadoShadow::leerOrdenDelta(const char* json, OrdenCerradura& orden) {
    JsonDocument filtro;
    filtro["state"]["cerradura"] = true;
    JsonDocument documento;
    if (!deserializarConFiltro(json, filtro, documento)) {
        return false;
    }
    orden = interpretarCerradura(documento["state"]["cerradura"]);
    return true;
}

bool EstadoShadow::leerOrdenDocumentoCompleto(const char* json, OrdenCerradura& orden) {
    JsonDocument filtro;
    filtro["state"]["delta"]["cerradura"] = true;
    JsonDocument documento;
    if (!deserializarConFiltro(json, filtro, documento)) {
        return false;
    }
    orden = interpretarCerradura(documento["state"]["delta"]["cerradura"]);
    return true;
}

const char* EstadoShadow::textoCerradura(EstadoCerradura estado) {
    return estado == EstadoCerradura::Abierta ? TextoAbierta : TextoCerrada;
}

const char* EstadoShadow::textoTapa(EstadoTapa estado) {
    return estado == EstadoTapa::Abierta ? TextoAbierta : TextoCerrada;
}
