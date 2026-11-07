#include "SensorTapa.h"

#include <Arduino.h>

SensorTapa::SensorTapa(uint8_t pin) : pin_(pin) {}

void SensorTapa::iniciar() {
    pinMode(pin_, INPUT_PULLUP);
    ultimaLecturaAbierta_ = digitalRead(pin_) == HIGH;
    abierta_ = ultimaLecturaAbierta_;
    ultimoCambioLecturaMs_ = millis();
    cambioPendiente_ = false;
}

void SensorTapa::actualizar() {
    const bool lecturaAbierta = digitalRead(pin_) == HIGH;
    const unsigned long ahoraMs = millis();

    if (lecturaAbierta != ultimaLecturaAbierta_) {
        ultimaLecturaAbierta_ = lecturaAbierta;
        ultimoCambioLecturaMs_ = ahoraMs;
    }

    if (ultimaLecturaAbierta_ != abierta_ &&
        ahoraMs - ultimoCambioLecturaMs_ >= AntirreboteMs) {
        abierta_ = ultimaLecturaAbierta_;
        cambioPendiente_ = true;
    }
}

bool SensorTapa::estaAbierta() const {
    return abierta_;
}

bool SensorTapa::huboCambio() {
    const bool cambio = cambioPendiente_;
    cambioPendiente_ = false;
    return cambio;
}
