import os
import time

from openai import OpenAI

openai_api_key = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def embed_query(query_text):
    response = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=[query_text]
    )
    return response.data[0].embedding


def call_completion(prompt):
    completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return completion.choices[0].message.content.strip()


def get_embeddings(texts, batch_size=100):
    embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=batch
        )
        embeddings.extend([data.embedding for data in response.data])
        time.sleep(0.5)  # avoid OpenAI API rate limits

    return embeddings


def filter_relevant_questions(main_question, candidate_questions, num_questions=3):
    filter_prompt = f"""
    Main Question:
    {main_question}

    Candidate Questions:
    {'; '.join(candidate_questions)}

    Your task is to select EXACTLY {num_questions} questions from the candidate list that are most relevant and closely related to the main question. 
    Return them clearly numbered from 1 to {num_questions}. Provide only exact original questions.

    Relevant Questions:
    """

    completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": filter_prompt
        }]
    )
    response = completion.choices[0].message.content.strip()

    relevant_questions = [q.split('.', 1)[-1].strip() for q in response.split("\n") if q.strip()]
    return relevant_questions
