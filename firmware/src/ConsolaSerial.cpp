#include "ConsolaSerial.h"

#include <Arduino.h>
#include <string.h>

namespace {

constexpr uint8_t PrimerCaracterImprimible = 32;  // Espacio.
constexpr uint8_t UltimoCaracterImprimible = 126;  // Virgulilla (~).

bool esFinDeLinea(char caracter) {
    return caracter == '\r' || caracter == '\n';
}

bool esImprimible(char caracter) {
    const uint8_t valor = static_cast<uint8_t>(caracter);
    return valor >= PrimerCaracterImprimible && valor <= UltimoCaracterImprimible;
}

}  // namespace

bool ConsolaSerial::leerComando() {
    for (size_t leidos = 0; leidos < BytesMaximosPorVuelta && Serial.available() > 0; ++leidos) {
        const char caracter = static_cast<char>(Serial.read());
        if (!esFinDeLinea(caracter)) {
            anteriorFueRetornoDeCarro_ = false;
            agregarCaracter(caracter);
            continue;
        }
        // CRLF es un unico fin de linea, aunque el LF llegue en otra vuelta.
        const bool esLfDeUnCrlf = caracter == '\n' && anteriorFueRetornoDeCarro_;
        anteriorFueRetornoDeCarro_ = caracter == '\r';
        if (!esLfDeUnCrlf && terminarLinea()) {
            return true;
        }
    }
    return false;
}

const char* ConsolaSerial::comando() const {
    return comandoListo_;
}

void ConsolaSerial::agregarCaracter(char caracter) {
    if (lineaEnCursoEsInvalida_) {
        return;  // Se descarta hasta el fin de linea.
    }
    if (!esImprimible(caracter) || longitudEnCurso_ >= LongitudMaximaComando) {
        lineaEnCursoEsInvalida_ = true;
        return;
    }
    lineaEnCurso_[longitudEnCurso_++] = caracter;
    lineaEnCurso_[longitudEnCurso_] = '\0';
}

bool ConsolaSerial::terminarLinea() {
    const bool esValida = !lineaEnCursoEsInvalida_ && longitudEnCurso_ > 0;
    if (esValida) {
        memcpy(comandoListo_, lineaEnCurso_, longitudEnCurso_ + 1);
    } else if (lineaEnCursoEsInvalida_) {
        Serial.println(F("Consola: linea demasiado larga o con caracteres invalidos; descartada."));
    }
    longitudEnCurso_ = 0;
    lineaEnCurso_[0] = '\0';
    lineaEnCursoEsInvalida_ = false;
    return esValida;
}
