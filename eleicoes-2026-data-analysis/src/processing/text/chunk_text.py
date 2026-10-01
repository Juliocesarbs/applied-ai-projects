"""Funções para divisão dos planos de governo em chunks."""

import pandas as pd


DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 150


def split_text_into_chunks(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """Divide um texto em blocos de palavras com sobreposição."""

    if chunk_size <= 0:
        raise ValueError("chunk_size deve ser maior que zero.")

    if overlap < 0:
        raise ValueError("overlap não pode ser negativo.")

    if overlap >= chunk_size:
        raise ValueError("overlap deve ser menor que chunk_size.")

    words = text.split()

    if not words:
        return []

    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(words), step):
        end = start + chunk_size
        chunk_words = words[start:end]

        if not chunk_words:
            break

        chunks.append(
            " ".join(chunk_words)
        )

        if end >= len(words):
            break

    return chunks


def build_chunks_dataframe(
    corpus: pd.DataFrame,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> pd.DataFrame:
    """Cria um DataFrame de chunks a partir do corpus."""

    required_columns = {
        "SQ_CANDIDATO",
        "NM_URNA_CANDIDATO",
        "SG_PARTIDO",
        "TEXTO",
    }

    missing_columns = (
        required_columns - set(corpus.columns)
    )

    if missing_columns:
        raise ValueError(
            "Colunas ausentes no corpus: "
            f"{sorted(missing_columns)}"
        )

    records = []

    for _, row in corpus.iterrows():
        chunks = split_text_into_chunks(
            text=row["TEXTO"],
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for chunk_id, chunk_text in enumerate(chunks):
            records.append(
                {
                    "SQ_CANDIDATO": row["SQ_CANDIDATO"],
                    "NM_URNA_CANDIDATO": (
                        row["NM_URNA_CANDIDATO"]
                    ),
                    "SG_PARTIDO": row["SG_PARTIDO"],
                    "CHUNK_ID": chunk_id,
                    "TEXTO_CHUNK": chunk_text,
                    "QT_PALAVRAS": len(
                        chunk_text.split()
                    ),
                }
            )

    return pd.DataFrame(records)