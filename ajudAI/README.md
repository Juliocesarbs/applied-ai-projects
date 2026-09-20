# ajudAI

`ajudAI` é uma POC de um assistente financeiro com múltiplos agentes.

O objetivo do projeto é explorar, de forma simples, como um LLM local pode identificar a necessidade do usuário, direcionar a mensagem para um agente especializado e consultar ferramentas com dados fictícios.

> Este projeto usa apenas dados e cenários sintéticos. Não representa sistemas, dados, processos ou arquitetura de nenhuma instituição real.

## Como funciona

```text
Usuário
   ↓
Router
   ↓
PIX | CARD | ACCOUNT | OUT_OF_SCOPE
   ↓
Agente especializado
   ↓
Tool
   ↓
Resposta
```

O fluxo é orquestrado com LangGraph.

O Router usa o modelo local Qwen3 4B, executado com Ollama, para entender a mensagem e escolher entre:

* `PIX`
* `CARD`
* `ACCOUNT`
* `OUT_OF_SCOPE`

No fluxo de Pix, o agente também identifica a intenção da mensagem antes de escolher a operação necessária.

As tools usam dados sintéticos e retornam informações de forma determinística.

## Rules vs LLM

O projeto começou com um Router simples baseado em palavras-chave.

Depois, o mesmo problema foi testado com um LLM local.

Resultado no conjunto de teste sintético com 40 mensagens:

| Router   | Accuracy | Macro F1 | Latência média |
| -------- | -------: | -------: | -------------: |
| Rules    |    72,5% |    73,5% |          ~0 ms |
| Qwen3 4B |    97,5% |    97,5% |        ~395 ms |

O Router com regras é muito rápido, mas tem dificuldade quando a mensagem não contém as palavras esperadas.

Exemplo:

```text
"O dinheiro que enviei ainda não chegou"
```

Mesmo sem mencionar diretamente "Pix", o LLM consegue interpretar o contexto e direcionar a mensagem para o agente correto.

## Otimização

Durante os testes, o Qwen3 4B inicialmente levava cerca de 10 segundos para algumas classificações.

Como o problema é apenas de classificação, o modo de reasoning do modelo foi desativado.

Com isso, a inferência caiu para a faixa de aproximadamente 300–400 ms nos testes locais.

## Tecnologias

* Python
* LangGraph
* Ollama
* Qwen3 4B
* Pydantic
* scikit-learn
* pytest

## Executando

Com o ambiente virtual ativo:

```bash
python main.py
```

Para executar os testes:

```bash
python -m pytest -v
```

## Limitações

Este é um projeto de estudo e não uma aplicação pronta para produção.

O dataset de avaliação é pequeno e sintético. Os resultados servem para comparar as abordagens dentro desta POC e não representam o desempenho do modelo em cenários reais.
