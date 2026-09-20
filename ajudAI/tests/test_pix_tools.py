from src.tools.pix_tools import get_pix_limit, get_pix_transaction


def test_get_existing_pix_transaction() -> None:
    transaction = get_pix_transaction("PIX002")

    assert transaction is not None
    assert transaction["transaction_id"] == "PIX002"
    assert transaction["amount"] == 75.50
    assert transaction["status"] == "PROCESSING"


def test_get_non_existing_pix_transaction() -> None:
    transaction = get_pix_transaction("PIX999")

    assert transaction is None


def test_get_pix_limit() -> None:
    limit = get_pix_limit()

    assert limit == 5000.00