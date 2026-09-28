from pathlib import Path

import pandas as pd
from pypdf import PdfReader


PDF_DIR = Path(
    "data/raw/government_plans/pdf"
)

MANIFEST_PATH = Path(
    "data/processed/government_plans/"
    "government_plans_manifest.csv"
)

OUTPUT_DIR = Path(
    "data/processed/government_plans/text"
)

CORPUS_PATH = Path(
    "data/processed/government_plans/"
    "government_plans_corpus.csv"
)


def load_manifest(
    path: Path,
) -> pd.DataFrame:
    """Carrega o manifesto dos documentos."""

    return pd.read_csv(path)


def filter_eligible_documents(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Mantém somente documentos elegíveis para análise."""

    return df[
        df["ST_ELEGIVEL_ANALISE"].eq(True)
    ].copy()


def extract_pages(
    pdf_path: Path,
) -> list[str]:
    """Extrai o texto de cada página do PDF."""

    reader = PdfReader(
        pdf_path
    )

    return [
        page.extract_text() or ""
        for page in reader.pages
    ]


def normalize_text(
    text: str,
) -> str:
    """Aplica normalização mínima ao texto extraído."""

    lines = [
        line.strip()
        for line in text.splitlines()
    ]

    lines = [
        line
        for line in lines
        if line
    ]

    return "\n".join(
        lines
    )


def build_document_text(
    pages: list[str],
) -> str:
    """Combina o texto extraído das páginas."""

    normalized_pages = [
        normalize_text(page)
        for page in pages
    ]

    return "\n\n".join(
        page
        for page in normalized_pages
        if page
    )


def save_text(
    text: str,
    output_path: Path,
) -> None:
    """Salva o texto extraído de um documento."""

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        text,
        encoding="utf-8",
    )


def build_corpus(
    manifest: pd.DataFrame,
) -> pd.DataFrame:
    """Constrói o corpus dos planos elegíveis."""

    records = []

    for _, row in manifest.iterrows():
        pdf_path = (
            PDF_DIR
            / row["ARQUIVO_PROPOSTA"]
        )

        pages = extract_pages(
            pdf_path
        )

        text = build_document_text(
            pages
        )

        text_file = (
            f"{row['SQ_CANDIDATO']}.txt"
        )

        save_text(
            text,
            OUTPUT_DIR / text_file,
        )

        records.append(
            {
                "SQ_CANDIDATO": row["SQ_CANDIDATO"],
                "NM_URNA_CANDIDATO": row[
                    "NM_URNA_CANDIDATO"
                ],
                "SG_PARTIDO": row["SG_PARTIDO"],
                "ARQUIVO_PROPOSTA": row[
                    "ARQUIVO_PROPOSTA"
                ],
                "ARQUIVO_TEXTO": text_file,
                "QT_PAGINAS": len(pages),
                "QT_CARACTERES": len(text),
                "QT_PALAVRAS": len(
                    text.split()
                ),
            }
        )

    return pd.DataFrame(
        records
    )


def save_corpus(
    corpus: pd.DataFrame,
    path: Path,
) -> None:
    """Salva os metadados do corpus."""

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    corpus.to_csv(
        path,
        index=False,
        encoding="utf-8",
    )


def main() -> None:
    manifest = load_manifest(
        MANIFEST_PATH
    )

    manifest = filter_eligible_documents(
        manifest
    )

    corpus = build_corpus(
        manifest
    )

    save_corpus(
        corpus,
        CORPUS_PATH,
    )

    print(
        corpus.to_string(
            index=False
        )
    )

    print(
        "\nDocumentos no corpus: "
        f"{len(corpus)}"
    )

    print(
        "Corpus salvo em: "
        f"{CORPUS_PATH}"
    )


if __name__ == "__main__":
    main()