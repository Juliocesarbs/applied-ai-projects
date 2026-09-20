# ajudAI

POC de um assistente inteligente baseado em agentes especializados para atendimento de solicitações em um contexto financeiro.

O objetivo do projeto é explorar como diferentes estratégias de roteamento e agentes especializados podem interpretar solicitações em linguagem natural e utilizar ferramentas para responder ao usuário.

> Todos os dados, cenários e informações utilizados neste projeto são fictícios e foram criados exclusivamente para fins de estudo e demonstração.

## Arquitetura

O fluxo inicial do projeto é:

User → Router → Specialized Agent → Tool → Response

Os domínios utilizados na POC são:

- Account
- Card
- Pix

## Estrutura

```text
ajudAI/
├── src/
│   ├── agents/
│   ├── router/
│   └── tools/
├── tests/
├── main.py
└── requirements.txt