# pip install streamlit-chat
# pip install streamlit-audiorecorder

import streamlit as st
from audiorecorder import audiorecorder
import openai_api
from streamlit_chat import message as msg

def main():
    st.set_page_config(
        page_title = 'Voice Chatbot',
        layout = 'wide'
    )
    st.header('Voice Chatbot')

    with st.expander('Voice Chatbot 프로그램을 사용하는 방법', expanded = False): #
        st.write(
            '''
            1. 녹음하기 버튼을 눌러 질문을 녹음합니다.
            2. 녹음이 완료되면 Whisper 모델을 이용해 자동으로 음성을 텍스트로 변환 후 LLM에 질의합니다.
            3. LLM의 응답을 다시 TTS 모델을 통해 음성으로 변환하고 이를 사용자에게 전달합니다.
            4. LLM은 OpenAI사의 GPT모델을 사용합니다.
            5. 모든 질문 / 답변은 텍스트로 제공합니다.
            '''
        )

    # session state 초기화
    # messages : LLM 질의를 위한 대화 내역
    # check_reset : 초기화를 위한 flag
    system_instruction = '당신은 친절한 챗봇입니다.'

    if 'messages' not in st.session_state:
        system_instruction = '당신은 친절한 챗봇입니다.'
        st.session_state['messages'] = [
            {'role' : 'system', 'content' : system_instruction}
        ]

    if 'check_reset' not in st.session_state:
        st.session_state['check_reset'] = False

    with st.sidebar:
        model = st.radio(label = 'GPT 모델', options = ['gpt-3.5-turbo', 'gpt-4-turbo', 'gpt-4o'])
        print(model)

        if st.button(label = '초기화'):
            st.session_state['messages'] = [
                {'role' : 'system', 'content' : system_instruction}
            ]
            st.session_state['check_reset'] = True # 화면 정리

    col1, col2 = st.columns(2)
    with col1:
        st.subheader('녹음하기')

        audio = audiorecorder()
        print(audio)

        if (audio.duration_seconds > 0) and (st.session_state['check_reset'] == False):
            # 화면상의 재생기능
            st.audio(audio.export().read())
            # 사용자음성에서 텍스트 추출
            query = openai_api.stt(audio)
            print(f'질문 : {query}')
            # LLM 질의
            st.session_state['messages'].append({'role' : 'user', 'content' : query})
            response = openai_api.ask_gpt(st.session_state['messages'], model)
            print(f'대답 : {response}')
            # 음성으로 변환
            audio_tag = openai_api.tts(response)
            st.html(audio_tag)

    with col2:
        st.subheader('질문/답변')

        if (audio.duration_seconds > 0) and (st.session_state['check_reset'] == False):
            for i, message in enumerate(st.session_state['messages']):
                role = message['role']
                content = message['content']
                if role == 'user':
                    msg(content, is_user = True, key = str(i), avatar_style = 'big_smile')
                elif role == 'assistant':
                    msg(content, is_user = False, key = str(i))
        else:
            # 초기화 버튼을 누르면 화면이 정리되고 다시 check_reset 원상복구
            st.session_state['check_reset'] = False




if __name__ == '__main__':
    main()