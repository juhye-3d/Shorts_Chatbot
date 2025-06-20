import streamlit as st
from openai import OpenAI

# 앱 제목 및 설명
st.title("🎬 유튜브 쇼츠 콘텐츠 생성기 챗봇")
st.write(
    "주제만 입력하면 쇼츠 콘텐츠의 제목부터 편집 팁, 해시태그, 썸네일 문구까지 자동 생성됩니다! "
    "🎯 타겟과 🎨 톤도 자유롭게 설정하세요."
)

# OpenAI API 키 입력
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("진행을 위해 API 키를 입력해주세요.", icon="🔑")
    st.stop()

# OpenAI 클라이언트 생성
client = OpenAI(api_key=openai_api_key)

# 모드 선택
mode = st.selectbox("모드를 선택하세요", ["기본 대화", "유튜브 쇼츠 생성"])

# 타겟 & 톤 선택
if mode == "유튜브 쇼츠 생성":
    target = st.selectbox("🎯 타겟층", ["10대", "20대", "직장인", "엄마들", "전 연령"])
    tone = st.selectbox("🎨 톤 앤 매너", ["유쾌한", "감성적인", "진지한", "믿음직한", "힙한", "깔끔한"])

# 시스템 메시지 설정
if "messages" not in st.session_state:
    st.session_state.messages = []
    if mode == "유튜브 쇼츠 생성":
        st.session_state.messages.append({
            "role": "system",
            "content": (
                f"당신은 유튜브 쇼츠 콘텐츠 기획 전문가입니다.\n"
                f"타겟층은 '{target}', 톤은 '{tone}'입니다.\n\n"
                "사용자가 주제를 입력하면 아래 항목을 작성하세요:\n"
                "1. 🎬 제목 (눈길 끄는 제목)\n"
                "2. 🧲 후킹 스크립트 (첫 3초에 시선 끄는 문장)\n"
                "3. 📄 콘텐츠 구성 (3단계 핵심 흐름)\n"
                "4. ✂️ 편집 포인트 (효과, 전환, 속도 등)\n"
                "5. 🔖 해시태그 (5개)\n"
                "6. 🖼️ 썸네일 문구 (짧고 임팩트 있게)\n\n"
                "모든 항목은 타겟과 톤에 맞게 작성하세요."
            )
        })

# 이전 메시지 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 받기
if prompt := st.chat_input("주제를 입력하세요 (예: 아침 루틴, 공부법 등)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # GPT 응답 생성
    stream = client.chat.completions.create(
        model="gpt-4o",
        messages=st.session_state.messages,
        stream=True,
    )

    # 응답 출력 및 저장
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

# 저장 버튼
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
    last_response = st.session_state.messages[-1]["content"]
    st.download_button("💾 답변 저장하기", last_response, file_name="shorts_idea.txt")
