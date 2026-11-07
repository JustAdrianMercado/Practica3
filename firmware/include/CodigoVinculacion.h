#pragma once

#include <stddef.h>

/**
 * Codigo de 4 digitos con el que un usuario de Alexa vincula esta caja (docs/contratos.md,
 * seccion 4). Se genera al azar en el primer arranque y se guarda en la memoria NVS, asi se
 * conserva tras reinicios y nuevas cargas de firmware.
 */
class CodigoVinculacion {
public:
    static constexpr size_t CantidadDigitos = 4;

    // Llamar despues de iniciar el WiFi: con la radio encendida, esp_random() es aleatorio.
    void iniciar();

    // Texto de 4 digitos terminado en cero; vacio hasta llamar a iniciar().
    const char* texto() const;

private:
    char texto_[CantidadDigitos + 1] = {};

    bool leerGuardado();
    void generarYGuardar();
    static bool esCodigoValido(const char* candidato);
};
