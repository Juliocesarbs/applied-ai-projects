from pathlib import Path

import pandas as pd


RAW_CANDIDATES_PATH = Path(
    "data/raw/consulta_cand_2026/"
    "consulta_cand_2026_BR.csv"
)

RAW_COMPLEMENTARY_PATH = Path(
    "data/raw/consulta_cand_complementar_2026/"
    "consulta_cand_complementar_2026_BR.csv"
)

ALL_RECORDS_PATH = Path(
    "data/processed/registros_presidenciais_2026.csv"
)

ELIGIBLE_CANDIDATES_PATH = Path(
    "data/processed/candidatos_deferidos_2026.csv"
)


CANDIDATE_COLUMNS = [
    "ANO_ELEICAO",
    "DT_ELEICAO",
    "SQ_CANDIDATO",
    "NR_CANDIDATO",
    "NM_CANDIDATO",
    "NM_URNA_CANDIDATO",
    "TP_AGREMIACAO",
    "NR_PARTIDO",
    "SG_PARTIDO",
    "NM_PARTIDO",
    "NM_FEDERACAO",
    "SG_FEDERACAO",
    "NM_COLIGACAO",
    "DS_COMPOSICAO_COLIGACAO",
    "SG_UF_NASCIMENTO",
    "DT_NASCIMENTO",
    "DS_GENERO",
    "DS_GRAU_INSTRUCAO",
    "DS_ESTADO_CIVIL",
    "DS_COR_RACA",
    "DS_OCUPACAO",
]


COMPLEMENTARY_COLUMNS = [
    "SQ_CANDIDATO",
    "NR_IDADE_DATA_POSSE",
    "VR_DESPESA_MAX_CAMPANHA",
    "ST_REELEICAO",
    "ST_DECLARAR_BENS",
    "DS_SITUACAO_CANDIDATO_TOT",
    "ST_CANDIDATO_INSERIDO_URNA",
    "ST_SUBSTITUIDO",
    "SQ_SUBSTITUIDO",
    "DT_ACEITE_CANDIDATURA",
    "DS_SITUACAO_JULGAMENTO",
    "DS_SITUACAO_JULGAMENTO_PLEITO",
]


SPECIAL_TEXT_VALUES = {
    "#NE": pd.NA,
    "#NULO": pd.NA,
}


def load_tse_csv(path: Path) -> pd.DataFrame:
    """Carrega um arquivo CSV disponibilizado pelo TSE."""

    return pd.read_csv(
        path,
        sep=";",
        encoding="latin-1",
    )


def filter_presidential_records(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Mantém somente registros para Presidente."""

    return df[
        df["DS_CARGO"].eq("PRESIDENTE")
    ].copy()


def select_columns(
    df: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:
    """Seleciona somente as colunas necessárias."""

    available_columns = [
        column
        for column in columns
        if column in df.columns
    ]

    return df[available_columns].copy()


def merge_complementary_data(
    candidates: pd.DataFrame,
    complementary: pd.DataFrame,
) -> pd.DataFrame:
    """Adiciona informações complementares aos registros."""

    return candidates.merge(
        complementary,
        on="SQ_CANDIDATO",
        how="left",
        validate="one_to_one",
    )


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


def convert_dates(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Converte campos de data para datetime."""

    df = df.copy()

    date_formats = {
        "DT_ELEICAO": "%d/%m/%Y",
        "DT_NASCIMENTO": "%d/%m/%Y",
    }

    for column, date_format in date_formats.items():
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                format=date_format,
                errors="coerce",
            )

    if "DT_ACEITE_CANDIDATURA" in df.columns:
        df["DT_ACEITE_CANDIDATURA"] = pd.to_datetime(
            df["DT_ACEITE_CANDIDATURA"],
            errors="coerce",
        )

    return df


def add_analysis_status(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Identifica os registros que atendem à regra
    definida para a análise principal.
    """

    df = df.copy()

    df["ST_ELEGIVEL_ANALISE"] = (
        df["DS_SITUACAO_JULGAMENTO"]
        .eq("DEFERIDO")
        & df["ST_SUBSTITUIDO"].ne("S")
    )

    return df


def filter_eligible_candidates(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Mantém somente candidaturas com registro
    deferido para a análise principal.
    """

    return df[
        df["ST_ELEGIVEL_ANALISE"]
    ].copy()


def validate_presidential_records(
    df: pd.DataFrame,
) -> None:
    """Valida o conjunto completo de registros presidenciais."""

    print(
        f"Registros presidenciais encontrados: {len(df)}"
    )

    duplicates = (
        df["SQ_CANDIDATO"]
        .duplicated()
        .sum()
    )

    print(
        f"SQ_CANDIDATO duplicados: {duplicates}"
    )

    print("\nSituação de julgamento:")

    print(
        df["DS_SITUACAO_JULGAMENTO"]
        .value_counts(
            dropna=False
        )
    )

    print("\nSituação de substituição:")

    print(
        df["ST_SUBSTITUIDO"]
        .value_counts(
            dropna=False
        )
    )

    print("\nElegibilidade para análise:")

    print(
        df["ST_ELEGIVEL_ANALISE"]
        .value_counts(
            dropna=False
        )
    )


def validate_eligible_candidates(
    df: pd.DataFrame,
) -> None:
    """Valida o universo utilizado na análise principal."""

    if df.empty:
        raise ValueError(
            "Nenhuma candidatura deferida foi encontrada."
        )

    if df["SQ_CANDIDATO"].duplicated().any():
        raise ValueError(
            "Existem candidatos duplicados no dataset analítico."
        )

    if not (
        df["DS_SITUACAO_JULGAMENTO"]
        .eq("DEFERIDO")
        .all()
    ):
        raise ValueError(
            "Existem registros não deferidos no dataset analítico."
        )

    if (
        df["ST_SUBSTITUIDO"]
        .eq("S")
        .any()
    ):
        raise ValueError(
            "Existem registros substituídos no dataset analítico."
        )

    print(
        "\nCandidaturas deferidas para análise: "
        f"{len(df)}"
    )

    print(
        "Validação do universo analítico: OK"
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
    candidates = load_tse_csv(
        RAW_CANDIDATES_PATH
    )

    complementary = load_tse_csv(
        RAW_COMPLEMENTARY_PATH
    )

    candidates = filter_presidential_records(
        candidates
    )

    candidates = select_columns(
        candidates,
        CANDIDATE_COLUMNS,
    )

    complementary = select_columns(
        complementary,
        COMPLEMENTARY_COLUMNS,
    )

    presidential_records = merge_complementary_data(
        candidates,
        complementary,
    )

    presidential_records = clean_special_values(
        presidential_records
    )

    presidential_records = convert_dates(
        presidential_records
    )

    presidential_records = add_analysis_status(
        presidential_records
    )

    eligible_candidates = filter_eligible_candidates(
        presidential_records
    )

    validate_presidential_records(
        presidential_records
    )

    validate_eligible_candidates(
        eligible_candidates
    )

    save_dataframe(
        presidential_records,
        ALL_RECORDS_PATH,
    )

    save_dataframe(
        eligible_candidates,
        ELIGIBLE_CANDIDATES_PATH,
    )


if __name__ == "__main__":
    main()