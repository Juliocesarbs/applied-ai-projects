"""Constrói o índice semântico dos planos de governo."""

import json
from pathlib import Path

import pandas as pd

from src.analysis.embeddings import (
    DEFAULT_EMBEDDING_MODEL,
    generate_embeddings,
    save_chunks_metadata,
    save_embeddings,
    validate_embeddings,
)
from src.processing.text.chunk_text import build_chunks_dataframe


CORPUS_PATH = Path(
    "data/processed/government_plans/government_plans_corpus.csv"
)

TEXT_DIR = Path(
    "data/processed/government_plans/text"
)

OUTPUT_DIR = Path(
    "data/processed/government_plans/embeddings"
)

CHUNKS_PATH = OUTPUT_DIR / "chunks_metadata.csv"
EMBEDDINGS_PATH = OUTPUT_DIR / "embeddings.npy"
CONFIG_PATH = OUTPUT_DIR / "embedding_config.json"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 75
BATCH_SIZE = 8


def load_corpus(
    corpus_path: Path = CORPUS_PATH,
    text_dir: Path = TEXT_DIR,
) -> pd.DataFrame:
    """Carrega o corpus e os textos dos planos."""

    if not corpus_path.exists():
        raise FileNotFoundError(
            f"Corpus não encontrado: {corpus_path}"
        )

    corpus = pd.read_csv(
        corpus_path
    )

    required_columns = {
        "SQ_CANDIDATO",
        "NM_URNA_CANDIDATO",
        "SG_PARTIDO",
        "ARQUIVO_TEXTO",
    }

    missing_columns = (
        required_columns - set(corpus.columns)
    )

    if missing_columns:
        raise ValueError(
            "Colunas ausentes no corpus: "
            f"{sorted(missing_columns)}"
        )

    if corpus["SQ_CANDIDATO"].duplicated().any():
        raise ValueError(
            "Existem candidatos duplicados no corpus."
        )

    texts = []

    for file_name in corpus["ARQUIVO_TEXTO"]:
        file_path = text_dir / file_name

        if not file_path.exists():
            raise FileNotFoundError(
                f"Texto não encontrado: {file_path}"
            )

        text = file_path.read_text(
            encoding="utf-8"
        )

        if not text.strip():
            raise ValueError(
                f"Arquivo de texto vazio: {file_path}"
            )

        texts.append(
            text
        )

    corpus = corpus.copy()
    corpus["TEXTO"] = texts

    return corpus


def build_index(
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
    batch_size: int = BATCH_SIZE,
) -> None:
    """Constrói e persiste chunks e embeddings."""

    print("Carregando corpus...")

    corpus = load_corpus()

    print(
        f"Documentos: {len(corpus)}"
    )

    print(
        "Construindo chunks "
        f"({chunk_size}/{chunk_overlap})..."
    )

    chunks = build_chunks_dataframe(
        corpus=corpus,
        chunk_size=chunk_size,
        overlap=chunk_overlap,
    )

    if chunks.empty:
        raise RuntimeError(
            "Nenhum chunk foi criado."
        )

    print(
        f"Chunks criados: {len(chunks)}"
    )

    print("\nChunks por candidato:")

    chunk_counts = (
        chunks
        .groupby(
            [
                "NM_URNA_CANDIDATO",
                "SG_PARTIDO",
            ]
        )
        .size()
        .sort_values(
            ascending=False
        )
    )

    print(
        chunk_counts.to_string()
    )

    print(
        "\nGerando embeddings com "
        f"{DEFAULT_EMBEDDING_MODEL}..."
    )

    embeddings = generate_embeddings(
        texts=chunks[
            "TEXTO_CHUNK"
        ].tolist(),
        model=DEFAULT_EMBEDDING_MODEL,
        batch_size=batch_size,
    )

    validate_embeddings(
        embeddings=embeddings,
        expected_rows=len(chunks),
    )

    print(
        "\nMatriz de embeddings:"
    )

    print(
        f"Shape: {embeddings.shape}"
    )

    print(
        f"Dtype: {embeddings.dtype}"
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    save_chunks_metadata(
        chunks=chunks,
        output_path=CHUNKS_PATH,
    )

    save_embeddings(
        embeddings=embeddings,
        output_path=EMBEDDINGS_PATH,
    )

    config = {
        "embedding_model": (
            DEFAULT_EMBEDDING_MODEL
        ),
        "embedding_dimension": int(
            embeddings.shape[1]
        ),
        "chunk_size_words": chunk_size,
        "chunk_overlap_words": chunk_overlap,
        "num_chunks": len(chunks),
        "num_documents": len(corpus),
        "batch_size": batch_size,
    }

    with CONFIG_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            config,
            file,
            ensure_ascii=False,
            indent=4,
        )

    print("\nArquivos salvos:")

    print(
        f"- {CHUNKS_PATH}"
    )

    print(
        f"- {EMBEDDINGS_PATH}"
    )

    print(
        f"- {CONFIG_PATH}"
    )

    print(
        "\nÍndice semântico construído com sucesso."
    )


if __name__ == "__main__":
    build_index()