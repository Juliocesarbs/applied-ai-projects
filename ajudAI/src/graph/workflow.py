from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from src.agents.account_agent import handle_account_request
from src.agents.card_agent import handle_card_request
from src.agents.pix_agent import handle_pix_request
from src.router.router import route_message


class AgentState(TypedDict):
    message: str
    route: str
    response: str


def router_node(state: AgentState) -> dict:
    route = route_message(state["message"])

    return {"route": route}


def pix_node(state: AgentState) -> dict:
    response = handle_pix_request(state["message"])

    return {"response": response}


def card_node(state: AgentState) -> dict:
    response = handle_card_request(state["message"])

    return {"response": response}


def account_node(state: AgentState) -> dict:
    response = handle_account_request(state["message"])

    return {"response": response}


def out_of_scope_node(state: AgentState) -> dict:
    return {"response": "Não foi possível atender essa solicitação."}


def select_route(state: AgentState) -> str:
    return state["route"]


def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("router", router_node)
    builder.add_node("pix", pix_node)
    builder.add_node("card", card_node)
    builder.add_node("account", account_node)
    builder.add_node("out_of_scope", out_of_scope_node)

    builder.add_edge(START, "router")

    builder.add_conditional_edges(
        "router",
        select_route,
        {
            "PIX": "pix",
            "CARD": "card",
            "ACCOUNT": "account",
            "OUT_OF_SCOPE": "out_of_scope",
        },
    )

    builder.add_edge("pix", END)
    builder.add_edge("card", END)
    builder.add_edge("account", END)
    builder.add_edge("out_of_scope", END)

    return builder.compile()


graph = build_graph()