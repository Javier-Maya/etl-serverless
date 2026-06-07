"""
Módulo de transformación de datos.
Combina fechas, normaliza tipos y prepara los datos para la carga.
"""
import logging

import pandas as pd

logger = logging.getLogger(__name__)


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica todas las transformaciones necesarias al DataFrame.

    Args:
        df: DataFrame validado con los datos del CSV.

    Returns:
        DataFrame transformado y listo para cargar en PostgreSQL.
    """
    # TODO: combinar transaction_date + transaction_time en transaction_datetime
    # TODO: normalizar tipos de datos (amount a float, items_count a int)
    # TODO: normalizar strings (strip, lowercase donde corresponda)
    pass