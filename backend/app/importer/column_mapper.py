from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)



standard_fields = [

    "chassis number",

    "vehicle weight",

    "container number",

    "bill of lading",

    "cargo type",

    "owner",

    "arrival date"

]



field_embeddings = model.encode(
    standard_fields
)



def detect_column(column_name):

    column_embedding = model.encode(
        [column_name]
    )


    scores = cosine_similarity(
        column_embedding,
        field_embeddings
    )[0]


    best_index = scores.argmax()


    confidence = scores[best_index]


    if confidence < 0.45:

        return None, float(confidence)


    return (
        standard_fields[best_index],
        float(confidence)
    )