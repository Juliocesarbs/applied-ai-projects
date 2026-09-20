import re
from typing import Literal

from ollama import chat
from pydantic import BaseModel

from src.tools.pix_tools import get_pix_limit, get_pix_transaction


class PixIntentDecision(BaseModel):
    intent: Literal["PIX_STATUS", "PIX_LIMIT", "PIX_UNKNOWN"]


SYSTEM_PROMPT = """
Classifique a intenção de uma solicitação relacionada a Pix.

Intenções disponíveis:

PIX_STATUS:
Consulta sobre uma transferência Pix realizada, incluindo status,
falha, processamento, atraso ou confirmação de recebimento.

PIX_LIMIT:
Consulta sobre limite ou valor máximo permitido para transferências Pix.

PIX_UNKNOWN:
Solicitações relacionadas a Pix que não pertencem às intenções anteriores.

Não responda ao cliente.
Retorne somente a classificação solicitada.
"""


def identify_pix_intent(message: str) -> str:
    response = chat(
        model="qwen3:4b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        format=PixIntentDecision.model_json_schema(),
        think=False,
        options={"temperature": 0},
    )

    decision = PixIntentDecision.model_validate_json(
        response.message.content
    )

    return decision.intent


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