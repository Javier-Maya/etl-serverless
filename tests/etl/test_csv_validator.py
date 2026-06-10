import pandas as pd
import pytest

from src.etl.csv_validator import validate_schema, validate_records


def _make_valid_df() -> pd.DataFrame:
    """Crea un DataFrame válido de prueba con todos los campos requeridos."""
    return pd.DataFrame({
        "transaction_id": ["TXN001", "TXN002"],
        "store_id": ["STORE01", "STORE01"],
        "store_name": ["Tienda Centro", "Tienda Centro"],
        "terminal_id": ["TERM01", "TERM01"],
        "transaction_date": ["2026-06-06", "2026-06-06"],
        "transaction_time": ["10:00:00", "11:00:00"],
        "card_type": ["VISA", "MASTERCARD"],
        "amount": [15000.0, 8500.0],
        "currency": ["CLP", "CLP"],
        "status": ["APPROVED", "DECLINED"],
        "product_category": ["FOOD", "ELECTRONICS"],
        "items_count": [2, 1],
    })


class TestValidateSchema:

    def test_validate_schema_valid_df_returns_true(self):
        """Con todas las columnas requeridas, validate_schema retorna True."""
        # Arrange
        df = _make_valid_df()

        # Act
        result = validate_schema(df)

        # Assert
        assert result is True

    def test_validate_schema_missing_column_returns_false(self):
        """Si falta una columna requerida, validate_schema retorna False."""
        # Arrange
        df = _make_valid_df().drop(columns=["amount"])

        # Act
        result = validate_schema(df)

        # Assert
        assert result is False

    def test_validate_schema_extra_column_does_not_affect_result(self):
        """Columnas adicionales no deben afectar la validación del schema."""
        # Arrange
        df = _make_valid_df()
        df["columna_extra"] = "valor"

        # Act
        result = validate_schema(df)

        # Assert
        assert result is True

    def test_validate_schema_empty_df_raises_value_error(self):
        """Un DataFrame vacío debe lanzar ValueError."""
        # Arrange
        df = pd.DataFrame()

        # Act / Assert
        with pytest.raises(ValueError, match="vacío"):
            validate_schema(df)


class TestValidateRecords:

    def test_validate_records_all_valid_returns_empty_rejected(self):
        """Con todos los registros válidos, rejected_df debe estar vacío."""
        # Arrange
        df = _make_valid_df()

        # Act
        valid_df, rejected_df = validate_records(df)

        # Assert
        assert len(valid_df) == 2
        assert len(rejected_df) == 0

    def test_validate_records_declined_status_not_rejected(self):
        """Registros con status DECLINED deben ser válidos — son transacciones legítimas."""
        # Arrange
        df = _make_valid_df()

        # Act
        valid_df, rejected_df = validate_records(df)

        # Assert
        assert "TXN002" in valid_df["transaction_id"].values
        assert len(rejected_df) == 0

    def test_validate_records_null_transaction_id_rejected(self):
        """Filas con transaction_id nulo deben ser rechazadas."""
        # Arrange
        df = _make_valid_df()
        df.loc[0, "transaction_id"] = None

        # Act
        valid_df, rejected_df = validate_records(df)

        # Assert
        assert len(rejected_df) == 1
        assert "transaction_id" in rejected_df.iloc[0]["rejection_reason"]

    def test_validate_records_non_numeric_amount_rejected(self):
        """Filas con amount no numérico deben ser rechazadas."""
        # Arrange
        df = _make_valid_df()
        df["amount"] = df["amount"].astype(object)
        df.loc[0, "amount"] = "no_es_numero"

        # Act
        valid_df, rejected_df = validate_records(df)

        # Assert
        assert len(rejected_df) == 1
        assert "amount" in rejected_df.iloc[0]["rejection_reason"]

    def test_validate_records_negative_amount_rejected(self):
        """Filas con amount negativo deben ser rechazadas."""
        # Arrange
        df = _make_valid_df()
        df.loc[0, "amount"] = -100.0

        # Act
        valid_df, rejected_df = validate_records(df)

        # Assert
        assert len(rejected_df) == 1
        assert "negativo" in rejected_df.iloc[0]["rejection_reason"]

    def test_validate_records_non_numeric_items_count_rejected(self):
        """Filas con items_count no numérico deben ser rechazadas."""
        # Arrange
        df = _make_valid_df()
        df["items_count"] = df["items_count"].astype(object)
        df.loc[0, "items_count"] = "dos"

        # Act
        valid_df, rejected_df = validate_records(df)

        # Assert
        assert len(rejected_df) == 1
        assert "items_count" in rejected_df.iloc[0]["rejection_reason"]

    def test_validate_records_rejected_df_has_rejection_reason_column(self):
        """El DataFrame de rechazados debe incluir la columna rejection_reason."""
        # Arrange
        df = _make_valid_df()
        df.loc[0, "transaction_id"] = None

        # Act
        _, rejected_df = validate_records(df)

        # Assert
        assert "rejection_reason" in rejected_df.columns