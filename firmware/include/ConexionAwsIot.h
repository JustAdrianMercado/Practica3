#pragma once

#include <MQTT.h>
#include <WiFiClientSecure.h>

#include "ConexionWifi.h"

/**
 * MQTT sobre TLS con autenticacion mutua (certificado X.509 del Thing) hacia AWS IoT Core.
 * Usa los temas del Shadow clasico del Thing (ver docs/contratos.md, seccion 3).
 *
 * Se atiende sin bloquear llamando actualizar() en cada vuelta de loop(). Los mensajes del
 * Shadow se copian en el callback y la aplicacion los retira con tomarMensaje(): nunca se
 * publica desde el callback, porque la biblioteca puede estar esperando un ACK.
 */
class ConexionAwsIot {
public:
    static constexpr size_t TamanoMensaje = 2048;  // get/accepted incluye estado y metadatos.

    enum class TipoMensaje : uint8_t {
        Delta,             // update/delta: cambios de desired que difieren de reported.
        DocumentoCompleto  // get/accepted: Shadow completo pedido al conectar.
    };

    struct MensajeShadow {
        TipoMensaje tipo;
        char contenido[TamanoMensaje];  // JSON terminado en cero.
    };

    // Las cadenas deben seguir existiendo durante toda la vida del objeto.
    ConexionAwsIot(ConexionWifi& conexionWifi, const char* endpoint, unsigned short puerto,
                   const char* nombreThing, const char* certificadoCa,
                   const char* certificadoDispositivo, const char* clavePrivada);

    void iniciar();
    void actualizar();
    bool estaConectada();

    // true una sola vez por cada conexion nueva: momento de enviar el reporte completo.
    bool seAcabaDeConectar();

    // Publica un documento {"state":{"reported":{...}}} en el tema update del Shadow.
    bool publicarActualizacion(const char* documento);

    // Entrega un mensaje del Shadow pendiente: primero el documento completo, luego el delta.
    // Si llega un mensaje antes de retirar el anterior del mismo tipo, se conserva el ultimo.
    bool tomarMensaje(MensajeShadow& destino);

private:
    static constexpr unsigned long IntervaloReintentoMs = 5000UL;
    static constexpr unsigned long TiempoSincronizacionMs = 10000UL;
    static constexpr size_t TamanoTema = 160;

    ConexionWifi& conexionWifi_;
    const char* endpoint_;
    const unsigned short puerto_;
    const char* nombreThing_;
    const char* certificadoCa_;
    const char* certificadoDispositivo_;
    const char* clavePrivada_;

    WiFiClientSecure transporteSeguro_;
    MQTTClient cliente_{static_cast<int>(TamanoMensaje + TamanoTema)};

    char temaActualizar_[TamanoTema] = {};
    char temaDelta_[TamanoTema] = {};
    char temaPedirDocumento_[TamanoTema] = {};
    char temaDocumentoAceptado_[TamanoTema] = {};
    char temaDocumentoRechazado_[TamanoTema] = {};
    char temaActualizacionRechazada_[TamanoTema] = {};

    MensajeShadow documentoPendiente_ = {TipoMensaje::DocumentoCompleto, {}};
    MensajeShadow deltaPendiente_ = {TipoMensaje::Delta, {}};
    bool hayDocumento_ = false;
    bool hayDelta_ = false;

    bool habilitada_ = false;
    bool lista_ = false;
    bool conexionNueva_ = false;
    bool huboIntento_ = false;
    bool sincronizandoHora_ = false;
    unsigned long ultimoIntentoMs_ = 0;
    unsigned long inicioSincronizacionMs_ = 0;

    bool configuracionCompleta() const;
    bool armarTemas();
    bool prepararHora();
    void intentarConectar();
    bool suscribir(const char* tema);
    void cerrarConexion();
    void recibirMensaje(const char* tema, const char* datos, int longitud);
    static bool copiarContenido(MensajeShadow& destino, const char* datos, int longitud);
};
