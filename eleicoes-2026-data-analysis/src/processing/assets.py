from pathlib import Path

import pandas as pd


RAW_ASSETS_PATH = Path(
    "data/raw/bem_candidato_2026/"
    "bem_candidato_2026_BR.csv"
)

CANDIDATES_PATH = Path(
    "data/processed/candidatos_deferidos_2026.csv"
)

PROCESSED_ASSETS_PATH = Path(
    "data/processed/bens_candidatos_deferidos_2026.csv"
)

ANALYTICAL_DATA_PATH = Path(
    "data/processed/"
    "candidatos_deferidos_2026_com_patrimonio.csv"
)


ASSET_COLUMNS = [
    "SQ_CANDIDATO",
    "NR_ORDEM_BEM_CANDIDATO",
    "CD_TIPO_BEM_CANDIDATO",
    "DS_TIPO_BEM_CANDIDATO",
    "DS_BEM_CANDIDATO",
    "VR_BEM_CANDIDATO",
    "DT_ULT_ATUAL_BEM_CANDIDATO",
]


SPECIAL_TEXT_VALUES = {
    "#NE": pd.NA,
    "#NULO": pd.NA,
}


def load_assets(
    path: Path,
) -> pd.DataFrame:
    """Carrega os bens declarados ao TSE."""

    return pd.read_csv(
        path,
        sep=";",
        encoding="latin-1",
    )


def load_candidates(
    path: Path,
) -> pd.DataFrame:
    """Carrega as candidaturas deferidas."""

    return pd.read_csv(path)


def select_asset_columns(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Seleciona as colunas utilizadas na análise."""

    available_columns = [
        column
        for column in ASSET_COLUMNS
        if column in df.columns
    ]

    return df[available_columns].copy()


def filter_candidate_assets(
    assets: pd.DataFrame,
    candidates: pd.DataFrame,
) -> pd.DataFrame:
    """Mantém apenas bens das candidaturas deferidas."""

    candidate_ids = candidates[
        "SQ_CANDIDATO"
    ].unique()

    return assets[
        assets["SQ_CANDIDATO"]
        .isin(candidate_ids)
    ].copy()


def clean_special_values(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Converte códigos especiais textuais em valores ausentes."""

    df = df.copy()

    text_columns = df.select_dtypes(
        include=["object", "string"]
    ).columns

    df[text_columns] = df[text_columns].replace(
        SPECIAL_TEXT_VALUES
    )

    return df


def convert_asset_values(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Converte valores monetários para tipo numérico."""

    df = df.copy()

    df["VR_BEM_CANDIDATO"] = (
        df["VR_BEM_CANDIDATO"]
        .astype("string")
        .str.replace(
            ".",
            "",
            regex=False,
        )
        .str.replace(
            ",",
            ".",
            regex=False,
        )
    )

    df["VR_BEM_CANDIDATO"] = pd.to_numeric(
        df["VR_BEM_CANDIDATO"],
        errors="coerce",
    )

    return df


def convert_dates(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Converte campos de data."""

    df = df.copy()

    column = "DT_ULT_ATUAL_BEM_CANDIDATO"

    if column in df.columns:
        df[column] = pd.to_datetime(
            df[column],
            format="%d/%m/%Y",
            errors="coerce",
        )

    return df


def aggregate_assets(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Calcula métricas patrimoniais por candidato."""

    return (
        df.groupby(
            "SQ_CANDIDATO",
            as_index=False,
        )
        .agg(
            QT_BENS=(
                "NR_ORDEM_BEM_CANDIDATO",
                "count",
            ),
            VL_TOTAL_BENS=(
                "VR_BEM_CANDIDATO",
                "sum",
            ),
            VL_MEDIO_BENS=(
                "VR_BEM_CANDIDATO",
                "mean",
            ),
            VL_MEDIANO_BENS=(
                "VR_BEM_CANDIDATO",
                "median",
            ),
            VL_MAIOR_BEM=(
                "VR_BEM_CANDIDATO",
                "max",
            ),
        )
    )


def merge_candidates_assets(
    candidates: pd.DataFrame,
    asset_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Combina candidaturas deferidas e métricas de bens."""

    df = candidates.merge(
        asset_summary,
        on="SQ_CANDIDATO",
        how="left",
        validate="one_to_one",
    )

    df["QT_BENS"] = (
        df["QT_BENS"]
        .fillna(0)
        .astype(int)
    )

    return df


def add_asset_metrics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Cria métricas derivadas sobre os bens declarados."""

    df = df.copy()

    df["PC_MAIOR_BEM"] = (
        df["VL_MAIOR_BEM"]
        / df["VL_TOTAL_BENS"]
    )

    return df


def validate_assets(
    assets: pd.DataFrame,
    candidates: pd.DataFrame,
    analytical_data: pd.DataFrame,
) -> None:
    """Executa verificações de qualidade dos dados."""

    print(
        "Bens das candidaturas deferidas: "
        f"{len(assets)}"
    )

    print(
        "Candidaturas com bens declarados: "
        f"{assets['SQ_CANDIDATO'].nunique()}"
    )

    print(
        "Candidaturas deferidas: "
        f"{len(candidates)}"
    )

    print(
        "Registros após o JOIN: "
        f"{len(analytical_data)}"
    )

    invalid_values = (
        assets["VR_BEM_CANDIDATO"]
        .isna()
        .sum()
    )

    print(
        "Valores de bens ausentes/inválidos: "
        f"{invalid_values}"
    )

    duplicated_assets = assets.duplicated(
        subset=[
            "SQ_CANDIDATO",
            "NR_ORDEM_BEM_CANDIDATO",
        ]
    ).sum()

    print(
        "Bens duplicados por candidato/ordem: "
        f"{duplicated_assets}"
    )

    if len(analytical_data) != len(candidates):
        raise ValueError(
            "O JOIN alterou a quantidade de candidatos."
        )

    if not (
        analytical_data[
            "DS_SITUACAO_JULGAMENTO"
        ]
        .eq("DEFERIDO")
        .all()
    ):
        raise ValueError(
            "O dataset contém candidatura não deferida."
        )

    if analytical_data[
        "SQ_CANDIDATO"
    ].duplicated().any():
        raise ValueError(
            "Existem candidatos duplicados após o JOIN."
        )

    print(
        "Validação do dataset patrimonial: OK"
    )


def save_dataframe(
    df: pd.DataFrame,
    path: Path,
) -> None:
    """Salva um DataFrame processado."""

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        path,
        index=False,
        encoding="utf-8",
    )

    print(
        f"Arquivo salvo em: {path}"
    )


def main() -> None:
    assets = load_assets(
        RAW_ASSETS_PATH
    )

    candidates = load_candidates(
        CANDIDATES_PATH
    )

    assets = select_asset_columns(
        assets
    )

    assets = filter_candidate_assets(
        assets,
        candidates,
    )

    assets = clean_special_values(
        assets
    )

    assets = convert_asset_values(
        assets
    )

    assets = convert_dates(
        assets
    )

    asset_summary = aggregate_assets(
        assets
    )

    analytical_data = merge_candidates_assets(
        candidates,
        asset_summary,
    )

    analytical_data = add_asset_metrics(
        analytical_data
    )

    validate_assets(
        assets,
        candidates,
        analytical_data,
    )

    save_dataframe(
        assets,
        PROCESSED_ASSETS_PATH,
    )

    save_dataframe(
        analytical_data,
        ANALYTICAL_DATA_PATH,
    )


if __name__ == "__main__":
    main()