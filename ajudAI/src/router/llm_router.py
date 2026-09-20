from typing import Literal

from ollama import chat
from pydantic import BaseModel


class RouteDecision(BaseModel):
    route: Literal["PIX", "CARD", "ACCOUNT", "OUT_OF_SCOPE"]


SYSTEM_PROMPT = """
Classifique solicitações de clientes de uma instituição financeira fictícia.

Rotas disponíveis:

PIX:
Transferências via Pix, problemas com Pix e limites Pix.

CARD:
Cartão, fatura, limite ou status do cartão.

ACCOUNT:
Saldo, extrato ou movimentações da conta.

OUT_OF_SCOPE:
Assuntos fora das categorias anteriores.

Classifique a solicitação sem responder ao cliente.
"""


def route_message_with_llm(message: str) -> str:
    response = chat(
        model="qwen3:4b",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        format=RouteDecision.model_json_schema(),
        options={
            "temperature": 0,
        },
    )

    decision = RouteDecision.model_validate_json(
        response.message.content
    )

    return decision.route