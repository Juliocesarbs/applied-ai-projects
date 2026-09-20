from src.tools.account_tools import (
    get_account_balance,
    get_account_transactions,
)


def handle_account_request(message: str) -> str:
    message = message.lower()

    if "saldo" in message:
        balance = get_account_balance()
        return f"Seu saldo disponível é R$ {balance:.2f}."

    if "extrato" in message:
        transactions = get_account_transactions()
        return " | ".join(transactions)

    return "Não foi possível identificar a solicitação de conta."