import os

from pymilvus import (
    Collection,
    CollectionSchema,
    connections,
    DataType,
    FieldSchema,
    utility
)

from coxwave import const

MILVUS_HOST = os.getenv('MILVUS_HOST', "localhost")
MILVUS_PORT = os.getenv('MILVUS_PORT', "19530")

COLLECTION_FIELD_NAME_EMBEDDING = const.KEY_EMBEDDING
COLLECTION_METRIC_TYPE_L2 = "L2"
COLLECTION_INDEX_TYPE_IVF_FLAT = "IVF_FLAT"

connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)


def get_or_create_collection(collection_name=None):
    if collection_name is None:
        raise ValueError("Collection name is required.")

    if utility.has_collection(collection_name):
        collection = Collection(name=collection_name)
    else:
        schema = CollectionSchema(
            fields=[
                FieldSchema(name=const.KEY_ID, dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name=const.KEY_QUESTION, dtype=DataType.VARCHAR, max_length=2048),
                FieldSchema(name=const.KEY_ANSWER, dtype=DataType.VARCHAR, max_length=32768),
                FieldSchema(name=const.KEY_EMBEDDING, dtype=DataType.FLOAT_VECTOR, dim=1536),
            ],
            description=f"{collection_name} data embeddings"
        )
        collection = Collection(name=collection_name, schema=schema)
        collection.create_index(
            field_name=COLLECTION_FIELD_NAME_EMBEDDING,
            index_params={
                "metric_type": COLLECTION_METRIC_TYPE_L2,
                "index_type": COLLECTION_INDEX_TYPE_IVF_FLAT,
                "params": {
                    "nlist": 128
                }
            }
        )

    return collection


def get_query(collection: Collection, query_embedding, top_k=3):
    collection.load()

    search_params = {
        "metric_type": "L2",
        "params": {
            "nprobe": 10
        }
    }

    results = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        output_fields=['question', 'answer']
    )

    return results


def init_collection(collection_name=None):
    if collection_name is None:
        raise ValueError("Collection name is required.")

    collection = get_or_create_collection(collection_name)
    collection.drop()


def is_relevant(docs=None, threshold=None):
    if docs is None:
        raise ValueError("docs is required.")

    if threshold is None:
        raise ValueError("Threshold is required.")

    for hits in docs:
        if hits is None:
            return False

        for hit in hits:
            distance = hit.distance
            if distance <= threshold:
                return True

    return False


def filter_by_threshold(candidate_hits, filter_key=None, threshold=0.2):
    if filter_key is None:
        raise ValueError("filter_key is required.")

    relevant = []
    for hit in candidate_hits:
        distance = hit.distance
        if distance <= threshold:
            relevant.append(hit.entity.get(filter_key))
    return relevant
