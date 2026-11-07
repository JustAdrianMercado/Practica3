#include "ConexionAwsIot.h"

#include <WiFi.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

namespace {

constexpr time_t FechaMinimaValida = 1767225600;  // 1 de enero de 2026, UTC.
constexpr unsigned long TiempoConexionTcpMs = 5000UL;
constexpr unsigned long TiempoHandshakeTlsS = 10UL;  // El TLS mutuo tarda varios segundos.
constexpr int TiempoOperacionMqttMs = 3000;          // CONNACK, SUBACK y PUBACK.
constexpr int KeepAliveS = 30;

bool cadenaVacia(const char* texto) {
    return texto == nullptr || texto[0] == '\0';
}

}  // namespace

ConexionAwsIot::ConexionAwsIot(ConexionWifi& conexionWifi, const char* endpoint,
                               unsigned short puerto, const char* nombreThing,
                               const char* certificadoCa, const char* certificadoDispositivo,
                               const char* clavePrivada)
    : conexionWifi_(conexionWifi),
      endpoint_(endpoint),
      puerto_(puerto),
      nombreThing_(nombreThing),
      certificadoCa_(certificadoCa),
      certificadoDispositivo_(certificadoDispositivo),
      clavePrivada_(clavePrivada) {}

bool ConexionAwsIot::configuracionCompleta() const {
    return !cadenaVacia(endpoint_) && !cadenaVacia(nombreThing_) && !cadenaVacia(certificadoCa_) &&
           !cadenaVacia(certificadoDispositivo_) && !cadenaVacia(clavePrivada_) && puerto_ == 8883;
}

bool ConexionAwsIot::armarTemas() {
    struct Tema {
        char* destino;
        const char* sufijo;
    };
    const Tema temas[] = {
        {temaActualizar_, "update"},
        {temaDelta_, "update/delta"},
        {temaPedirDocumento_, "get"},
        {temaDocumentoAceptado_, "get/accepted"},
        {temaDocumentoRechazado_, "get/rejected"},
        {temaActualizacionRechazada_, "update/rejected"},
    };
    for (const Tema& tema : temas) {
        const int escritos = snprintf(tema.destino, TamanoTema, "$aws/things/%s/shadow/%s",
                                      nombreThing_, tema.sufijo);
        if (escritos <= 0 || static_cast<size_t>(escritos) >= TamanoTema) {
            return false;
        }
    }
    return true;
}

void ConexionAwsIot::iniciar() {
    if (!configuracionCompleta()) {
        Serial.println(F("AWS IoT: configuracion incompleta (ConfiguracionAws.h). Modo local."));
        return;
    }
    if (!armarTemas()) {
        Serial.println(F("AWS IoT: nombre de Thing demasiado largo. Modo local."));
        return;
    }

    // Autenticacion mutua: CA de Amazon para validar el servidor y certificado propio.
    transporteSeguro_.setCACert(certificadoCa_);
    transporteSeguro_.setCertificate(certificadoDispositivo_);
    transporteSeguro_.setPrivateKey(clavePrivada_);
    transporteSeguro_.setHandshakeTimeout(TiempoHandshakeTlsS);

    cliente_.begin(endpoint_, puerto_, transporteSeguro_);
    cliente_.setOptions(KeepAliveS, true, TiempoOperacionMqttMs);  // Sesion limpia.
    cliente_.onMessageAdvanced([this](MQTTClient*, char tema[], char datos[], int longitud) {
        recibirMensaje(tema, datos, longitud);
    });
    habilitada_ = true;
    Serial.print(F("AWS IoT: Thing "));
    Serial.print(nombreThing_);
    Serial.println(F("; esperando WiFi y hora valida."));
}

bool ConexionAwsIot::prepararHora() {
    // Sin hora real no se puede validar la vigencia del certificado del servidor.
    if (time(nullptr) >= FechaMinimaValida) {
        if (sincronizandoHora_) {
            Serial.println(F("AWS IoT: hora disponible para validar TLS."));
            sincronizandoHora_ = false;
        }
        return true;
    }

    const unsigned long ahora = millis();
    if (!sincronizandoHora_) {
        if (huboIntento_ && ahora - ultimoIntentoMs_ < IntervaloReintentoMs) {
            return false;
        }
        Serial.println(F("AWS IoT: solicitando hora por NTP."));
        configTime(0, 0, "pool.ntp.org", "time.cloudflare.com");
        inicioSincronizacionMs_ = ahora;
        sincronizandoHora_ = true;
    } else if (ahora - inicioSincronizacionMs_ >= TiempoSincronizacionMs) {
        Serial.println(F("AWS IoT: hora no disponible; TLS aplazado."));
        sincronizandoHora_ = false;
        huboIntento_ = true;
        ultimoIntentoMs_ = ahora;
    }
    return false;
}

void ConexionAwsIot::cerrarConexion() {
    transporteSeguro_.stop();
    lista_ = false;
    huboIntento_ = true;
    ultimoIntentoMs_ = millis();
}

bool ConexionAwsIot::suscribir(const char* tema) {
    if (cliente_.subscribe(tema, 1)) {
        return true;
    }
    Serial.print(F("AWS IoT: no se pudo suscribir a "));
    Serial.println(tema);
    cerrarConexion();
    return false;
}

void ConexionAwsIot::intentarConectar() {
    huboIntento_ = true;
    ultimoIntentoMs_ = millis();
    // El modem-sleep retrasa la llegada del delta; sin el se cumple mejor el tiempo de respuesta.
    WiFi.setSleep(false);
    Serial.println(F("AWS IoT: iniciando conexion TLS mutua y MQTT."));

    // El nombre del endpoint conserva SNI y la validacion del nombre del servidor.
    if (!transporteSeguro_.connect(endpoint_, puerto_, TiempoConexionTcpMs)) {
        Serial.println(F("AWS IoT: fallo TLS/DNS/TCP. Revisar hora, endpoint y certificados."));
        cerrarConexion();
        return;
    }
    transporteSeguro_.setTimeout(1);  // Segundos, para las lecturas posteriores.

    // La politica de IoT exige que el client id sea el nombre del Thing.
    // true omite solo la apertura de red: TLS ya se establecio en connect().
    if (!cliente_.connect(nombreThing_, true)) {
        Serial.print(F("AWS IoT: MQTT rechazado o agotado (revisar politica). Error: "));
        Serial.print(static_cast<int>(cliente_.lastError()));
        Serial.print(F(", codigo: "));
        Serial.println(static_cast<int>(cliente_.returnCode()));
        cerrarConexion();
        return;
    }

    if (!suscribir(temaDelta_) || !suscribir(temaDocumentoAceptado_) ||
        !suscribir(temaDocumentoRechazado_) || !suscribir(temaActualizacionRechazada_)) {
        return;
    }

    // Pedir el Shadow completo: si hay un desired pendiente, llega en state.delta.
    if (!cliente_.publish(temaPedirDocumento_, "", false, 1)) {
        Serial.println(F("AWS IoT: no se pudo pedir el Shadow."));
        cerrarConexion();
        return;
    }

    lista_ = true;
    conexionNueva_ = true;
    Serial.println(F("AWS IoT: conectado; Shadow suscrito y documento solicitado."));
}

bool ConexionAwsIot::estaConectada() {
    return habilitada_ && lista_ && conexionWifi_.estaConectada() && cliente_.connected();
}

bool ConexionAwsIot::seAcabaDeConectar() {
    if (!conexionNueva_ || !estaConectada()) {
        return false;
    }
    conexionNueva_ = false;
    return true;
}

void ConexionAwsIot::actualizar() {
    if (!habilitada_) {
        return;
    }
    if (!conexionWifi_.estaConectada()) {
        if (lista_) {
            Serial.println(F("AWS IoT: WiFi perdido; se reconectara al volver la red."));
            cerrarConexion();
        }
        sincronizandoHora_ = false;
        return;
    }
    if (lista_) {
        if (!cliente_.loop()) {
            Serial.println(F("AWS IoT: conexion perdida. Reintento en 5 s."));
            cerrarConexion();
        }
        return;
    }
    if (!prepararHora()) {
        return;
    }
    if (huboIntento_ && millis() - ultimoIntentoMs_ < IntervaloReintentoMs) {
        return;
    }
    intentarConectar();
}

bool ConexionAwsIot::publicarActualizacion(const char* documento) {
    if (!estaConectada() || cadenaVacia(documento)) {
        return false;
    }
    if (strlen(documento) >= TamanoMensaje) {
        Serial.println(F("AWS IoT: documento demasiado grande; no se publica."));
        return false;
    }
    if (!cliente_.publish(temaActualizar_, documento, false, 1)) {
        Serial.println(F("AWS IoT: fallo de publicacion. Reintento de conexion en 5 s."));
        cerrarConexion();
        return false;
    }
    return true;
}

bool ConexionAwsIot::copiarContenido(MensajeShadow& destino, const char* datos, int longitud) {
    if (datos == nullptr || longitud <= 0 || static_cast<size_t>(longitud) >= TamanoMensaje) {
        return false;
    }
    memcpy(destino.contenido, datos, static_cast<size_t>(longitud));
    destino.contenido[longitud] = '\0';
    return true;
}

void ConexionAwsIot::recibirMensaje(const char* tema, const char* datos, int longitud) {
    // Solo copiar: el procesamiento y cualquier publicacion ocurren fuera del callback.
    MensajeShadow* destino = nullptr;
    bool* hayPendiente = nullptr;
    if (strcmp(tema, temaDelta_) == 0) {
        destino = &deltaPendiente_;
        hayPendiente = &hayDelta_;
    } else if (strcmp(tema, temaDocumentoAceptado_) == 0) {
        destino = &documentoPendiente_;
        hayPendiente = &hayDocumento_;
    } else if (strcmp(tema, temaDocumentoRechazado_) == 0) {
        // 404 en el primer arranque: el Shadow se crea con el primer reporte.
        Serial.println(F("AWS IoT: get rechazado (el Shadow aun no existe o hubo un error)."));
        return;
    } else if (strcmp(tema, temaActualizacionRechazada_) == 0) {
        Serial.print(F("AWS IoT: update rechazado: "));
        if (datos != nullptr && longitud > 0) {
            Serial.write(reinterpret_cast<const uint8_t*>(datos), static_cast<size_t>(longitud));
        }
        Serial.println();
        return;
    } else {
        return;
    }

    // Si el mensaje no entra, se conserva el pendiente anterior del mismo tipo.
    if (copiarContenido(*destino, datos, longitud)) {
        *hayPendiente = true;
    } else {
        Serial.println(F("AWS IoT: mensaje del Shadow vacio o demasiado grande; descartado."));
    }
}

bool ConexionAwsIot::tomarMensaje(MensajeShadow& destino) {
    if (hayDocumento_) {
        destino = documentoPendiente_;
        hayDocumento_ = false;
        return true;
    }
    if (hayDelta_) {
        destino = deltaPendiente_;
        hayDelta_ = false;
        return true;
    }
    return false;
}
