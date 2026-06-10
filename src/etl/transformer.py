import logging

import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

STRING_COLUMNS = [
    "transaction_id",
    "store_id",
    "store_name",
    "terminal_id",
    "card_type",
    "currency",
    "status",
    "product_category",
]

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def combine_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """
    Combina transaction_date y transaction_time en una sola columna transaction_datetime.

    Las columnas originales se eliminan tras la combinación. Formato
    esperado: fecha 'YYYY-MM-DD', hora 'HH:MM:SS'.

    Args:
        df: DataFrame con columnas transaction_date y transaction_time separadas.

    Returns:
        DataFrame con la columna transaction_datetime agregada y las columnas
        transaction_date y transaction_time eliminadas.

    Raises:
        ValueError: Si alguna fila tiene formato de fecha u hora inválido.

    Example:
        >>> result = combine_datetime(df)
        >>> "transaction_datetime" in result.columns
        True
    """
    df = df.copy()
    combined = df["transaction_date"].astype(str) + " " + df["transaction_time"].astype(str)

    try:
        df["transaction_datetime"] = pd.to_datetime(combined, format=DATETIME_FORMAT)
    except ValueError as e:
        raise ValueError(f"Formato de fecha u hora inválido: {e}") from e

    df = df.drop(columns=["transaction_date", "transaction_time"])

    logger.info("Columnas de fecha combinadas en transaction_datetime")

    return df


def normalize_amounts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte amount a float64 e items_count a int64.

    Args:
        df: DataFrame con columnas amount e items_count.

    Returns:
        DataFrame con amount como float64 e items_count como int64.

    Example:
        >>> result = normalize_amounts(df)
        >>> result["amount"].dtype
        dtype('float64')
    """
    df = df.copy()
    df["amount"] = pd.to_numeric(df["amount"], errors="raise").astype(float)
    df["items_count"] = pd.to_numeric(df["items_count"], errors="raise").astype(int)
    return df


def normalize_strings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina espacios en blanco al inicio y al final de las columnas de texto.

    Args:
        df: DataFrame con columnas de texto a normalizar.

    Returns:
        DataFrame con columnas de texto sin espacios extremos.

    Example:
        >>> result = normalize_strings(df)
        >>> result.iloc[0]["store_name"]
        'Tienda Centro'
    """
    df = df.copy()
    for col in STRING_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Orquesta todas las transformaciones del DataFrame.

    Aplica en orden: normalización de strings, normalización de tipos
    numéricos y combinación de columnas de fecha y hora.

    Args:
        df: DataFrame con los datos del CSV, ya validados.

    Returns:
        DataFrame transformado y listo para carga en base de datos.

    Example:
        >>> result = transform(df)
        >>> "transaction_datetime" in result.columns
        True
    """
    logger.info("Inicio de transformaciones", extra={"input_rows": len(df)})

    df = normalize_strings(df)
    df = normalize_amounts(df)
    df = combine_datetime(df)

    logger.info("Transformaciones completadas", extra={"output_rows": len(df)})

    return df