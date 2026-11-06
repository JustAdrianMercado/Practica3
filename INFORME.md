# Informe técnico — Práctica 3: Caja de los Enigmas

**Integración de un objeto inteligente con Alexa mediante MQTT y AWS IoT Core**

SIS-234 · Ingeniería de Sistemas · Grupo: Santiago Torres, Adrián Mercado, Mateo Rojas y Lucía Escobar

> Esqueleto del informe (§4.2 de la [consigna](docs/consigna/Práctica_3.md)). Cada sección indica quién la redacta; Lucía coordina y unifica el estilo. Borrar las notas entre corchetes al completar cada sección.

## 1. Caso de Uso y Requerimientos

### 1.1 Caso de uso *(Lucía, Santiago)*
[Caja de los Enigmas: módulo de cerradura por voz y su relación con el proyecto final.]

### 1.2 Justificación del sensor y del actuador *(Santiago)*
[Reed switch y servo SG90: por qué, rango de trabajo, tensión ≤12 V, por qué no un LED ni el ultrasónico.]

### 1.3 Requerimientos funcionales *(Lucía)*
[RF1–RF9 con su criterio de aceptación.]

### 1.4 Requerimientos no funcionales *(Lucía, Adrián)*
[Estabilidad, exactitud, tiempo de respuesta, frecuencia de reporte justificada, reconexión, seguridad: valores declarados y medibles.]

## 2. Análisis y Diseño

### 2.1 Arquitectura del sistema *(Adrián)*
### 2.2 Diagrama de circuito *(Santiago)*
### 2.3 Diagrama de clases del objeto inteligente *(Adrián, Santiago)*
### 2.4 Diagrama de clases de la función Lambda *(Mateo)*
### 2.5 Diagramas de secuencia *(Lucía, Mateo)*
[Como mínimo: vinculación de un Thing, consulta del sensor y comando sobre el actuador, desde el usuario hasta el objeto inteligente.]
### 2.6 Especificación del documento Shadow *(Adrián)*
[Atributos, tipos, valores válidos y uso de `desired`, `reported` y `delta`; basada en [docs/contratos.md](docs/contratos.md).]
### 2.7 Diseño del mecanismo de vinculación *(Mateo)*
### 2.8 Diseño de la skill de Alexa *(Lucía)*
[Nombre de invocación, intents, slots y frases de ejemplo.]
### 2.9 Matriz de trazabilidad *(Lucía)*
[Cada RF/RNF → diseño → código → prueba.]

## 3. Desarrollo e Implementación

### 3.1 Estructura del código del objeto inteligente *(Adrián, Santiago)*
### 3.2 Estructura del código de la función Lambda *(Mateo)*
### 3.3 Configuración de AWS IoT Core: Thing, certificados y política *(Adrián)*
### 3.4 Configuración de Lambda, DynamoDB y rol IAM, con la justificación de los permisos *(Mateo)*
### 3.5 Configuración de Alexa: modelo de interacción y vinculación con la Lambda *(Lucía)*
### 3.6 Montaje *(Santiago)*

## 4. Pruebas y Validaciones

### 4.1 Plan de pruebas y procedimiento *(Lucía)*
### 4.2 Pruebas funcionales y de frases de la skill *(Lucía, Mateo)*
### 4.3 Estabilidad *(Santiago, Adrián)*
### 4.4 Exactitud del sensor *(Santiago)*
### 4.5 Tiempo de respuesta extremo a extremo *(Santiago, Lucía)*
### 4.6 Frecuencia de reporte *(Adrián)*
### 4.7 Reconexión y sincronización del estado `desired` pendiente *(Adrián)*
### 4.8 Incidencias y análisis de errores *(todos)*

## 5. Resultados *(Lucía)*

## 6. Conclusiones *(Lucía, todos)*

## 7. Recomendaciones *(Lucía, todos)*
[Incluir extensiones hacia el Escape Room: acertijos, desafíos, más sensores y actuadores.]

## 8. Anexos

### 8.1 Diagramas y esquemas
### 8.2 Fotografías y evidencias de las pruebas
### 8.3 Configuraciones exportadas
### 8.4 Aportes de cada integrante
