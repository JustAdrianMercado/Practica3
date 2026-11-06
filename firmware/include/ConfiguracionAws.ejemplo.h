#pragma once

// Copiar a ConfiguracionAws.h y completar SOLO la copia local ignorada por Git.
// Nunca versionar el certificado del dispositivo ni su clave privada.
// Endpoint vacio: la conexion con AWS IoT queda deshabilitada y el resto del firmware funciona.

// IoT Core -> Settings -> Device data endpoint (termina en -ats.iot.us-east-1.amazonaws.com).
constexpr char EndpointAwsIot[] = "";
constexpr unsigned short PuertoAwsIot = 8883;  // MQTT sobre TLS con autenticacion mutua.

// Nombre exacto del Thing; tambien se usa como client id MQTT (lo exige la politica de IoT).
constexpr char NombreThing[] = "caja-enigmas-01";

// Pegar cada PEM completo entre R"PEM( y )PEM", incluidas las lineas BEGIN y END.
// CA publica de Amazon: https://www.amazontrust.com/repository/AmazonRootCA1.pem
constexpr char CertificadoCaAmazon[] = R"PEM()PEM";

// Archivo xxxx-certificate.pem.crt descargado al crear el Thing.
constexpr char CertificadoDispositivo[] = R"PEM()PEM";

// Archivo xxxx-private.pem.key descargado al crear el Thing. SECRETO.
constexpr char ClavePrivadaDispositivo[] = R"PEM()PEM";
