import pandas as pd
import pytest

from src.etl.transformer import combine_datetime, normalize_amounts, normalize_strings, transform


def _make_valid_df() -> pd.DataFrame:
    """Crea un DataFrame válido de prueba para transformaciones."""
    return pd.DataFrame({
        "transaction_id": ["TXN001", "TXN002"],
        "store_id": ["STORE01", "STORE01"],
        "store_name": ["  Tienda Centro  ", "Tienda Centro"],
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


class TestCombineDatetime:

    def test_combine_datetime_creates_transaction_datetime_column(self):
        """combine_datetime debe crear la columna transaction_datetime."""
        # Arrange
        df = _make_valid_df()

        # Act
        result = combine_datetime(df)

        # Assert
        assert "transaction_datetime" in result.columns

    def test_combine_datetime_removes_original_columns(self):
        """combine_datetime debe eliminar transaction_date y transaction_time."""
        # Arrange
        df = _make_valid_df()

        # Act
        result = combine_datetime(df)

        # Assert
        assert "transaction_date" not in result.columns
        assert "transaction_time" not in result.columns

    def test_combine_datetime_result_is_datetime_dtype(self):
        """La columna transaction_datetime debe ser de tipo datetime."""
        # Arrange
        df = _make_valid_df()

        # Act
        result = combine_datetime(df)

        # Assert
        assert pd.api.types.is_datetime64_any_dtype(result["transaction_datetime"])

    def test_combine_datetime_correct_value(self):
        """El valor de transaction_datetime debe corresponder a la fecha y hora originales."""
        # Arrange
        df = _make_valid_df()

        # Act
        result = combine_datetime(df)

        # Assert
        expected = pd.Timestamp("2026-06-06 10:00:00")
        assert result.iloc[0]["transaction_datetime"] == expected

    def test_combine_datetime_does_not_mutate_input(self):
        """combine_datetime no debe modificar el DataFrame original."""
        # Arrange
        df = _make_valid_df()
        original_columns = list(df.columns)

        # Act
        combine_datetime(df)

        # Assert
        assert list(df.columns) == original_columns

    def test_combine_datetime_invalid_format_raises_value_error(self):
        """Fechas con formato inválido deben lanzar ValueError."""
        # Arrange
        df = _make_valid_df()
        df.loc[0, "transaction_date"] = "06/06/2026"

        # Act / Assert
        with pytest.raises(ValueError):
            combine_datetime(df)


class TestNormalizeAmounts:

    def test_normalize_amounts_converts_amount_to_float(self):
        """normalize_amounts debe convertir amount a float64."""
        # Arrange
        df = _make_valid_df()
        df["amount"] = df["amount"].astype(str)

        # Act
        result = normalize_amounts(df)

        # Assert
        assert result["amount"].dtype == float

    def test_normalize_amounts_converts_items_count_to_int(self):
        """normalize_amounts debe convertir items_count a int64."""
        # Arrange
        df = _make_valid_df()

        # Act
        result = normalize_amounts(df)

        # Assert
        assert result["items_count"].dtype == int

    def test_normalize_amounts_does_not_mutate_input(self):
        """normalize_amounts no debe modificar el DataFrame original."""
        # Arrange
        df = _make_valid_df()
        df["amount"] = df["amount"].astype(str)
        original_dtype = df["amount"].dtype

        # Act
        normalize_amounts(df)

        # Assert
        assert df["amount"].dtype == original_dtype


class TestNormalizeStrings:

    def test_normalize_strings_strips_leading_trailing_whitespace(self):
        """normalize_strings debe eliminar espacios al inicio y al final de strings."""
        # Arrange
        df = _make_valid_df()

        # Act
        result = normalize_strings(df)

        # Assert
        assert result.iloc[0]["store_name"] == "Tienda Centro"

    def test_normalize_strings_does_not_modify_clean_values(self):
        """normalize_strings no debe modificar strings que ya están limpios."""
        # Arrange
        df = _make_valid_df()

        # Act
        result = normalize_strings(df)

        # Assert
        assert result.iloc[1]["store_name"] == "Tienda Centro"

    def test_normalize_strings_does_not_mutate_input(self):
        """normalize_strings no debe modificar el DataFrame original."""
        # Arrange
        df = _make_valid_df()
        original_value = df.iloc[0]["store_name"]

        # Act
        normalize_strings(df)

        # Assert
        assert df.iloc[0]["store_name"] == original_value


class TestTransform:

    def test_transform_returns_dataframe(self):
        """transform debe retornar un DataFrame."""
        # Arrange
        df = _make_valid_df()

        # Act
        result = transform(df)

        # Assert
        assert isinstance(result, pd.DataFrame)

    def test_transform_produces_transaction_datetime_column(self):
        """El pipeline completo debe generar transaction_datetime."""
        # Arrange
        df = _make_valid_df()

        # Act
        result = transform(df)

        # Assert
        assert "transaction_datetime" in result.columns
        assert "transaction_date" not in result.columns
        assert "transaction_time" not in result.columns

    def test_transform_preserves_row_count(self):
        """transform no debe eliminar ni duplicar filas."""
        # Arrange
        df = _make_valid_df()

        # Act
        result = transform(df)

        # Assert
        assert len(result) == len(df)