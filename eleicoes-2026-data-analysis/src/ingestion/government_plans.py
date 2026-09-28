from pathlib import Path
import re
from zipfile import ZipFile

import pandas as pd
import requests


TSE_API_URL = (
    "https://dadosabertos.tse.jus.br/api/3/action/"
    "package_show?id=candidatos-2026"
)

OUTPUT_DIR = Path(
    "data/raw/government_plans"
)

EXTRACT_DIR = OUTPUT_DIR / "pdf"

CANDIDATES_PATH = Path(
    "data/processed/registros_presidenciais_2026.csv"
)

MANIFEST_PATH = Path(
    "data/processed/government_plans/"
    "government_plans_manifest.csv"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/152.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

PDF_PATTERN = re.compile(
    r"2026BR(\d+)_\d+\.pdf$"
)


def get_dataset_metadata() -> dict:
    """Obtém os metadados do conjunto de candidatos do TSE."""

    response = requests.get(
        TSE_API_URL,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()["result"]


def find_presidential_plans_resource(
    metadata: dict,
) -> dict:
    """Localiza o recurso de propostas para Presidente."""

    for resource in metadata["resources"]:
        if resource.get("name") == "BR - Proposta de governo":
            return resource

    raise ValueError(
        "Recurso de propostas presidenciais não encontrado."
    )


def download_file(
    url: str,
    output_path: Path,
) -> None:
    """Baixa um arquivo para o diretório informado."""

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=60,
    )

    response.raise_for_status()

    output_path.write_bytes(
        response.content
    )


def extract_candidate_id(
    file_name: str,
) -> int | None:
    """Extrai o SQ_CANDIDATO do nome do PDF."""

    match = PDF_PATTERN.search(
        Path(file_name).name
    )

    if match is None:
        return None

    return int(
        match.group(1)
    )


def extract_candidate_pdfs(
    zip_path: Path,
    output_dir: Path,
) -> list[dict]:
    """Extrai os PDFs e identifica seus candidatos."""

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    documents = []

    with ZipFile(zip_path) as zip_file:
        for file_name in zip_file.namelist():
            candidate_id = extract_candidate_id(
                file_name
            )

            if candidate_id is None:
                continue

            source = zip_file.open(
                file_name
            )

            output_path = (
                output_dir
                / Path(file_name).name
            )

            with (
                source,
                output_path.open("wb") as destination,
            ):
                destination.write(
                    source.read()
                )

            documents.append(
                {
                    "SQ_CANDIDATO": candidate_id,
                    "ARQUIVO_PROPOSTA": output_path.name,
                }
            )

    return documents


def load_candidates(
    path: Path,
) -> pd.DataFrame:
    """Carrega os registros presidenciais processados."""

    return pd.read_csv(path)


def build_manifest(
    documents: list[dict],
    candidates: pd.DataFrame,
) -> pd.DataFrame:
    """Relaciona os documentos aos registros dos candidatos."""

    documents_df = pd.DataFrame(
        documents
    )

    candidate_columns = [
        "SQ_CANDIDATO",
        "NM_URNA_CANDIDATO",
        "SG_PARTIDO",
        "DS_SITUACAO_JULGAMENTO",
        "ST_SUBSTITUIDO",
        "ST_ELEGIVEL_ANALISE",
    ]

    manifest = documents_df.merge(
        candidates[candidate_columns],
        on="SQ_CANDIDATO",
        how="left",
        validate="one_to_one",
    )

    return manifest


def validate_manifest(
    manifest: pd.DataFrame,
    candidates: pd.DataFrame,
) -> None:
    """Valida a associação entre PDFs e candidatos."""

    print(
        f"Documentos encontrados: {len(manifest)}"
    )

    print(
        "Candidatos presidenciais: "
        f"{len(candidates)}"
    )

    unmatched = (
        manifest["NM_URNA_CANDIDATO"]
        .isna()
        .sum()
    )

    print(
        "Documentos sem candidato associado: "
        f"{unmatched}"
    )

    duplicates = (
        manifest["SQ_CANDIDATO"]
        .duplicated()
        .sum()
    )

    print(
        "Candidatos com documentos duplicados: "
        f"{duplicates}"
    )

    missing_documents = (
        set(candidates["SQ_CANDIDATO"])
        - set(manifest["SQ_CANDIDATO"])
    )

    print(
        "Candidatos sem documento: "
        f"{len(missing_documents)}"
    )

    eligible_documents = (
        manifest["ST_ELEGIVEL_ANALISE"]
        .fillna(False)
        .sum()
    )

    print(
        "Documentos elegíveis para análise: "
        f"{eligible_documents}"
    )

    if unmatched > 0:
        raise ValueError(
            "Existem documentos sem candidato associado."
        )

    if duplicates > 0:
        raise ValueError(
            "Existem documentos duplicados por candidato."
        )

    if missing_documents:
        raise ValueError(
            "Existem candidatos sem documento de proposta."
        )


def save_manifest(
    manifest: pd.DataFrame,
    path: Path,
) -> None:
    """Salva o manifesto dos documentos."""

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    manifest.to_csv(
        path,
        index=False,
        encoding="utf-8",
    )

    print(
        f"Manifesto salvo em: {path}"
    )


def main() -> None:
    metadata = get_dataset_metadata()

    resource = find_presidential_plans_resource(
        metadata
    )

    zip_path = (
        OUTPUT_DIR
        / "proposta_governo_2026_BR.zip"
    )

    download_file(
        resource["url"],
        zip_path,
    )

    documents = extract_candidate_pdfs(
        zip_path,
        EXTRACT_DIR,
    )

    candidates = load_candidates(
        CANDIDATES_PATH
    )

    manifest = build_manifest(
        documents,
        candidates,
    )

    validate_manifest(
        manifest,
        candidates,
    )

    save_manifest(
        manifest,
        MANIFEST_PATH,
    )


if __name__ == "__main__":
    main()