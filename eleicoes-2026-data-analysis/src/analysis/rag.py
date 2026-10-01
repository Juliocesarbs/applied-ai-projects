"""Pipeline RAG para análise dos planos de governo."""

from pathlib import Path

import numpy as np
import pandas as pd
import requests

from src.analysis.semantic_search import semantic_search


OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"

DEFAULT_GENERATION_MODEL = "gemma3:4b"

DEFAULT_EMBEDDINGS_DIR = Path(
    "data/processed/government_plans/embeddings"
)


def generate_response(
    prompt: str,
    model: str = DEFAULT_GENERATION_MODEL,
) -> str:
    """Gera resposta utilizando um modelo local via Ollama."""

    if not prompt.strip():
        raise ValueError(
            "O prompt não pode estar vazio."
        )

    response = requests.post(
        OLLAMA_GENERATE_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0,
                "seed": 42,
            },
        },
        timeout=300,
    )

    if not response.ok:
        raise RuntimeError(
            "Erro na geração: "
            f"{response.status_code} - {response.text}"
        )

    data = response.json()

    generated_text = data.get(
        "response",
        "",
    ).strip()

    if not generated_text:
        raise RuntimeError(
            "Ollama retornou uma resposta vazia."
        )

    return generated_text


def build_context(
    results: pd.DataFrame,
) -> str:
    """Constrói o contexto com os chunks recuperados."""

    if results.empty:
        return ""

    context_parts = []

    for index, row in results.iterrows():
        source_id = index + 1

        context_parts.append(
            (
                f"[FONTE {source_id}]\n"
                f"Candidato: "
                f"{row['NM_URNA_CANDIDATO']}\n"
                f"Partido: "
                f"{row['SG_PARTIDO']}\n"
                f"Chunk: "
                f"{row['CHUNK_ID']}\n"
                f"Texto:\n"
                f"{row['TEXTO_CHUNK']}"
            )
        )

    return "\n\n".join(
        context_parts
    )


def build_prompt(
    query: str,
    context: str,
) -> str:
    """Constrói o prompt utilizado pelo RAG."""

    return f"""
Você analisa documentos de planos de governo.

Responda à pergunta usando somente as informações
presentes nas fontes abaixo.

Para cada candidato relevante:

CANDIDATO (PARTIDO) [FONTE X]
- Liste de forma objetiva as informações encontradas.

Regras:
- Responda em português.
- Use apenas informações explicitamente presentes nas fontes.
- Não complete frases cortadas.
- Não faça avaliações, recomendações ou rankings.
- Não misture informações de candidatos diferentes.
- Sempre indique [FONTE X].

Se as fontes não contiverem nenhuma informação
relacionada à pergunta, responda apenas:
"Não há evidência suficiente nas fontes recuperadas."

Pergunta:
{query}

Fontes:
{context}

Resposta:
""".strip()


def load_rag_data(
    embeddings_dir: Path = DEFAULT_EMBEDDINGS_DIR,
) -> tuple[pd.DataFrame, np.ndarray]:
    """Carrega chunks e embeddings persistidos."""

    chunks_path = (
        embeddings_dir
        / "chunks_metadata.csv"
    )

    embeddings_path = (
        embeddings_dir
        / "embeddings.npy"
    )

    if not chunks_path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {chunks_path}"
        )

    if not embeddings_path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {embeddings_path}"
        )

    chunks = pd.read_csv(
        chunks_path
    )

    embeddings = np.load(
        embeddings_path
    )

    if embeddings.ndim != 2:
        raise ValueError(
            "A matriz de embeddings deve possuir "
            "duas dimensões."
        )

    if len(chunks) != embeddings.shape[0]:
        raise ValueError(
            "Quantidade de chunks diferente "
            "da quantidade de embeddings."
        )

    return chunks, embeddings


class RAGPipeline:
    """Pipeline de recuperação e geração."""

    def __init__(
        self,
        embeddings_dir: Path = DEFAULT_EMBEDDINGS_DIR,
        generation_model: str = DEFAULT_GENERATION_MODEL,
    ) -> None:
        self.generation_model = generation_model

        (
            self.chunks,
            self.embeddings,
        ) = load_rag_data(
            embeddings_dir
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> pd.DataFrame:
        """Recupera evidências semanticamente relevantes."""

        return semantic_search(
            query=query,
            chunks=self.chunks,
            embeddings=self.embeddings,
            top_k=top_k,
        )

    def query(
        self,
        query: str,
        top_k: int = 3,
    ) -> tuple[str, pd.DataFrame]:
        """Executa recuperação e geração."""

        results = self.retrieve(
            query=query,
            top_k=top_k,
        )

        context = build_context(
            results
        )

        prompt = build_prompt(
            query=query,
            context=context,
        )

        response = generate_response(
            prompt=prompt,
            model=self.generation_model,
        )

        return response, results