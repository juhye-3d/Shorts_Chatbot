import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("💬 JH-Chatbot")
st.write(
    "OpenAI의 GPT-4.0-mini 모델을 활용한 응답 챗봇입니다. "
    "API 키를 입력하고 아래 모드를 선택해 시작하세요! [API 키 받기](https://platform.openai.com/account/api-keys) "
    "🔍 [튜토리얼 링크](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)"
)

# ✅ 모드 선택 (항상 UI에 표시)
mode = st.selectbox("모드를 선택하세요", ["기본 대화", "유튜브 쇼츠 생성", "블로그 요약", "이메일 작성"])

# ✅ API 키 입력
openai_api_key = st.text_input("OpenAI API Key", type="password")

if not openai_api_key:
    st.info("진행을 위해 OpenAI API 키를 입력해주세요.", icon="🗝️")

else:
    client = OpenAI(api_key=openai_api_key)

    # ✅ 메시지 세션 초기화 + 선택 모드 반영
    if "messages" not in st.session_state:
        st.session_state.messages = []

        if mode == "유튜브 쇼츠 생성":
            st.session_state.messages.append({
                "role": "system",
                "content": "당신은 유튜브 쇼츠 기획 전문가입니다. 사용자가 주제를 주면 제목, 후킹 스크립트, 편집 포인트를 제안하세요."
            })
        elif mode == "블로그 요약":
            st.session_state.messages.append({
                "role": "system",
                "content": "당신은 전문 요약가입니다. 사용자가 블로그 글을 붙여넣으면 핵심 요약을 3문장 이내로 작성하세요."
            })
        elif mode == "이메일 작성":
            st.session_state.messages.append({
                "role": "system",
                "content": "당신은 프로페셔널 이메일 비서입니다. 사용자의 요청을 바탕으로 자연스럽고 정중한 이메일을 작성하세요."
            })

    # ✅ 기존 메시지 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ✅ 채팅 입력 필드
    if prompt := st.chat_input("무엇을 도와드릴까요?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # ✅ GPT 응답 생성
        stream = client.chat.completions.create(
            model="gpt-4.0-mini",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # ✅ 마지막 응답 저장 버튼
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
        last_response = st.session_state.messages[-1]["content"]
        st.download_button("💾 답변 저장하기", last_response, file_name="chat_response.txt")
