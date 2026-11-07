#pragma once

#include <stdint.h>
#include <ESP32Servo.h>

class CerraduraServo {
public:
    CerraduraServo(uint8_t pin, int anguloCerrada, int anguloAbierta);

    void iniciar();
    void abrir();
    void cerrar();
    bool estaAbierta() const;
    bool aplicar(const char* estado);

private:
    uint8_t pin_;
    int anguloCerrada_;
    int anguloAbierta_;
    Servo servo_;
    bool abierta_ = false;
};
