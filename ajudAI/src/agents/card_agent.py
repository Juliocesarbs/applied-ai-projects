from src.tools.card_tools import (
    get_card_invoice,
    get_card_limit,
    get_card_status,
)


def handle_card_request(message: str) -> str:
    message = message.lower()

    if "fatura" in message:
        invoice = get_card_invoice()
        return f"Sua fatura atual é R$ {invoice:.2f}."

    if "limite" in message:
        limit = get_card_limit()

        return (
            f"Seu limite total é R$ {limit['total']:.2f} "
            f"e o disponível é R$ {limit['available']:.2f}."
        )

    if "bloqueado" in message or "status" in message:
        status = get_card_status()
        return f"O status do seu cartão é {status}."

    return "Não foi possível identificar a solicitação de cartão."