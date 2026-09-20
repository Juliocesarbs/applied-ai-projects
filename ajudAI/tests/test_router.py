import pytest

from src.router.router import route_message


@pytest.mark.parametrize(
    "message, expected_route",
    [
        ("Fiz um Pix e não chegou", "PIX"),
        ("Quero fazer uma transferência", "PIX"),
        ("Qual o valor da minha fatura?", "CARD"),
        ("Qual o limite do meu cartão?", "CARD"),
        ("Quero consultar meu saldo", "ACCOUNT"),
        ("Preciso do extrato da minha conta", "ACCOUNT"),
        ("Qual a previsão do tempo?", "OUT_OF_SCOPE"),
    ],
)
def test_route_message(message: str, expected_route: str) -> None:
    assert route_message(message) == expected_route

@pytest.mark.xfail(
    reason="Known limitation of the rules-based router"
)
def test_route_message_semantic_pix_request() -> None:
    message = "O dinheiro que enviei ontem ainda não chegou"

    assert route_message(message) == "PIX"