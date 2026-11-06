// Caja de los Enigmas - objeto inteligente (Iteracion 0).
// Por ahora solo mantiene la conexion WiFi; AWS IoT, servo y sensor se agregan en las
// siguientes iteraciones (ver docs/planificacion).

#include <Arduino.h>

#include "ConexionWifi.h"

#if __has_include("ConfiguracionWifi.h")
#include "ConfiguracionWifi.h"
#else
#include "ConfiguracionWifi.ejemplo.h"
#endif

namespace {

ConexionWifi conexionWifi(NombreRedWifi, ClaveRedWifi);

}  // namespace

void setup() {
    Serial.begin(115200);
    Serial.println(F("Caja de los Enigmas - SIS-234 - Iteracion 0"));
    conexionWifi.iniciar();
}

void loop() {
    conexionWifi.actualizar();
}
