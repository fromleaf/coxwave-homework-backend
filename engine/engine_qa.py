from coxwave import const
from coxwave.const import messages
from coxwave.utils import (
    util_embedding,
    util_openai
)

DEFAULT_PROMPT_FORM = """
You are a helpful assistant specialized in smart store FAQs. 
Answer the user's current question clearly and concisely based on the provided context and previous conversation (if exists).
Especially pay attention to the most relevant FAQ provided. 

Context and previous conversation:
{full_context}

User Question:
{user_question}

Answer:
"""
THRESHOLD_QA_SIMILARITY = 0.28
THRESHOLD_CANDIDATE_HITS_SIMILARITY = 0.25


def get_naver_smartstore_qa_response(user_question, context_history=None, num_suggestions=3):
    collection = util_embedding.get_or_create_collection(const.COLLECTION_NAVER_SMARTSTORE_FAQ)

    query_embedding = util_openai.embed_query(user_question)

    retrieved_docs = util_embedding.get_query(collection, query_embedding, top_k=10)

    if not util_embedding.is_relevant(retrieved_docs, THRESHOLD_QA_SIMILARITY):
        return {
            "answer": messages.CHATBOT_NAVER_SMARTSTORE_ANSWER_FOR_NOT_RELEVANT_MESSAGE,
            "suggestions": []
        }

    main_answer = None
    main_question = None
    context_documents = []
    # candidate_questions = []
    candidate_hits = []
    for idx, hits in enumerate(retrieved_docs):
        for j, hit in enumerate(hits):
            question = hit.entity.get(const.KEY_QUESTION)
            answer = hit.entity.get(const.KEY_ANSWER)
            if idx == 0 and j == 0:
                main_answer = answer
                main_question = question
            else:
                # candidate_questions.append(question)
                candidate_hits.append(hit)
            context_documents.append(f"Question: {question}\nAnswer: {answer}")

    # suggested_questions = util_openai.filter_relevant_questions(
    #     main_question,
    #     candidate_questions
    # )[:num_suggestions]
    suggested_questions = util_embedding.filter_by_threshold(
        candidate_hits,
        filter_key=const.KEY_QUESTION,
        threshold=THRESHOLD_CANDIDATE_HITS_SIMILARITY
    )[:num_suggestions]

    full_context = ""
    if context_history:
        full_context = "Previous conversation:\n"
        full_context += "\n".join(context_history) + "\n\n"

    full_context += f"Most Relevant FAQ:\nQuestion: {main_question}\nAnswer: {main_answer}\n\n"
    full_context += "Other Related FAQ:\n" + "\n".join(context_documents[1:])

    generated_answer = util_openai.call_completion(
        DEFAULT_PROMPT_FORM.format(
            full_context=full_context,
            user_question=user_question
        )
    )

    return {
        "answer": generated_answer,
        "suggestions": suggested_questions
    }
