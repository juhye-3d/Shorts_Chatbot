import streamlit as st
from openai import OpenAI

# 앱 제목 및 설명
st.title("🎬 유튜브 쇼츠 콘텐츠 생성기 챗봇")
st.write(
    "주제만 입력하면 쇼츠 콘텐츠의 제목부터 후킹, 구성, 편집 포인트, 해시태그, 썸네일 문구까지 자동 생성됩니다!"
)

# OpenAI API Key 입력
openai_api_key = st.text_input("🔑 OpenAI API Key", type="password")
if not openai_api_key:
    st.info("진행을 위해 API 키를 입력해주세요.")
    st.stop()

# OpenAI 클라이언트 설정
client = OpenAI(api_key=openai_api_key)

# 모드 선택
mode = st.selectbox("모드를 선택하세요", ["기본 대화", "유튜브 쇼츠 생성"])

# 타겟과 톤 (쇼츠 모드일 경우만)
if mode == "유튜브 쇼츠 생성":
    target = st.selectbox("🎯 타겟층", ["10대", "20대", "직장인", "엄마들", "전 연령"])
    tone = st.selectbox("🎨 톤 앤 매너", ["유쾌한", "감성적인", "진지한", "믿음직한", "힙한", "깔끔한"])

# 모드가 바뀌면 messages 초기화
if "current_mode" not in st.session_state:
    st.session_state.current_mode = mode
elif st.session_state.current_mode != mode:
    st.session_state.messages = []
    st.session_state.current_mode = mode

# system prompt 설정
if "messages" not in st.session_state:
    st.session_state.messages = []

    if mode == "유튜브 쇼츠 생성":
        st.session_state.messages.append({
            "role": "system",
            "content": (
                f"당신은 유튜브 쇼츠 콘텐츠 기획 전문가입니다. 타겟층은 '{target}', 톤은 '{tone}'입니다.\n\n"
                "사용자가 주제를 입력하면 **절대로 설명문 형식이 아닌**, 아래 포맷으로 정확히 출력하세요:\n"
                "---\n"
                "🎬 **제목**:\n(눈길을 끄는 짧은 제목)\n\n"
                "🧲 **후킹 스크립트**:\n(시작 3초 시선 끌 문장)\n\n"
                "📄 **콘텐츠 구성 (3단계)**:\n1. ...\n2. ...\n3. ...\n\n"
                "✂️ **편집 포인트**:\n- 효과, 전환, 자막, 배경음 등\n\n"
                "🔖 **해시태그 (5개)**:\n#...\n\n"
                "🖼️ **썸네일 문구**:\n(짧고 임팩트 있게!)\n"
                "---\n"
                "⚠️ 절대 설명문 없이 위 포맷으로만 출력할 것!"
            )
        })

# 기존 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("주제를 입력하세요 (예: 아침 루틴, 공부법 등)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # GPT 응답 생성 (스트리밍)
    stream = client.chat.completions.create(
        model="gpt-4o",
        messages=st.session_state.messages,
        stream=True,
    )

    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

# 답변 저장
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
    last_response = st.session_state.messages[-1]["content"]
    st.download_button("💾 답변 저장하기", last_response, file_name="shorts_idea.txt")
