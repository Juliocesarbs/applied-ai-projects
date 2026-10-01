"""Geração, validação e persistência de embeddings com Ollama."""

from pathlib import Path

import numpy as np
import pandas as pd
import requests


OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
DEFAULT_EMBEDDING_MODEL = "qwen3-embedding:0.6b"
DEFAULT_BATCH_SIZE = 8


def generate_embedding(
    text: str,
    model: str = DEFAULT_EMBEDDING_MODEL,
) -> list[float]:
    """Gera embedding para um único texto."""

    if not text.strip():
        raise ValueError("O texto não pode estar vazio.")

    response = requests.post(
        OLLAMA_EMBED_URL,
        json={
            "model": model,
            "input": text,
        },
        timeout=120,
    )

    if not response.ok:
        raise RuntimeError(
            "Erro ao gerar embedding: "
            f"{response.status_code} - {response.text}"
        )

    data = response.json()

    embeddings = data.get("embeddings")

    if not embeddings:
        raise RuntimeError(
            "Ollama não retornou embeddings."
        )

    return embeddings[0]


def generate_embeddings_batch(
    texts: list[str],
    model: str = DEFAULT_EMBEDDING_MODEL,
) -> np.ndarray:
    """Gera embeddings para um lote de textos."""

    if not texts:
        raise ValueError(
            "A lista de textos não pode estar vazia."
        )

    response = requests.post(
        OLLAMA_EMBED_URL,
        json={
            "model": model,
            "input": texts,
        },
        timeout=300,
    )

    if not response.ok:
        raise RuntimeError(
            "Erro ao gerar embeddings: "
            f"{response.status_code} - {response.text}"
        )

    data = response.json()

    embeddings = data.get("embeddings")

    if not embeddings:
        raise RuntimeError(
            "Ollama não retornou embeddings."
        )

    return np.asarray(
        embeddings,
        dtype=np.float32,
    )


def generate_embeddings(
    texts: list[str],
    model: str = DEFAULT_EMBEDDING_MODEL,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> np.ndarray:
    """Gera embeddings em lotes."""

    if batch_size <= 0:
        raise ValueError(
            "batch_size deve ser maior que zero."
        )

    if not texts:
        raise ValueError(
            "A lista de textos não pode estar vazia."
        )

    batches = []

    total = len(texts)

    for start in range(0, total, batch_size):
        end = min(
            start + batch_size,
            total,
        )

        batch = texts[start:end]

        batch_embeddings = generate_embeddings_batch(
            texts=batch,
            model=model,
        )

        batches.append(
            batch_embeddings
        )

        print(
            f"Embeddings: {end}/{total}"
        )

    return np.vstack(
        batches
    )


def validate_embeddings(
    embeddings: np.ndarray,
    expected_rows: int | None = None,
) -> None:
    """Valida a matriz de embeddings."""

    if embeddings.ndim != 2:
        raise ValueError(
            "A matriz de embeddings deve possuir 2 dimensões."
        )

    if expected_rows is not None:
        if embeddings.shape[0] != expected_rows:
            raise ValueError(
                "Quantidade de embeddings diferente "
                "da quantidade esperada."
            )

    if not np.isfinite(embeddings).all():
        raise ValueError(
            "A matriz contém valores inválidos."
        )

    norms = np.linalg.norm(
        embeddings,
        axis=1,
    )

    if np.any(norms == 0):
        raise ValueError(
            "Foram encontrados embeddings com norma zero."
        )


def save_embeddings(
    embeddings: np.ndarray,
    output_path: Path,
) -> None:
    """Salva a matriz de embeddings."""

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    np.save(
        output_path,
        embeddings,
    )


def load_embeddings(
    input_path: Path,
) -> np.ndarray:
    """Carrega embeddings persistidos."""

    if not input_path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {input_path}"
        )

    return np.load(
        input_path
    )


def save_chunks_metadata(
    chunks: pd.DataFrame,
    output_path: Path,
) -> None:
    """Salva os metadados dos chunks."""

    required_columns = {
        "SQ_CANDIDATO",
        "NM_URNA_CANDIDATO",
        "SG_PARTIDO",
        "CHUNK_ID",
        "TEXTO_CHUNK",
        "QT_PALAVRAS",
    }

    missing_columns = (
        required_columns - set(chunks.columns)
    )

    if missing_columns:
        raise ValueError(
            "Colunas ausentes nos chunks: "
            f"{sorted(missing_columns)}"
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    chunks.to_csv(
        output_path,
        index=False,
    )