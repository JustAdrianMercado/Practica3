# Documentación de la Caja de los Enigmas

El [informe técnico](../INFORME.md) es la referencia principal del proyecto.
Describe la implementación, las pruebas y sus límites de medición.

| Material complementario | Finalidad |
|---|---|
| [Consigna original](consigna/Práctica_3.md) | Entregables del apartado 4.2 y rúbrica del 5.2. Se conserva íntegra. |
| [Contratos](contratos.md) | Nombres MQTT, Shadow, tabla, intents y pines compartidos. |
| [Configuración inicial de AWS IoT](configuracion-aws-iot.md) | Procedimiento de consola; no es una auditoría actual de permisos de usuarios. |
| [Montaje](GUIA_MONTAJE.md) | Cableado realizado, parámetros del hardware y uso de diagnósticos. |
| [Plan de pruebas de frases](PLAN_PRUEBAS.md) | Las 48 frases reales del modelo y su validación manual reportada. |
| [Protocolos de medición](PRUEBAS_FISICAS.md) | Métodos reproducibles para obtener medidas; separados de los resultados del informe. |
| [Backend Lambda](backend-lambda.md) | Auditoría histórica, datos únicos del paquete y receta de mantenimiento. |
| [Guía de defensa](GUIA_DEFENSA.md) | Recorrido del código y explicación individual del backend de Mateo. |
| [Circuito](diagramas/circuito.svg) | Esquema funcional del montaje entregado. Los otros diagramas están en el informe. |
| [Evidencias y fotografías](../INFORME.md#82-fotografías-y-evidencias) | Catálogo de imágenes existentes con su alcance. |
| [Planificación original](planificacion/00-resumen.md) | Reparto de responsabilidades y cronograma histórico; no representa el estado final de las pruebas. |

Las configuraciones exportadas permanecen en [config/aws](../config/aws) y
[config/alexa](../config/alexa). Las fotografías conservan sus archivos
originales y las capturas de AWS se publican en sus copias preparadas para el
informe. Los datos privados y artefactos de despliegue generados se mantienen
fuera de los archivos versionados.
