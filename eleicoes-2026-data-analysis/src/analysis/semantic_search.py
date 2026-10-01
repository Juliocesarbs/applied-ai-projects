"""Busca semântica nos planos de governo."""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from src.analysis.embeddings import generate_embedding


def semantic_search(
    query: str,
    chunks: pd.DataFrame,
    embeddings: np.ndarray,
    top_k: int = 5,
) -> pd.DataFrame:
    """Recupera os chunks semanticamente mais próximos da consulta."""

    if not query.strip():
        raise ValueError(
            "A consulta não pode estar vazia."
        )

    if top_k <= 0:
        raise ValueError(
            "top_k deve ser maior que zero."
        )

    if len(chunks) != embeddings.shape[0]:
        raise ValueError(
            "Quantidade de chunks diferente "
            "da quantidade de embeddings."
        )

    query_embedding = generate_embedding(
        query
    )

    query_vector = np.asarray(
        query_embedding,
        dtype=np.float32,
    ).reshape(1, -1)

    if query_vector.shape[1] != embeddings.shape[1]:
        raise ValueError(
            "Dimensão do embedding da consulta "
            "diferente da matriz persistida."
        )

    similarities = cosine_similarity(
        query_vector,
        embeddings,
    )[0]

    top_k = min(
        top_k,
        len(chunks),
    )

    top_indices = np.argsort(
        similarities
    )[-top_k:][::-1]

    results = chunks.iloc[
        top_indices
    ].copy()

    results["SIMILARIDADE"] = similarities[
        top_indices
    ]

    columns = [
        "SQ_CANDIDATO",
        "NM_URNA_CANDIDATO",
        "SG_PARTIDO",
        "CHUNK_ID",
        "SIMILARIDADE",
        "TEXTO_CHUNK",
    ]

    return results[
        columns
    ].reset_index(
        drop=True
    )