#include <Arduino.h>
#include <ESP32Servo.h>
#include <stdlib.h>
#include <string.h>

namespace {

constexpr uint8_t PinServo = 18;
constexpr int AnguloInicialPrueba = 90;
constexpr int AnguloMinimoPrueba = 45;
constexpr int AnguloMaximoPrueba = 135;
constexpr int PasoMaximo = 5;
constexpr unsigned long IntervaloMovimientoMs = 300UL;

Servo servo;
int anguloSolicitado = AnguloInicialPrueba;
unsigned long ultimoMovimientoMs = 0;
char comando[16];
size_t longitudComando = 0;
bool comandoDemasiadoLargo = false;

void mostrarAyuda() {
    Serial.println(F("Comandos con Enter: iniciar, +, -, numero, estado, ayuda."));
    Serial.println(F("iniciar: activa PWM y solicita 90 grados, solo sin carga."));
    Serial.println(F("+ / -: un grado. Numero: 45 a 135, maximo 5 grados por orden."));
    Serial.println(F("Esperar al menos 300 ms entre movimientos. No hay barrido automatico."));
}

void mostrarEstado() {
    if (servo.attached()) {
        Serial.print(F("PWM activo. Ultimo angulo solicitado: "));
        Serial.println(anguloSolicitado);
    } else {
        Serial.println(F("PWM inactivo. Escribir iniciar cuando el montaje este revisado."));
    }
}

void moverA(int angulo) {
    if (!servo.attached()) {
        mostrarEstado();
        return;
    }
    if (angulo < AnguloMinimoPrueba || angulo > AnguloMaximoPrueba) {
        Serial.println(F("Rechazado: ventana de prueba de 45 a 135 grados."));
        return;
    }
    const int diferencia = angulo - anguloSolicitado;
    if (diferencia < -PasoMaximo || diferencia > PasoMaximo) {
        Serial.println(F("Rechazado: avanzar como maximo 5 grados por orden."));
        return;
    }
    if (diferencia == 0) {
        mostrarEstado();
        return;
    }
    const unsigned long ahoraMs = millis();
    if (ahoraMs - ultimoMovimientoMs < IntervaloMovimientoMs) {
        Serial.println(F("Rechazado: esperar 300 ms entre movimientos."));
        return;
    }

    servo.write(angulo);
    anguloSolicitado = angulo;
    ultimoMovimientoMs = ahoraMs;
    mostrarEstado();
}

void ejecutarComando() {
    if (strcmp(comando, "ayuda") == 0) {
        mostrarAyuda();
    } else if (strcmp(comando, "estado") == 0) {
        mostrarEstado();
    } else if (strcmp(comando, "iniciar") == 0) {
        if (!servo.attached()) {
            servo.setPeriodHertz(50);
            servo.attach(PinServo);
            if (servo.attached()) {
                servo.write(AnguloInicialPrueba);
                anguloSolicitado = AnguloInicialPrueba;
                ultimoMovimientoMs = millis();
            }
        }
        mostrarEstado();
    } else if (strcmp(comando, "+") == 0) {
        moverA(anguloSolicitado + 1);
    } else if (strcmp(comando, "-") == 0) {
        moverA(anguloSolicitado - 1);
    } else {
        if (longitudComando > 3) {
            Serial.println(F("Comando invalido. Escribir ayuda."));
            return;
        }
        for (size_t i = 0; i < longitudComando; ++i) {
            if (comando[i] < '0' || comando[i] > '9') {
                Serial.println(F("Comando invalido. Escribir ayuda."));
                return;
            }
        }
        moverA(atoi(comando));
    }
}

}  // namespace

void setup() {
    Serial.begin(115200);
    Serial.println(F("Diagnostico SG90 en GPIO18. PWM inactivo al arrancar."));
    Serial.println(F("Primera prueba sin carga ni brazo conectado a la cerradura."));
    Serial.println(F("Revisar fuente externa de 5 V, polaridad y GND comun antes de conectar."));
    mostrarAyuda();
}

void loop() {
    while (Serial.available() > 0) {
        const char caracter = Serial.read();
        if (caracter == '\r' || caracter == '\n') {
            if (comandoDemasiadoLargo) {
                Serial.println(F("Comando demasiado largo; descartado."));
            } else if (longitudComando > 0) {
                comando[longitudComando] = '\0';
                ejecutarComando();
            }
            longitudComando = 0;
            comandoDemasiadoLargo = false;
        } else if (!comandoDemasiadoLargo) {
            if (longitudComando < sizeof(comando) - 1) {
                comando[longitudComando] = caracter;
                ++longitudComando;
            } else {
                comandoDemasiadoLargo = true;
            }
        }
    }
}
