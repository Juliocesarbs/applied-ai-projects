"""Exporta respostas do RAG com os textos das fontes recuperadas."""

from pathlib import Path

import pandas as pd


EMBEDDINGS_DIR = Path(
    "data/processed/government_plans/embeddings"
)

RAG_EVALUATION_PATH = (
    EMBEDDINGS_DIR
    / "rag_evaluation.csv"
)

CHUNKS_PATH = (
    EMBEDDINGS_DIR
    / "chunks_metadata.csv"
)

OUTPUT_PATH = (
    EMBEDDINGS_DIR
    / "rag_evaluation_with_sources.txt"
)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carrega avaliação RAG e metadados dos chunks."""

    if not RAG_EVALUATION_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {RAG_EVALUATION_PATH}"
        )

    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {CHUNKS_PATH}"
        )

    evaluation = pd.read_csv(
        RAG_EVALUATION_PATH
    )

    chunks = pd.read_csv(
        CHUNKS_PATH
    )

    return evaluation, chunks


def parse_source(source: str) -> tuple[str, str, int]:
    """Extrai candidato, partido e chunk do identificador."""

    parts = source.split("|")

    if len(parts) != 3:
        raise ValueError(
            f"Fonte inválida: {source}"
        )

    candidate = parts[0].strip()
    party = parts[1].strip()
    chunk_id = int(parts[2])

    return candidate, party, chunk_id


def find_chunk(
    chunks: pd.DataFrame,
    candidate: str,
    party: str,
    chunk_id: int,
) -> pd.Series:
    """Localiza o chunk correspondente à fonte."""

    result = chunks[
        (chunks["NM_URNA_CANDIDATO"] == candidate)
        & (chunks["SG_PARTIDO"] == party)
        & (chunks["CHUNK_ID"] == chunk_id)
    ]

    if len(result) != 1:
        raise ValueError(
            "Não foi possível identificar unicamente "
            f"{candidate}|{party}|{chunk_id}"
        )

    return result.iloc[0]


def build_report(
    evaluation: pd.DataFrame,
    chunks: pd.DataFrame,
) -> str:
    """Constrói relatório textual para avaliação manual."""

    sections = []

    for _, row in evaluation.iterrows():
        section = [
            "=" * 100,
            f"QUERY_ID: {row['QUERY_ID']}",
            f"PERGUNTA: {row['QUERY']}",
            "",
            "RESPOSTA DO MODELO:",
            str(row["RESPONSE"]),
            "",
            "FONTES RECUPERADAS:",
        ]

        sources = str(
            row["SOURCES"]
        ).split(" || ")

        for source_number, source in enumerate(
            sources,
            start=1,
        ):
            candidate, party, chunk_id = parse_source(
                source
            )

            chunk = find_chunk(
                chunks=chunks,
                candidate=candidate,
                party=party,
                chunk_id=chunk_id,
            )

            section.extend(
                [
                    "",
                    "-" * 100,
                    (
                        f"FONTE {source_number} | "
                        f"{candidate} ({party}) | "
                        f"CHUNK {chunk_id}"
                    ),
                    "",
                    str(
                        chunk["TEXTO_CHUNK"]
                    ),
                ]
            )

        sections.append(
            "\n".join(section)
        )

    return "\n\n".join(
        sections
    )


def save_report(
    report: str,
) -> None:
    """Salva o relatório."""

    OUTPUT_PATH.write_text(
        report,
        encoding="utf-8",
    )

    print(
        f"Arquivo salvo em: {OUTPUT_PATH}"
    )


def main() -> None:
    """Executa a exportação."""

    evaluation, chunks = load_data()

    print(
        f"Respostas RAG: {len(evaluation)}"
    )

    print(
        f"Chunks disponíveis: {len(chunks)}"
    )

    report = build_report(
        evaluation=evaluation,
        chunks=chunks,
    )

    save_report(
        report
    )


if __name__ == "__main__":
    main()