import pytest

from src.agents.pix_agent import handle_pix_request, identify_pix_intent


@pytest.mark.parametrize(
    "message, expected_intent",
    [
        ("Meu Pix não chegou", "PIX_STATUS"),
        ("Quero saber o status do meu Pix", "PIX_STATUS"),
        ("Meu Pix está pendente", "PIX_STATUS"),
        ("Qual meu limite de Pix?", "PIX_LIMIT"),
        ("Qual o valor máximo de Pix?", "PIX_LIMIT"),
        ("Tenho uma dúvida sobre Pix", "PIX_UNKNOWN"),
    ],
)
def test_identify_pix_intent(message: str, expected_intent: str) -> None:
    assert identify_pix_intent(message) == expected_intent