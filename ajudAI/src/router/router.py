PIX_KEYWORDS = (
    "pix",
    "transferência",
    "transferencia",
)

CARD_KEYWORDS = (
    "cartão",
    "cartao",
    "fatura",
    "limite",
)

ACCOUNT_KEYWORDS = (
    "saldo",
    "conta",
    "extrato",
    "lançamento",
    "lancamento",
)


def contains_keyword(message: str, keywords: tuple[str, ...]) -> bool:
    message = message.lower()
    return any(keyword in message for keyword in keywords)


def route_message(message: str) -> str:
    if contains_keyword(message, PIX_KEYWORDS):
        return "PIX"

    if contains_keyword(message, CARD_KEYWORDS):
        return "CARD"

    if contains_keyword(message, ACCOUNT_KEYWORDS):
        return "ACCOUNT"

    return "OUT_OF_SCOPE"