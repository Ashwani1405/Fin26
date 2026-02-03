from datetime import date
from decimal import Decimal

from app.services.data_processing import compute_monthly_cashflow
from app.models.database_schema import Transaction, TransactionDirection


def assert_almost_equal(a, b, tol=1e-6):
    """Safe numeric comparison for ML-style outputs."""
    assert abs(float(a) - float(b)) < tol, f"{a} != {b}"


def test_monthly_cashflow_computation():
    print("🔍 Testing Monthly Cashflow Computation...")

    # --------------------
    # Arrange (Mock Data)
    # --------------------
    transactions = [
        Transaction(
            transaction_date=date(2024, 1, 5),
            amount=Decimal("5000"),
            direction=TransactionDirection.INCOME,
        ),
        Transaction(
            transaction_date=date(2024, 1, 10),
            amount=Decimal("150"),
            direction=TransactionDirection.EXPENSE,
        ),
        Transaction(
            transaction_date=date(2024, 1, 25),
            amount=Decimal("1200"),
            direction=TransactionDirection.EXPENSE,
        ),
        Transaction(
            transaction_date=date(2024, 2, 1),
            amount=Decimal("3000"),
            direction=TransactionDirection.INCOME,
        ),
        Transaction(
            transaction_date=date(2024, 2, 14),
            amount=Decimal("200"),
            direction=TransactionDirection.EXPENSE,
        ),
    ]

    # --------------------
    # Act
    # --------------------
    df = compute_monthly_cashflow(transactions)

    print("\n📊 Computed DataFrame:")
    print(df)

    # --------------------
    # Assert (Structure)
    # --------------------
    expected_columns = {
        "month",
        "total_income",
        "total_expense",
        "net_cashflow",
    }
    assert set(df.columns) == expected_columns, "Unexpected DataFrame schema"
    assert len(df) == 2, "Expected 2 months of data"

    # --------------------
    # Assert (January 2024)
    # --------------------
    jan = df.loc[df["month"] == "2024-01"].iloc[0]
    assert_almost_equal(jan["total_income"], 5000)
    assert_almost_equal(jan["total_expense"], 1350)
    assert_almost_equal(jan["net_cashflow"], 3650)

    # --------------------
    # Assert (February 2024)
    # --------------------
    feb = df.loc[df["month"] == "2024-02"].iloc[0]
    assert_almost_equal(feb["total_income"], 3000)
    assert_almost_equal(feb["total_expense"], 200)
    assert_almost_equal(feb["net_cashflow"], 2800)

    print("\n✅ SUCCESS: Monthly cashflow logic verified")


if __name__ == "__main__":
    test_monthly_cashflow_computation()
