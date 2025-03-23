from engine.engine_qa import get_chat_response

if __name__ == "__main__":
    user_question = "미성년자도 판매 회원 등록이 가능한가요?"
    # user_question = "오늘 저녁에 여의도 가려는데 맛집 추천좀 해줄래?"
    response = get_chat_response(user_question)

    print("📌 챗봇 응답 📌\n", response["answer"])
    print("\n💡 추가로 이런 내용을 물어보시는 건 어떠신가요?")
    for idx, suggestion in enumerate(response["suggestions"], start=1):
        print(f"   {idx}. {suggestion}")
