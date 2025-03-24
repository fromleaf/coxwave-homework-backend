from coxwave import const
from coxwave.utils import (
    util_file,
    util_openai
)
from coxwave.utils.util_embedding import get_or_create_collection


def _store_data_to_naver_smart_faq_store_collection(collection_name=None, data=None):
    if collection_name is None:
        raise ValueError("Collection name is required.")

    if data is None:
        raise ValueError("Data is required.")

    questions = []
    answers = []
    for key, value in data.items():
        questions.append(key)
        answers.append(value)

    question_embeddings = util_openai.get_embeddings(questions)
    collection = get_or_create_collection(collection_name)
    insert_data = [questions, answers, question_embeddings]

    collection.insert(data=insert_data)
    collection.flush()


def create_naver_smartstore_faq(file_path=None):
    if file_path is None:
        raise ValueError("File path is required.")

    data = util_file.load_pickle_file(file_path)
    _store_data_to_naver_smart_faq_store_collection(const.COLLECTION_NAVER_SMARTSTORE_FAQ, data)
