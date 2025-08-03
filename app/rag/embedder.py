import torch.nn.functional as F
import torch
from transformers import AutoTokenizer, AutoModel
import uuid
import os


model_name_or_path = 'Alibaba-NLP/gte-multilingual-base'
tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
model = AutoModel.from_pretrained(model_name_or_path, trust_remote_code=True)
model.eval()


def generate_embeddings(texts: list[str] | str) -> torch.Tensor:
    inputs = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors='pt'
    )

    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state[:, 0]
        embeddings = F.normalize(embeddings, p=2, dim=1)
    
    return embeddings


def embedd_chunks(processed_chunks):
    for item in processed_chunks:
        embeddings = []

        for chunk in item["chunks"]:
            joined_sentences = " ".join(chunk)

            emb = generate_embeddings(joined_sentences)

            emb_np = emb[0].cpu().numpy()
            embeddings.append(emb_np)

        item["embeddings"] = embeddings
    
    return processed_chunks


def generate_chunk_entries(processed_contents):
    chunk_entries = []

    for item in processed_contents:
        page_num = item["page_number"]

        for idx, chunk in enumerate(item["chunks"]):
            chunk_dict = {}
            chunk_text = " ".join(chunk)
            token_count = len(chunk_text)/4

            chunk_dict["chunk_id"] = str(uuid.uuid4())
            chunk_dict["page_num"] = int(page_num)
            chunk_dict["text"] = chunk_text
            chunk_dict["embedding"] = item["embeddings"][idx]

            metadata = {
                "char_count": len(chunk_text),
                "sentence_count": len(chunk),
                "token_count": token_count,
            }

            chunk_dict["metadata"] = metadata

            chunk_entries.append(chunk_dict)

    return chunk_entries



def embedding_pipeline(processed_chunks):
    processed_chunks = embedd_chunks(processed_chunks)
    chunk_entries = generate_chunk_entries(processed_chunks)

    return chunk_entries