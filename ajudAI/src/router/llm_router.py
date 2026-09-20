from typing import Literal

from ollama import chat
from pydantic import BaseModel


class RouteDecision(BaseModel):
    route: Literal["PIX", "CARD", "ACCOUNT", "OUT_OF_SCOPE"]


SYSTEM_PROMPT = """
Você classifica solicitações de clientes de uma instituição financeira fictícia.

Escolha exatamente uma das rotas abaixo.

PIX:
Solicitações relacionadas ao envio de dinheiro por Pix ou transferência
instantânea, incluindo status, falhas, recebimento e limites de envio.

CARD:
Solicitações relacionadas ao cartão de crédito, incluindo fatura,
compras no crédito, limite disponível, compras recusadas e status
do cartão.

ACCOUNT:
Solicitações sobre uma conta já existente, limitadas a saldo,
extrato, entradas, saídas, transações e movimentações da conta.

OUT_OF_SCOPE:
Qualquer solicitação fora das definições anteriores.
Inclui outros produtos ou serviços financeiros, abertura de conta,
investimentos, poupança, empréstimos, financiamentos, seguros,
dados cadastrais e atendimento.

Use o contexto completo da mensagem.
Não classifique apenas pela presença de uma palavra.
Não responda ao cliente.
Retorne somente a classificação solicitada.
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
        think=False,
        options={
            "temperature": 0,
        },
    )

    decision = RouteDecision.model_validate_json(
        response.message.content
    )

    return decision.route