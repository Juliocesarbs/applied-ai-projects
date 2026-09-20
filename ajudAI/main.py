from src.agents.account_agent import handle_account_request
from src.agents.card_agent import handle_card_request
from src.agents.pix_agent import handle_pix_request
from src.router.router import route_message


def get_user_message() -> str:
    return input("Como posso ajudar? ").strip()


def handle_request(message: str, route: str) -> str:
    if route == "PIX":
        return handle_pix_request(message)

    if route == "CARD":
        return handle_card_request(message)

    if route == "ACCOUNT":
        return handle_account_request(message)

    return "Não foi possível atender essa solicitação."


def main() -> None:
    message = get_user_message()
    route = route_message(message)
    response = handle_request(message, route)

    print(f"\nRota: {route}")
    print(f"Resposta: {response}")


if __name__ == "__main__":
    main()