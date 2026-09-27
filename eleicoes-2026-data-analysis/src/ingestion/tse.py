from pathlib import Path
from zipfile import ZipFile

import requests


DATASET_API_URL = (
    "https://dadosabertos.tse.jus.br/api/3/action/"
    "package_show?id=candidatos-2026"
)

RAW_DATA_PATH = Path("data/raw")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/152.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


def get_dataset_metadata() -> dict:
    response = requests.get(
        DATASET_API_URL,
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()

    if not data.get("success"):
        raise RuntimeError(
            "Não foi possível consultar o catálogo do TSE."
        )

    return data["result"]


def find_resource(dataset: dict, resource_name: str) -> dict:
    resources = dataset.get("resources", [])

    for resource in resources:
        if resource.get("name") == resource_name:
            return resource

    raise ValueError(
        f"Recurso '{resource_name}' não encontrado."
    )


def download_resource(resource: dict) -> Path:
    RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)

    url = resource["url"]
    filename = url.split("/")[-1]
    destination = RAW_DATA_PATH / filename

    print(f"Baixando: {resource['name']}")

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=120,
    )
    response.raise_for_status()

    destination.write_bytes(response.content)

    print(f"Arquivo salvo em: {destination}")

    return destination


def extract_zip(zip_path: Path) -> Path:
    destination = zip_path.parent / zip_path.stem

    destination.mkdir(
        parents=True,
        exist_ok=True,
    )

    with ZipFile(zip_path, "r") as zip_file:
        zip_file.extractall(destination)

    print(f"Arquivos extraídos em: {destination}")

    return destination


def main() -> None:
    dataset = get_dataset_metadata()

    resource_names = [
        "Candidatos",
        "Candidatos - Informações complementares",
        "Bens de candidatos",
    ]

    for resource_name in resource_names:
        resource = find_resource(
            dataset,
            resource_name=resource_name,
        )

        zip_path = download_resource(
            resource
        )

        extract_zip(
            zip_path
        )


if __name__ == "__main__":
    main()