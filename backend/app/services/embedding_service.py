from openai import OpenAI

from app.config import settings


EMBEDDING_MODEL = "text-embedding-3-small"

#Create OpenAI embedding service


def get_openai_client() -> OpenAI:
    if not settings.openai_api_key:
        raise ValueError("OpenAI API key is missing.")

    return OpenAI(api_key=settings.openai_api_key)


def generate_embedding(text: str) -> list[float]:
    client = get_openai_client()

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )

    return response.data[0].embedding


def generate_embeddings_for_chunks(chunks: list[dict]) -> list[dict]:
    embedded_chunks = []

    for chunk in chunks:
        embedding = generate_embedding(chunk["chunk_text"])

        embedded_chunks.append(
            {
                **chunk,
                "embedding": embedding,
                "embedding_model": EMBEDDING_MODEL,
            }
        )

    return embedded_chunks