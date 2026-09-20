PIX_TRANSACTIONS = [
    {
        "transaction_id": "PIX001",
        "amount": 150.00,
        "status": "COMPLETED",
    },
    {
        "transaction_id": "PIX002",
        "amount": 75.50,
        "status": "PROCESSING",
    },
    {
        "transaction_id": "PIX003",
        "amount": 320.00,
        "status": "FAILED",
    },
]

PIX_LIMIT = 5000.00


def get_pix_transaction(transaction_id: str) -> dict | None:
    for transaction in PIX_TRANSACTIONS:
        if transaction["transaction_id"] == transaction_id:
            return transaction

    return None


def get_pix_limit() -> float:
    return PIX_LIMIT