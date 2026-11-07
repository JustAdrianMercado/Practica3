#pragma once

#include <stdint.h>

// Convencion provisional: LOW = tapa cerrada, HIGH = abierta.
// Pendiente verificar con el reed y el iman del montaje real.
class SensorTapa {
public:
    SensorTapa(uint8_t pin);

    void iniciar();
    void actualizar();
    bool estaAbierta() const;
    bool huboCambio();

private:
    static constexpr unsigned long AntirreboteMs = 50UL;

    uint8_t pin_;
    bool ultimaLecturaAbierta_ = false;
    bool abierta_ = false;
    bool cambioPendiente_ = false;
    unsigned long ultimoCambioLecturaMs_ = 0;
};
