# Backend de la skill Caja de los Enigmas

Implementación Python de **Mateo Rojas** para AWS Lambda, región `us-east-1`.
Punto de entrada: `lambda_function.lambda_handler`; runtime objetivo Python 3.12.

- `lambda_function.py`: compone clientes, servicios y manejadores con `crear_skill`.
- `manejadores/`: solicitudes de Alexa; `servicios/`: DynamoDB y Shadow.
- `textos.py`: respuestas compartidas; `tests/`: suite local con AWS simulado.
- [requirements.txt](requirements.txt): rangos de dependencias de desarrollo.
- [requirements-despliegue.txt](requirements-despliegue.txt): versiones fijadas
  del paquete verificado.

Variables: `TABLA_VINCULACIONES`, `PREFIJO_THING` e `IOT_ENDPOINT`.
El backend usa el rol de ejecución; no se incluyen credenciales personales.

Desde la raíz, con dependencias instaladas:

```powershell
python -m unittest discover -s lambda/tests -v
```

Diseño y resultados: [INFORME.md](../INFORME.md).
Auditoría, paquete y receta de mantenimiento:
[backend-lambda.md](../docs/backend-lambda.md).
Preparación de la defensa: [GUIA_DEFENSA.md](../docs/GUIA_DEFENSA.md).
