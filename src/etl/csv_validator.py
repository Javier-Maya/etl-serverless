import logging

import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

REQUIRED_COLUMNS = [
    "transaction_id",
    "store_id",
    "store_name",
    "terminal_id",
    "transaction_date",
    "transaction_time",
    "card_type",
    "amount",
    "currency",
    "status",
    "product_category",
    "items_count",
]

REJECTION_REASON_COLUMN = "rejection_reason"


def validate_schema(df: pd.DataFrame) -> bool:
    """
    Valida que el DataFrame contenga todas las columnas requeridas.

    Realiza validación estructural del archivo: verifica que existan
    las columnas esperadas antes de procesar cualquier registro.

    Args:
        df: DataFrame con los datos del archivo CSV recibido.

    Returns:
        True si todas las columnas requeridas están presentes, False si no.

    Raises:
        ValueError: Si el DataFrame está vacío.

    Example:
        >>> validate_schema(df)
        True
    """
    if df.empty:
        raise ValueError("El DataFrame no puede estar vacío.")

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing_columns:
        logger.warning(
            "Schema inválido — columnas faltantes",
            extra={"missing_columns": missing_columns},
        )
        return False

    return True


def validate_records(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Valida los registros del DataFrame y los separa en válidos y rechazados.

    Registros con status DECLINED son considerados válidos: son transacciones
    rechazadas por el emisor de la tarjeta, no errores de datos.

    Reglas de rechazo:
    - transaction_id nulo o vacío (impide deduplicación)
    - amount nulo o no numérico
    - amount negativo
    - items_count nulo o no numérico

    Args:
        df: DataFrame con los datos del CSV, ya validado en schema.

    Returns:
        Tupla (valid_df, rejected_df). El rejected_df incluye la columna
        'rejection_reason' con el motivo del rechazo de cada fila.

    Raises:
        ValueError: Si el DataFrame está vacío.

    Example:
        >>> valid_df, rejected_df = validate_records(df)
        >>> len(rejected_df)
        0
    """
    if df.empty:
        raise ValueError("El DataFrame no puede estar vacío.")

    rejection_reasons = pd.Series("", index=df.index, dtype=str)

    # Validar transaction_id: requerido para deduplicación en DB
    null_id_mask = df["transaction_id"].isnull() | (
        df["transaction_id"].astype(str).str.strip() == ""
    )
    rejection_reasons[null_id_mask] = "transaction_id nulo o vacío"

    # Validar amount: debe ser numérico y no negativo
    amount_numeric = pd.to_numeric(df["amount"], errors="coerce")
    invalid_amount_mask = amount_numeric.isna() & ~null_id_mask
    rejection_reasons[invalid_amount_mask] = "amount nulo o no numérico"

    already_rejected = null_id_mask | invalid_amount_mask
    negative_amount_mask = (amount_numeric < 0) & ~already_rejected
    rejection_reasons[negative_amount_mask] = "amount negativo"

    # Validar items_count: debe ser numérico
    already_rejected = already_rejected | negative_amount_mask
    items_numeric = pd.to_numeric(df["items_count"], errors="coerce")
    invalid_items_mask = items_numeric.isna() & ~already_rejected
    rejection_reasons[invalid_items_mask] = "items_count nulo o no numérico"

    rejection_mask = rejection_reasons != ""

    valid_df = df[~rejection_mask].copy()
    rejected_df = df[rejection_mask].copy()
    rejected_df[REJECTION_REASON_COLUMN] = rejection_reasons[rejection_mask]

    logger.info(
        "Validación de registros completada",
        extra={
            "total_rows": len(df),
            "valid_rows": len(valid_df),
            "rejected_rows": len(rejected_df),
        },
    )

    return valid_df, rejected_df