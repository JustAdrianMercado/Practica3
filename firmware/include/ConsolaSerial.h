#pragma once

#include <stddef.h>

/**
 * Lee comandos de texto por el monitor Serial sin bloquear el loop().
 * Acepta lineas terminadas en LF, CR o CRLF. Una linea demasiado larga o con caracteres de
 * control se descarta completa: nunca se ejecuta un comando cortado a la mitad.
 */
class ConsolaSerial {
public:
    static constexpr size_t LongitudMaximaComando = 31;

    // true cuando termino de llegar una linea valida; queda disponible en comando().
    bool leerComando();
    const char* comando() const;

private:
    static constexpr size_t BytesMaximosPorVuelta = 32;  // No postergar el resto del loop().

    char comandoListo_[LongitudMaximaComando + 1] = {};
    char lineaEnCurso_[LongitudMaximaComando + 1] = {};
    size_t longitudEnCurso_ = 0;
    bool lineaEnCursoEsInvalida_ = false;
    bool anteriorFueRetornoDeCarro_ = false;

    void agregarCaracter(char caracter);
    bool terminarLinea();
};
