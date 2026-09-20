import re

from src.tools.pix_tools import get_pix_limit, get_pix_transaction


PIX_STATUS_KEYWORDS = (
    "não chegou",
    "nao chegou",
    "pendente",
    "status",
)

PIX_LIMIT_KEYWORDS = (
    "limite",
    "valor máximo",
    "valor maximo",
)


def contains_keyword(message: str, keywords: tuple[str, ...]) -> bool:
    message = message.lower()
    return any(keyword in message for keyword in keywords)


def identify_pix_intent(message: str) -> str:
    if contains_keyword(message, PIX_STATUS_KEYWORDS):
        return "PIX_STATUS"

    if contains_keyword(message, PIX_LIMIT_KEYWORDS):
        return "PIX_LIMIT"

    return "PIX_UNKNOWN"


def extract_transaction_id(message: str) -> str | None:
    match = re.search(r"\bPIX\d+\b", message.upper())

    if match is None:
        return None

    return match.group()


def handle_pix_status(transaction_id: str) -> str:
    transaction = get_pix_transaction(transaction_id)

    if transaction is None:
        return "Transação Pix não encontrada."

    status = transaction["status"]
    amount = transaction["amount"]

    return f"Pix de R$ {amount:.2f} com status {status}."


def handle_pix_limit() -> str:
    limit = get_pix_limit()

    return f"Seu limite Pix é R$ {limit:.2f}."


def handle_pix_request(message: str) -> str:
    intent = identify_pix_intent(message)

    if intent == "PIX_LIMIT":
        return handle_pix_limit()

    if intent == "PIX_STATUS":
        transaction_id = extract_transaction_id(message)

        if transaction_id is None:
            return "Informe o código da transação Pix."

        return handle_pix_status(transaction_id)

    return "Não foi possível identificar a solicitação de Pix."

def test_handle_pix_limit_request() -> None:
    response = handle_pix_request("Qual meu limite de Pix?")

    assert response == "Seu limite Pix é R$ 5000.00."


def test_handle_pix_status_request() -> None:
    response = handle_pix_request("Quero saber o status do Pix PIX002")

    assert response == "Pix de R$ 75.50 com status PROCESSING."


def test_handle_pix_status_without_transaction_id() -> None:
    response = handle_pix_request("Meu Pix não chegou")

    assert response == "Informe o código da transação Pix."


def test_handle_pix_status_with_invalid_transaction_id() -> None:
    response = handle_pix_request("Quero saber o status do Pix PIX999")

    assert response == "Transação Pix não encontrada."


def test_handle_unknown_pix_request() -> None:
    response = handle_pix_request("Tenho uma dúvida sobre Pix")

    assert response == "Não foi possível identificar a solicitação de Pix."