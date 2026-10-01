"""Avaliação do retrieval semântico dos planos de governo."""

from pathlib import Path

import numpy as np
import pandas as pd

from src.analysis.semantic_search import semantic_search


EMBEDDINGS_DIR = Path(
    "data/processed/government_plans/embeddings"
)

CHUNKS_PATH = (
    EMBEDDINGS_DIR
    / "chunks_metadata.csv"
)

EMBEDDINGS_PATH = (
    EMBEDDINGS_DIR
    / "embeddings.npy"
)

OUTPUT_PATH = (
    EMBEDDINGS_DIR
    / "retrieval_evaluation_500_75.csv"
)

TOP_K = 5


EVALUATION_QUERIES = [
    {
        "query_id": "educacao",
        "query": (
            "Quais propostas aparecem nos planos "
            "sobre educação pública?"
        ),
    },
    {
        "query_id": "saude",
        "query": (
            "Quais propostas aparecem nos planos "
            "sobre saúde pública e SUS?"
        ),
    },
    {
        "query_id": "seguranca",
        "query": (
            "Quais propostas aparecem nos planos "
            "sobre segurança pública e combate ao crime?"
        ),
    },
    {
        "query_id": "trabalho",
        "query": (
            "Quais propostas aparecem nos planos "
            "sobre emprego, trabalho e relações trabalhistas?"
        ),
    },
    {
        "query_id": "meio_ambiente",
        "query": (
            "Quais propostas aparecem nos planos "
            "sobre meio ambiente e mudanças climáticas?"
        ),
    },
    {
        "query_id": "moradia",
        "query": (
            "Quais propostas aparecem nos planos "
            "sobre habitação e moradia?"
        ),
    },
    {
        "query_id": "infraestrutura",
        "query": (
            "Quais propostas aparecem nos planos "
            "sobre infraestrutura e transporte público?"
        ),
    },
    {
        "query_id": "mulheres",
        "query": (
            "Quais propostas aparecem nos planos "
            "sobre políticas para mulheres?"
        ),
    },
]


def load_data() -> tuple[pd.DataFrame, np.ndarray]:
    """Carrega chunks e embeddings."""

    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {CHUNKS_PATH}"
        )

    if not EMBEDDINGS_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {EMBEDDINGS_PATH}"
        )

    chunks = pd.read_csv(
        CHUNKS_PATH
    )

    embeddings = np.load(
        EMBEDDINGS_PATH
    )

    if len(chunks) != embeddings.shape[0]:
        raise ValueError(
            "Quantidade de chunks diferente "
            "da quantidade de embeddings."
        )

    return chunks, embeddings


def evaluate_retrieval(
    chunks: pd.DataFrame,
    embeddings: np.ndarray,
) -> pd.DataFrame:
    """Executa as consultas da avaliação."""

    records = []

    for item in EVALUATION_QUERIES:
        query_id = item["query_id"]
        query = item["query"]

        print(
            f"\nConsulta: {query_id}"
        )

        results = semantic_search(
            query=query,
            chunks=chunks,
            embeddings=embeddings,
            top_k=TOP_K,
        )

        for rank, row in enumerate(
            results.itertuples(),
            start=1,
        ):
            records.append(
                {
                    "QUERY_ID": query_id,
                    "QUERY": query,
                    "RANK": rank,
                    "SQ_CANDIDATO": row.SQ_CANDIDATO,
                    "NM_URNA_CANDIDATO": (
                        row.NM_URNA_CANDIDATO
                    ),
                    "SG_PARTIDO": row.SG_PARTIDO,
                    "CHUNK_ID": row.CHUNK_ID,
                    "SIMILARIDADE": row.SIMILARIDADE,
                    "TEXTO_CHUNK": row.TEXTO_CHUNK,
                    "RELEVANTE": "",
                }
            )

        print(
            results[
                [
                    "NM_URNA_CANDIDATO",
                    "SG_PARTIDO",
                    "CHUNK_ID",
                    "SIMILARIDADE",
                ]
            ].to_string(
                index=False
            )
        )

    return pd.DataFrame(
        records
    )


def save_evaluation(
    evaluation: pd.DataFrame,
) -> None:
    """Salva os resultados para rotulagem manual."""

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    evaluation.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"\nArquivo salvo em: {OUTPUT_PATH}"
    )

    print(
        f"Resultados: {len(evaluation)}"
    )


def main() -> None:
    """Executa a avaliação de retrieval."""

    chunks, embeddings = load_data()

    print(
        f"Chunks carregados: {len(chunks)}"
    )

    print(
        f"Dimensão dos embeddings: "
        f"{embeddings.shape[1]}"
    )

    evaluation = evaluate_retrieval(
        chunks=chunks,
        embeddings=embeddings,
    )

    save_evaluation(
        evaluation
    )


if __name__ == "__main__":
    main()