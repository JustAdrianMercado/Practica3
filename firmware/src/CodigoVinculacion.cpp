#include "CodigoVinculacion.h"

#include <Arduino.h>
#include <Preferences.h>
#include <ctype.h>
#include <esp_random.h>
#include <stdio.h>
#include <string.h>

namespace {

constexpr char EspacioNvs[] = "caja";  // Maximo 15 caracteres (limite de la NVS).
constexpr char ClaveCodigo[] = "codigo";
constexpr uint32_t CantidadCodigosPosibles = 10000;  // De 0000 a 9999.
constexpr bool SoloLectura = true;

}  // namespace

void CodigoVinculacion::iniciar() {
    if (leerGuardado()) {
        return;
    }
    generarYGuardar();
}

const char* CodigoVinculacion::texto() const {
    return texto_;
}

bool CodigoVinculacion::leerGuardado() {
    Preferences memoria;
    if (!memoria.begin(EspacioNvs, SoloLectura)) {
        return false;  // Primer arranque: el espacio todavia no existe.
    }
    char candidato[CantidadDigitos + 1] = {};
    memoria.getString(ClaveCodigo, candidato, sizeof(candidato));
    memoria.end();

    if (!esCodigoValido(candidato)) {
        return false;
    }
    memcpy(texto_, candidato, sizeof(texto_));
    return true;
}

void CodigoVinculacion::generarYGuardar() {
    const uint32_t numero = esp_random() % CantidadCodigosPosibles;
    snprintf(texto_, sizeof(texto_), "%04lu", static_cast<unsigned long>(numero));

    Preferences memoria;
    if (!memoria.begin(EspacioNvs, !SoloLectura) || memoria.putString(ClaveCodigo, texto_) == 0) {
        // Sin NVS el codigo sirve igual hasta el proximo reinicio, pero cambiara.
        Serial.println(F("Vinculacion: no se pudo guardar el codigo en la NVS."));
    }
    memoria.end();
}

bool CodigoVinculacion::esCodigoValido(const char* candidato) {
    if (strlen(candidato) != CantidadDigitos) {
        return false;
    }
    for (size_t indice = 0; indice < CantidadDigitos; ++indice) {
        if (!isdigit(static_cast<unsigned char>(candidato[indice]))) {
            return false;
        }
    }
    return true;
}
