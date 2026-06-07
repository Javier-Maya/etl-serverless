"""
Módulo principal de la Lambda function ETL.
Orquesta el flujo completo: validación, transformación y carga de datos.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event: dict, context: Any) -> dict:
    """
    Procesa un archivo CSV de transacciones recibido desde S3.

    Args:
        event: Evento S3 con información del archivo recibido.
        context: Contexto de ejecución Lambda (timeout, función, etc).

    Returns:
        dict con statusCode 200 si el proceso fue exitoso.

    Raises:
        Exception: Relanza cualquier error no recuperable para que
                   Lambda lo registre en CloudWatch.
    """
    logger.info("Inicio de ejecución", extra={"event": event})

    try:
        # TODO: extraer bucket y key del evento S3
        # TODO: leer CSV desde S3
        # TODO: validar schema con csv_validator
        # TODO: transformar datos con transformer
        # TODO: cargar datos con db_client
        # TODO: mover archivo a processed/ o failed/
        pass

    except Exception as e:
        logger.error("Error en ejecución", extra={"error": str(e)})
        raise

    logger.info("Fin de ejecución")
    return {"statusCode": 200, "body": "OK"}