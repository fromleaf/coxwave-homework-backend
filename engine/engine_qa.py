from coxwave.utils import (
    util_embedding,
    util_openai
)

COLLECTION_NAVER_SMARTSTORE_FAQ = "naver_smartstore_faq"
SIMILARITY_THRESHOLD = 0.28
DEFAULT_PROMPT_FORM = """
You are a helpful assistant specialized in smart store FAQs. 
Answer the user's current question clearly and concisely based on the provided context and previous conversation (if exists).
Especially pay attention to the most relevant FAQ provided. 

Context and previous conversation:
{full_context}

User Question:
{user_input}

Answer:
"""


def filter_questions_by_threshold(candidate_hits, threshold=0.2):
    relevant_questions = []
    for hit in candidate_hits:
        distance = hit.distance
        if distance <= threshold:
            relevant_questions.append(hit.entity.get('question'))
    return relevant_questions


def get_chat_response(user_input, context_history=None, num_suggestions=3):
    collection = util_embedding.get_or_create_collection(COLLECTION_NAVER_SMARTSTORE_FAQ)

    query_embedding = util_openai.embed_query(user_input)

    retrieved_docs = util_embedding.get_query(collection, query_embedding, top_k=10)

    if not util_embedding.is_relevant(retrieved_docs, SIMILARITY_THRESHOLD):
        return {
            "answer": "저는 스마트스토어 FAQ를 위한 챗봇입니다. 스마트스토어에 대한 질문을 부탁드립니다.",
            "suggestions": []
        }

    main_answer = None
    main_question = None
    context_documents = []
    candidate_questions = []
    candidate_hits = []
    for idx, hits in enumerate(retrieved_docs):
        for j, hit in enumerate(hits):
            question = hit.entity.get('question')
            answer = hit.entity.get('answer')
            if idx == 0 and j == 0:
                main_answer = answer
                main_question = question
            else:
                candidate_questions.append(question)
                candidate_hits.append(hit)
            context_documents.append(f"Question: {question}\nAnswer: {answer}")

    # suggested_questions = util_openai.filter_relevant_questions(main_question, candidate_questions)[:num_suggestions]
    suggested_questions = filter_questions_by_threshold(candidate_hits, threshold=0.25)[:num_suggestions]

    full_context = ""
    if context_history:
        full_context += "\n".join(context_history) + "\n\n"

    full_context += f"Most Relevant FAQ:\nQuestion: {main_question}\nAnswer: {main_answer}\n\n"
    full_context += "Other Related FAQ:\n" + "\n".join(context_documents[1:])

    generated_answer = util_openai.call_completion(
        DEFAULT_PROMPT_FORM.format(
            full_context=full_context,
            user_input=user_input
        )
    )

    return {
        "answer": generated_answer,
        "suggestions": suggested_questions
    }
