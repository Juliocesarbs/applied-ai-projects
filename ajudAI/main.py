from src.graph.workflow import graph


def get_user_message() -> str:
    return input("Como posso ajudar? ").strip()


def main() -> None:
    message = get_user_message()

    result = graph.invoke(
        {
            "message": message,
            "route": "",
            "response": "",
        }
    )

    print(f"\nRota: {result['route']}")
    print(f"Resposta: {result['response']}")


if __name__ == "__main__":
    main()