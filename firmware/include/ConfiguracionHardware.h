#pragma once

#include <stdint.h>

// Pines y calibracion del montaje (docs/contratos.md, seccion 8; docs/GUIA_MONTAJE.md).
// No contiene secretos: se versiona. Al calibrar el montaje real, cambiar solo este archivo.

constexpr uint8_t PinServoCerradura = 18;  // Senal del SG90; se alimenta con 5 V externos.
constexpr uint8_t PinReedTapa = 4;         // Reed a GND con INPUT_PULLUP: LOW = tapa cerrada.

// PROVISIONALES: dentro del rango seguro 45-135 de firmware/pruebas/servo.
// Calibrar con esa prueba los angulos que de verdad traban y destraban la tapa.
constexpr int AnguloCerraduraCerradaGrados = 45;
constexpr int AnguloCerraduraAbiertaGrados = 135;
