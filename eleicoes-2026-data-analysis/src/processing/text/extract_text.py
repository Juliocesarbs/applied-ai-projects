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


def load_manifest(
    path: Path,
) -> pd.DataFrame:
    """Carrega o manifesto dos planos de governo."""

    return pd.read_csv(path)


def filter_eligible_documents(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Mantém somente documentos elegíveis para análise."""

    return df[
        df["ST_ELEGIVEL_ANALISE"].eq(True)
    ].copy()


def extract_pdf_metrics(
    pdf_path: Path,
) -> dict:
    """Extrai métricas básicas da camada textual de um PDF."""

    reader = PdfReader(
        pdf_path
    )

    page_texts = []

    for page in reader.pages:
        text = page.extract_text() or ""
        page_texts.append(text)

    full_text = "\n".join(
        page_texts
    )

    pages_with_text = sum(
        bool(text.strip())
        for text in page_texts
    )

    return {
        "QT_PAGINAS": len(reader.pages),
        "QT_PAGINAS_COM_TEXTO": pages_with_text,
        "QT_CARACTERES": len(full_text),
        "QT_PALAVRAS": len(
            full_text.split()
        ),
    }


def analyze_documents(
    manifest: pd.DataFrame,
) -> pd.DataFrame:
    """Avalia a extração textual dos documentos."""

    records = []

    for _, row in manifest.iterrows():
        pdf_path = (
            PDF_DIR
            / row["ARQUIVO_PROPOSTA"]
        )

        metrics = extract_pdf_metrics(
            pdf_path
        )

        records.append(
            {
                "SQ_CANDIDATO": row["SQ_CANDIDATO"],
                "NM_URNA_CANDIDATO": row[
                    "NM_URNA_CANDIDATO"
                ],
                "SG_PARTIDO": row["SG_PARTIDO"],
                **metrics,
            }
        )

    return pd.DataFrame(
        records
    )


def main() -> None:
    manifest = load_manifest(
        MANIFEST_PATH
    )

    manifest = filter_eligible_documents(
        manifest
    )

    metrics = analyze_documents(
        manifest
    )

    print(
        metrics.to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()