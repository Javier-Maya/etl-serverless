import logging
from typing import Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event: dict, context: Any) -> dict:
    """
    Punto de entrada de la Lambda. Recibe el evento S3 y orquesta el flujo ETL.

    Args:
        event: Evento S3 con los registros de los objetos creados.
        context: Contexto de ejecución Lambda (timeout, memoria, etc).

    Returns:
        dict con statusCode 200 si el proceso fue exitoso.

    Raises:
        Exception: Relanza cualquier error no recuperable para que
                   Lambda lo registre en CloudWatch.
    """
    logger.info("Inicio de ejecución Lambda")

    try:
        for record in event.get("Records", []):
            bucket_name = record["s3"]["bucket"]["name"]
            object_key = record["s3"]["object"]["key"]

            logger.info(
                "Archivo recibido desde S3",
                extra={
                    "bucket": bucket_name,
                    "key": object_key,
                }
            )

            # TODO Día 4: llamar a csv_validator, transformer, db_client

    except Exception as e:
        logger.error("Error en ejecución", extra={"error": str(e)})
        raise

    logger.info("Fin de ejecución Lambda")
    return {"statusCode": 200, "body": "OK"}