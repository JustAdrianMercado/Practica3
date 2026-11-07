#include "CerraduraServo.h"

#include <string.h>

CerraduraServo::CerraduraServo(uint8_t pin, int anguloCerrada, int anguloAbierta)
    : pin_(pin), anguloCerrada_(anguloCerrada), anguloAbierta_(anguloAbierta) {}

void CerraduraServo::iniciar() {
    servo_.attach(pin_);
    cerrar();
}

void CerraduraServo::abrir() {
    servo_.write(anguloAbierta_);
    abierta_ = true;
}

void CerraduraServo::cerrar() {
    servo_.write(anguloCerrada_);
    abierta_ = false;
}

bool CerraduraServo::estaAbierta() const {
    return abierta_;
}

bool CerraduraServo::aplicar(const char* estado) {
    if (estado == nullptr) {
        return false;
    }

    if (strcmp(estado, "abierta") == 0) {
        abrir();
    } else if (strcmp(estado, "cerrada") == 0) {
        cerrar();
    } else {
        return false;
    }

    return true;
}
