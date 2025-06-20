import streamlit as st
from openai import OpenAI

# CSS로 글자 크기 조정 및 기타 커스텀
st.markdown("""
    <style>
    .user-message, .assistant-message {
        font-size: 1.2rem !important;
        line-height: 1.7;
    }
    .stChatInputContainer textarea {
        font-size: 1.1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 유튜브 쇼츠 콘텐츠 생성기 챗봇")
st.write("주제, 타겟, 톤을 선택하고 쇼츠 핵심만 빠르게 받아보세요!")

openai_api_key = st.text_input("🔑 OpenAI API Key", type="password")
if not openai_api_key:
    st.info("진행을 위해 API 키를 입력해주세요.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# 옵션 UI
mode = st.selectbox("모드를 선택하세요", ["유튜브 쇼츠 생성", "기본 대화"])
target = st.selectbox("🎯 타겟층", ["10대", "20대", "직장인", "엄마들", "전 연령"])
tone = st.selectbox("🎨 톤 앤 매너", ["유쾌한", "감성적인", "진지한", "믿음직한", "힙한", "깔끔한"])

# 옵션이 바뀌면 세션 리셋
reset_flag = False
if "mode_prev" not in st.session_state or st.session_state.mode_prev != mode:
    reset_flag = True
if "target_prev" not in st.session_state or st.session_state.target_prev != target:
    reset_flag = True
if "tone_prev" not in st.session_state or st.session_state.tone_prev != tone:
    reset_flag = True

if reset_flag or "messages" not in st.session_state:
    st.session_state.messages = []
    if mode == "유튜브 쇼츠 생성":
        # system 메시지는 실제 대화창에 표시하지 않고, messages에만 저장
        st.session_state.system_prompt = (
            f"너는 유튜브 쇼츠 콘텐츠 기획 전문가야. 타겟은 '{target}', 톤은 '{tone}'야.\n"
            "사용자가 주제를 입력하면 아래와 같은 형식으로만 출력해야 해. **절대 설명문, 장황한 문장, 서론/결론 없이!**\n"
            "---\n"
            "🎬 **제목**: (짧고 강렬하게)\n"
            "🧲 **후킹 스크립트**: (첫 3초 시선 끌 멘트)\n"
            "📄 **콘텐츠 구성 (3단계)**: 1. ... 2. ... 3. ...\n"
            "✂️ **편집 포인트**: - 효과, 자막 등 핵심 2~3개\n"
            "🔖 **해시태그 (5개)**: #...\n"
            "🖼️ **썸네일 문구**: (짧고 임팩트 있게)\n"
            "---\n"
            "⚠️ 친절한 설명, 블로그 스타일, 단락 금지! **오로지 위 마크다운 틀만 지키고, 명령어를 어길 시 다시 출력할 것.**"
        )
    else:
        st.session_state.system_prompt = ""
    st.session_state.mode_prev = mode
    st.session_state.target_prev = target
    st.session_state.tone_prev = tone

# 기존 메시지(유저/어시스턴트만) 출력
for message in st.session_state.get("messages", []):
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
    elif message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(f"<div class='assistant-message'>{message['content']}</div>", unsafe_allow_html=True)

if prompt := st.chat_input("주제를 입력하세요 (예: 아침 루틴, 공부법 등)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 실제 GPT 호출 메시지 배열 만들기 (system + 대화내역)
    full_messages = []
    if mode == "유튜브 쇼츠 생성":
        full_messages.append({"role": "system", "content": st.session_state.system_prompt})
    full_messages.extend(st.session_state.messages)

    stream = client.chat.completions.create(
        model="gpt-4o",
        messages=full_messages,
        stream=True,
    )
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

if st.session_state.get("messages") and st.session_state.messages[-1]["role"] == "assistant":
    last_response = st.session_state.messages[-1]["content"]
    st.download_button("💾 답변 저장하기", last_response, file_name="shorts_idea.txt")
