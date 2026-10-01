"""Avaliação manual da geração do pipeline RAG."""

from pathlib import Path

import pandas as pd

from src.analysis.rag import RAGPipeline


OUTPUT_PATH = Path(
    "data/processed/government_plans/embeddings/"
    "rag_evaluation.csv"
)

TOP_K = 3


EVALUATION_QUERIES = [
    {
        "query_id": "educacao",
        "query": (
            "Quais propostas aparecem nos trechos "
            "recuperados sobre educação pública?"
        ),
    },
    {
        "query_id": "saude",
        "query": (
            "Quais propostas aparecem nos trechos "
            "recuperados sobre saúde pública e SUS?"
        ),
    },
    {
        "query_id": "seguranca",
        "query": (
            "Quais propostas aparecem nos trechos "
            "recuperados sobre segurança pública "
            "e combate ao crime?"
        ),
    },
    {
        "query_id": "trabalho",
        "query": (
            "Quais propostas aparecem nos trechos "
            "recuperados sobre emprego e trabalho?"
        ),
    },
    {
        "query_id": "meio_ambiente",
        "query": (
            "Quais propostas aparecem nos trechos "
            "recuperados sobre meio ambiente "
            "e mudanças climáticas?"
        ),
    },
    {
        "query_id": "moradia",
        "query": (
            "Quais propostas aparecem nos trechos "
            "recuperados sobre habitação e moradia?"
        ),
    },
    {
        "query_id": "infraestrutura",
        "query": (
            "Quais propostas aparecem nos trechos "
            "recuperados sobre infraestrutura "
            "e transporte público?"
        ),
    },
    {
        "query_id": "mulheres",
        "query": (
            "Quais propostas aparecem nos trechos "
            "recuperados sobre políticas para mulheres?"
        ),
    },
]


def load_existing_results() -> pd.DataFrame:
    """Carrega resultados já processados."""

    if not OUTPUT_PATH.exists():
        return pd.DataFrame()

    evaluation = pd.read_csv(
        OUTPUT_PATH
    )

    print(
        f"Resultados existentes: {len(evaluation)}"
    )

    return evaluation


def save_results(
    evaluation: pd.DataFrame,
) -> None:
    """Salva os resultados da avaliação."""

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    evaluation.to_csv(
        OUTPUT_PATH,
        index=False,
    )


def evaluate_rag() -> pd.DataFrame:
    """Executa as perguntas pendentes e salva cada resultado."""

    rag = RAGPipeline()

    evaluation = load_existing_results()

    if evaluation.empty:
        processed_queries = set()
    else:
        processed_queries = set(
            evaluation["QUERY_ID"]
            .dropna()
            .astype(str)
        )

    records = evaluation.to_dict(
        orient="records"
    )

    total = len(EVALUATION_QUERIES)

    for index, item in enumerate(
        EVALUATION_QUERIES,
        start=1,
    ):
        query_id = item["query_id"]
        query = item["query"]

        if query_id in processed_queries:
            print(
                f"[{index}/{total}] "
                f"{query_id}: já processada"
            )
            continue

        print(
            f"\n[{index}/{total}] "
            f"{query_id}"
        )

        try:
            response, sources = rag.query(
                query=query,
                top_k=TOP_K,
            )

        except Exception as error:
            print(
                f"Erro em {query_id}: {error}"
            )
            continue

        source_ids = []

        for row in sources.itertuples():
            source_ids.append(
                (
                    f"{row.NM_URNA_CANDIDATO}"
                    f"|{row.SG_PARTIDO}"
                    f"|{row.CHUNK_ID}"
                )
            )

        records.append(
            {
                "QUERY_ID": query_id,
                "QUERY": query,
                "RESPONSE": response,
                "SOURCES": " || ".join(source_ids),
                "GROUNDED": "",
                "CITACAO": "",
                "PORTUGUES": "",
                "SEM_AVALIACAO": "",
                "OBSERVACAO": "",
            }
        )

        evaluation = pd.DataFrame(
            records
        )

        save_results(
            evaluation
        )

        print(
            f"{query_id}: salva"
        )

    return pd.DataFrame(
        records
    )


def main() -> None:
    """Executa a avaliação do RAG."""

    evaluation = evaluate_rag()

    print(
        f"\nArquivo: {OUTPUT_PATH}"
    )

    print(
        f"Respostas salvas: {len(evaluation)}"
    )

    print(
        f"Esperadas: {len(EVALUATION_QUERIES)}"
    )


if __name__ == "__main__":
    main()