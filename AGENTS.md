# Instrucciones para agentes de IA (Codex, Claude Code, etc.)

Repositorio de la Práctica 3 de SIS-234: **Caja de los Enigmas**, un objeto inteligente con ESP32 integrado con Alexa mediante AWS IoT Core (Device Shadow), AWS Lambda (Python) y DynamoDB.

## Reglas del proyecto (tienen prioridad sobre las reglas de AWS de abajo)

- Antes de cambiar el firmware, la Lambda o la skill, leer [docs/contratos.md](docs/contratos.md): nombres del Shadow, temas MQTT, tabla, intents y pines. Si un cambio afecta un contrato, se actualiza ese archivo en el mismo PR.
- Plan y reparto de tareas: [docs/planificacion/](docs/planificacion/00-resumen.md).
- Región **us-east-1** para todo; perfil de AWS CLI del grupo: `caja-enigmas` (el usuario IAM de cada integrante).
- Los recursos de AWS se configuran desde la consola, porque así lo documenta el informe, y sus definiciones se exportan a `config/`. No migrar a CDK ni a CloudFormation salvo que el grupo lo pida.
- **Nunca** versionar certificados, la clave privada del Thing, credenciales WiFi ni access keys de AWS. Viven en `firmware/include/Configuracion*.h` (sin `.ejemplo`) o en `certificados-privados/`, que están en `.gitignore`.
- Código modular y orientado a objetos, con comentarios y documentación en español; C++ en el estilo del firmware existente y PEP 8 en Python.
- Cada integrante hace commits con su propia cuenta de GitHub, en su rama, e integra a `main` mediante PR.

## Uso de AWS por agentes: solo lectura salvo excepciones

El servidor `aws-mcp` y la AWS CLI tienen acceso a toda la cuenta del grupo. **Todo lo que se crea, modifica o borra en AWS lo hace una persona del grupo, a mano, desde la consola.** El agente sirve para **revisar** que lo hecho a mano esté bien.

**Permitido sin preguntar (solo lectura):** operaciones `Describe*`, `Get*`, `List*`, `Search*` y `Query`/`Scan` de solo lectura, por ejemplo:
- comprobar que un Thing existe y tiene su certificado y su política asociados;
- leer el Shadow de un Thing;
- revisar la configuración de la Lambda (runtime, variables de entorno, rol, disparador de Alexa);
- revisar los permisos efectivos del rol IAM y la política de IoT frente a `docs/contratos.md`;
- revisar la definición de la tabla de DynamoDB y sus ítems;
- leer los logs de CloudWatch para diagnosticar errores;
- consultar costos y el estado de la capa gratuita.

Al terminar una revisión, informar qué se comprobó, qué está bien y qué hay que corregir **a mano**, con los pasos en la consola. No corregirlo por cuenta propia.

**Excepciones (escrituras que se pueden hacer):** solo si un integrante las pide de forma explícita en la conversación, nombrando la acción. El agente describe antes el comando exacto y el recurso afectado, y espera la confirmación:
- `iot-data update-thing-shadow` y publicaciones MQTT de prueba sobre los Shadows `caja-enigmas-NN`;
- `lambda invoke` de `caja-enigmas-skill` con un evento de prueba;
- `lambda update-function-code` de `caja-enigmas-skill` con el zip generado desde `lambda/`;
- poner o borrar ítems de prueba en `CajaEnigmasVinculaciones`.

**Prohibido siempre, aunque se pida:** crear, modificar o borrar usuarios, roles o políticas de IAM; crear, desactivar o borrar certificados o políticas de IoT; borrar Things, tablas, funciones o logs; crear access keys; cambiar la facturación, los presupuestos o la configuración de la cuenta; crear recursos fuera de us-east-1. Estas acciones las hace una persona desde la consola.

Si una regla de AWS de abajo dice lo contrario (por ejemplo, preferir infraestructura como código o desplegar recursos), manda esta sección.

<!-- BEGIN AWS Agent Toolkit rules -->
# AWS Guidance

- Where these AWS rules conflict with the project's own instructions, the
  project's instructions take precedence.
- Prefer the AWS MCP Server for AWS interactions — it provides sandboxed
  execution, observability, and audit logging. If unavailable, use the
  AWS CLI directly.
- For any AWS task or question — building, configuring, migrating, debugging,
  or operating a service, writing SDK code, authoring CDK/CloudFormation, or
  answering how a service works — first call `aws___search_documentation` with
  topic `agent_skills` and load the matching skill with `aws___retrieve_skill`.
  Do this even when you believe you know the answer: skills carry current
  service behavior that your training may not. Prefer the skill's guidance over
  general knowledge. Skip it only for work that does not involve AWS.
- When uncertain about specific AWS details (API parameters, permissions,
  limits, error codes), verify against documentation rather than guessing.
  State uncertainty explicitly if you cannot confirm.
- Before reporting a count, a total, or that something does not exist, read
  every page of the results and search every Region and scope where it could
  be. If you could not, say the result is partial and name what you checked.
- To say what a system currently does, read what the runtime uses: the
  completed deployment, the alias or version that is invoked, the template the
  stack is running. A newer stored version, a draft, or a description field is
  not evidence of live behavior.
- Present a cause as confirmed only if data, configuration, or logs you read
  show it. Label anything else as unverified, and say what you would check
  next.
- Before you interpret the records that show a failure, such as error log
  lines, failed executions, or table items, read one of them whole, with
  every field. Don't truncate messages or select fields in your own code
  until you have.
- When an error says a value was undefined, null, empty, or missing, find
  the input, query result, or item that supplied that value. If the account
  shows why it was empty, such as no item matching the key, read that
  before you call the cause unverified.
- When a field in a record you read explains the result, such as an error
  counter, an empty array, a null, or a state value, name the field and its
  exact value in the answer, and say which record it came from.
- When the user asks a specific question or names a suspected cause, confirm
  or rule out each cause they raised, and do not offer alternatives your evidence
  does not support.
- When creating infrastructure, prefer infrastructure-as-code (AWS CDK or
  CloudFormation) over direct CLI commands.
- When working with infrastructure, follow AWS Well-Architected Framework
  principles.
- Do not use em dashes in AWS resource names or descriptions. Use
  hyphens instead.

## Before you conclude

- Before deciding the AWS account can't hold what the request asks for,
  look. List the places it could live, such as S3 buckets, databases, and
  log groups, and read what is there.
- Don't conclude that records are missing from metadata, such as a
  creation date or a stored-bytes count, or from one query that failed or
  came back empty. Read the records another way, across the full time
  range, before reporting them absent.
- A tool's own error is evidence. If a call the answer depends on fails
  with expired or missing credentials or AccessDenied, report that error
  and what it blocks, and don't overrule it with another check. Searching
  other Regions is for finding resources, not for retrying an auth error.
  Retry throttling with backoff before you report it.

## Secret Safety

- MUST load the `aws-secrets-manager` skill first for any secret,
  credential, API key, token, or password task. MUST NOT call
  `secretsmanager get-secret-value` or `batch-get-secret-value`, and MUST
  NOT hit the Secrets Manager Agent daemon directly. MUST use
  `{{resolve:secretsmanager:secret-id:SecretString:json-key}}` with
  `asm-exec` so the secret resolves at runtime without entering context.
<!-- END AWS Agent Toolkit rules -->
