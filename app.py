

from dotenv import load_dotenv
import streamlit as st
from streamlit_mic_recorder import mic_recorder
import os
import time
import re
from agents import *



# Load environment variables from .env file
load_dotenv()

# access the environment variable
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI()



st.image('med3.png',use_column_width= True)
st.title('Insight')
st.subheader('AI Wellness Coach for Philosophical and Practical Guidance')











# to access audio in proper format
def callback():
    if st.session_state.my_recorder_output:
        audio_bytes = st.session_state.my_recorder_output['bytes']
        #st.audio(audio_bytes)
        # Specify the path and filename to save the file
        file_path = 'client_audio.wav'
        # Writing the bytes to a file
        with open(file_path, 'wb') as f:
            f.write(audio_bytes)
        #client_audio_prompt =transcribe_audio(file_path)
       # st.write(client_audio_prompt)

#location matters
record = mic_recorder(
    start_prompt="Start recording",
    stop_prompt="Stop recording",
    just_once=False,
    use_container_width=False,
    format="wav",
    callback=callback,
    args=(),
    kwargs={},
    key='my_recorder'
)












def stream_data():
    words = response.split()  # Split the response into words
    last_index = len(words) - 1  # Index of the last word
    positions = [m.start() for m in re.finditer(r'\S+', response)]  # Start positions of each word
    
    for i, word in enumerate(words):
        # Yield the word followed by the appropriate spacing or newline
        if i < last_index:
            # Check the gap between the end of this word and the start of the next word
            gap = response[positions[i] + len(word):positions[i+1]]
            yield word + gap
        else:
            # Last word, just return the word
            yield word
        time.sleep(0.02)  # Delay to simulate streaming





#human_input=st.text_input("jojioij")
if record:
    client_audio_prompt =transcribe_audio('client_audio.wav')
    response = ai_agent(client_audio_prompt)
    st.write_stream(stream_data)
    audio(response)




# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["content"].endswith('png'):
            st.image('generated_image.png', caption='Your Image', width =1024, use_column_width= False)
        else:
            st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"),st.spinner(' '):
        response = ai_agent(prompt)
        st.write_stream(stream_data)
    #Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
elif record:
    client_audio_prompt =transcribe_audio('client_audio.wav')
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": client_audio_prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(client_audio_prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"),st.spinner(' '):
        response = ai_agent(client_audio_prompt)
        #st.write(response)
        st.write_stream(stream_data)
        audio(response)


    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})












 #os.remove('client_audio.wav')
#uploaded_files = st.file_uploader("upload", type=['wav', 'mp3'] accept_multiple_files=True)

