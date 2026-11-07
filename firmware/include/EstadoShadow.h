#pragma once

#include <stddef.h>
#include <stdint.h>

enum class EstadoCerradura : uint8_t { Cerrada, Abierta };
enum class EstadoTapa : uint8_t { Cerrada, Abierta };

/** Lo que un mensaje del Shadow pide sobre la cerradura. */
struct OrdenCerradura {
    bool estaPresente = false;  // El mensaje incluye el atributo "cerradura".
    bool esValida = false;      // Su valor es "abierta" o "cerrada".
    EstadoCerradura estadoPedido = EstadoCerradura::Cerrada;
};

/**
 * Estado del objeto que se sincroniza con el Device Shadow (docs/contratos.md, seccion 2).
 *
 * Guarda lo que el ESP32 reporta, lee las ordenes que llegan en el delta y arma el documento
 * "reported". No depende de Arduino, por eso se prueba en la PC (firmware/test).
 */
class EstadoShadow {
public:
    // Las cadenas deben seguir existiendo durante toda la vida del objeto.
    EstadoShadow(const char* codigoVinculacion, const char* versionFirmware);

    EstadoCerradura cerradura() const;
    EstadoTapa tapa() const;
    void establecerCerradura(EstadoCerradura nuevoEstado);
    void establecerTapa(EstadoTapa nuevoEstado);

    // Pide reportar aunque nada haya cambiado: al reconectar, cada 60 s o tras un valor invalido.
    void solicitarReporte();
    bool hayCambiosSinReportar() const;

    // Escribe {"state":{"reported":{...}}}. Devuelve false si el documento no entra en el destino.
    bool escribirReporte(char* destino, size_t capacidad) const;

    // Llamar solo cuando el reporte se publico con exito.
    void confirmarReporte();

    // Mensaje de update/delta: {"state":{"cerradura":"abierta"}, ...}.
    static bool leerOrdenDelta(const char* json, OrdenCerradura& orden);

    // Mensaje de get/accepted: la orden pendiente esta en {"state":{"delta":{...}}}.
    static bool leerOrdenDocumentoCompleto(const char* json, OrdenCerradura& orden);

    static const char* textoCerradura(EstadoCerradura estado);
    static const char* textoTapa(EstadoTapa estado);

private:
    const char* codigoVinculacion_;
    const char* versionFirmware_;
    EstadoCerradura cerradura_ = EstadoCerradura::Cerrada;
    EstadoTapa tapa_ = EstadoTapa::Cerrada;
    bool hayCambiosSinReportar_ = true;  // El primer reporte siempre se envia.
};
