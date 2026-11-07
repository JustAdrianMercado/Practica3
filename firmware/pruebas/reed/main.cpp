#include <Arduino.h>

#include "SensorTapa.h"

namespace {

constexpr uint8_t PinReed = 4;
constexpr unsigned long IntervaloReporteMs = 1000UL;

SensorTapa sensorTapa(PinReed);
int ultimaLectura = HIGH;
unsigned long ultimoReporteMs = 0;

void mostrarLectura(int lectura) {
    Serial.print(millis());
    Serial.print(F(" ms | electrica sin antirrebote: "));
    if (lectura == LOW) {
        Serial.println(F("LOW | contacto cerrado hacia GND"));
    } else {
        Serial.println(F("HIGH | contacto abierto"));
    }
}

void mostrarInterpretacion() {
    Serial.print(millis());
    Serial.print(F(" ms | SensorTapa, interpretacion provisional: "));
    if (sensorTapa.estaAbierta()) {
        Serial.println(F("tapa abierta"));
    } else {
        Serial.println(F("tapa cerrada"));
    }
}

}  // namespace

void setup() {
    Serial.begin(115200);
    sensorTapa.iniciar();
    Serial.println(F("Diagnostico reed GPIO4 a GND, INPUT_PULLUP."));
    Serial.println(F("LOW = tapa cerrada es provisional: comprobar con el iman."));
    Serial.println(F("Estado inicial de referencia; no es un evento de cambio."));
    ultimaLectura = digitalRead(PinReed);
    mostrarLectura(ultimaLectura);
    mostrarInterpretacion();
    ultimoReporteMs = millis();
}

void loop() {
    sensorTapa.actualizar();
    const int lectura = digitalRead(PinReed);
    if (lectura != ultimaLectura) {
        ultimaLectura = lectura;
        mostrarLectura(lectura);
    }

    if (sensorTapa.huboCambio()) {
        Serial.println(F("Cambio confirmado por SensorTapa tras 50 ms estables."));
        mostrarInterpretacion();
    }

    const unsigned long ahoraMs = millis();
    if (ahoraMs - ultimoReporteMs >= IntervaloReporteMs) {
        ultimoReporteMs = ahoraMs;
        Serial.println(F("Resumen periodico:"));
        mostrarLectura(lectura);
        mostrarInterpretacion();
    }
}
