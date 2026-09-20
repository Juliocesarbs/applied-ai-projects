CARD_DATA = {
    "invoice": 1320.50,
    "limit": 8000.00,
    "available_limit": 4679.50,
    "status": "ACTIVE",
}


def get_card_invoice() -> float:
    return CARD_DATA["invoice"]


def get_card_limit() -> dict:
    return {
        "total": CARD_DATA["limit"],
        "available": CARD_DATA["available_limit"],
    }


def get_card_status() -> str:
    return CARD_DATA["status"]