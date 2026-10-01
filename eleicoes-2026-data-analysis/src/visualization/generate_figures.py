from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROCESSED_DIR = Path("data/processed")
EMBEDDINGS_DIR = PROCESSED_DIR / "government_plans" / "embeddings"
OUTPUT_DIR = Path("outputs/figures")


def configure_plots():
    plt.rcParams.update(
        {
            "figure.figsize": (10, 6),
            "font.size": 11,
            "axes.titlesize": 15,
            "axes.labelsize": 11,
        }
    )


def save_figure(filename):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename

    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()

    print(f"Figura salva: {path}")


def generate_candidate_age_figure():
    path = PROCESSED_DIR / "candidatos_deferidos_2026.csv"
    df = pd.read_csv(path)

    ages = df["NR_IDADE_DATA_POSSE"].dropna()

    plt.figure()
    plt.hist(ages, bins=6, edgecolor="white")

    plt.title("Distribuição de idade das candidaturas")
    plt.xlabel("Idade na data da posse")
    plt.ylabel("Número de candidaturas")

    save_figure("candidate_age_distribution.png")


def generate_declared_assets_figure():
    path = PROCESSED_DIR / "candidatos_deferidos_2026_com_patrimonio.csv"
    df = pd.read_csv(path)

    data = (
        df[["NM_URNA_CANDIDATO", "SG_PARTIDO", "VL_TOTAL_BENS"]]
        .dropna(subset=["VL_TOTAL_BENS"])
        .sort_values("VL_TOTAL_BENS")
        .copy()
    )

    data["LABEL"] = (
        data["NM_URNA_CANDIDATO"].astype(str)
        + " ("
        + data["SG_PARTIDO"].astype(str)
        + ")"
    )

    data["VL_TOTAL_BENS_MILHOES"] = data["VL_TOTAL_BENS"] / 1_000_000

    plt.figure(figsize=(11, 7))
    plt.barh(
        data["LABEL"],
        data["VL_TOTAL_BENS_MILHOES"],
    )

    plt.title("Bens declarados ao TSE por candidatura")
    plt.xlabel("Valor total declarado (R$ milhões)")
    plt.ylabel("")

    save_figure("declared_assets.png")


def generate_retrieval_figure():
    baseline_path = EMBEDDINGS_DIR / "retrieval_evaluation_1000_150.csv"
    final_path = EMBEDDINGS_DIR / "retrieval_evaluation_500_75.csv"

    baseline = pd.read_csv(baseline_path)
    final = pd.read_csv(final_path)

    baseline_precision = baseline["RELEVANTE"].astype(int).mean()
    final_precision = final["RELEVANTE"].astype(int).mean()

    labels = ["1000 / 150", "500 / 75"]
    values = [baseline_precision, final_precision]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values)

    plt.title("Avaliação do retrieval")
    plt.xlabel("Chunk size / overlap")
    plt.ylabel("Precision@5")
    plt.ylim(0, 1.08)

    for bar, value in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.015,
            f"{value:.3f}",
            ha="center",
        )

    save_figure("retrieval_evaluation.png")

def calculate_rag_metrics(path):
    df = pd.read_csv(path)

    columns = [
        "GROUNDED",
        "CITACAO",
        "PORTUGUES",
        "SEM_AVALIACAO",
    ]

    if df[columns].isna().any().any():
        raise ValueError(
            f"Existem avaliações RAG não preenchidas em: {path}"
        )

    return {
        "Grounding": df["GROUNDED"].astype(int).mean(),
        "Citação": df["CITACAO"].astype(int).mean(),
        "Português": df["PORTUGUES"].astype(int).mean(),
        "Sem avaliação": df["SEM_AVALIACAO"].astype(int).mean(),
    }

def generate_rag_figure():
    llama_path = EMBEDDINGS_DIR / "rag_evaluation_llama3.2_3b.csv"
    gemma_path = EMBEDDINGS_DIR / "rag_evaluation_gemma3_4b.csv"

    llama = calculate_rag_metrics(llama_path)
    gemma = calculate_rag_metrics(gemma_path)

    metrics = list(llama.keys())

    comparison = pd.DataFrame(
        {
            "Llama 3.2 3B": [llama[m] for m in metrics],
            "Gemma 3 4B": [gemma[m] for m in metrics],
        },
        index=metrics,
    )

    ax = comparison.plot(
        kind="bar",
        figsize=(10, 6),
    )

    ax.set_title("Conformidade das respostas do RAG")
    ax.set_xlabel("")
    ax.set_ylabel("Taxa de conformidade")
    ax.set_ylim(0, 1.1)

    plt.xticks(rotation=0)
    plt.legend(title="Modelo")

    for container in ax.containers:
        ax.bar_label(
            container,
            labels=[f"{value:.0%}" for value in container.datavalues],
            padding=3,
        )

    save_figure("rag_evaluation.png")


def main():
    configure_plots()

    print("Gerando visualizações...")

    generate_candidate_age_figure()
    generate_declared_assets_figure()
    generate_retrieval_figure()
    generate_rag_figure()

    print("Visualizações concluídas.")


if __name__ == "__main__":
    main()