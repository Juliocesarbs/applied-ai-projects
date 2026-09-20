ACCOUNT_DATA = {
    "balance": 2450.00,
    "transactions": [
        "PIX - R$ 150.00",
        "Supermercado - R$ 320.50",
        "Salário + R$ 4500.00",
    ],
}


def get_account_balance() -> float:
    return ACCOUNT_DATA["balance"]


def get_account_transactions() -> list[str]:
    return ACCOUNT_DATA["transactions"]