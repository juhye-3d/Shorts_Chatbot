import streamlit as st
from openai import OpenAI

st.title("🎬 유튜브 쇼츠 콘텐츠 생성기 챗봇")
st.write("쇼츠 콘텐츠 핵심 포맷(제목/후킹/구성/편집/해시태그/썸네일)으로만 결과를 받고 싶다면 아래 옵션을 설정 후 주제를 입력하세요.")

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
        st.session_state.messages.append({
            "role": "system",
            "content": (
                f"너는 유튜브 쇼츠 콘텐츠 기획 전문가야. 타겟은 '{target}', 톤은 '{tone}'야.\n"
                "사용자가 주제를 입력하면 아래와 같은 형식으로만 출력해야 해. **절대 설명문, 장황한 문장, 서론/결론 없이!**\n"
                "반드시 아래의 마크다운 포맷만, 항목별로 한눈에 띄게:\n"
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
        })
    st.session_state.mode_prev = mode
    st.session_state.target_prev = target
    st.session_state.tone_prev = tone

# 기존 메시지 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("주제를 입력하세요 (예: 아침 루틴, 공부법 등)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # GPT 응답 생성 (스트리밍)
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
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
