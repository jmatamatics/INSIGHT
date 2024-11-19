

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
st.title('INSIGHT')
st.subheader('AI Wellness Coach for Philosophical and Practical Guidance')



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




# to access audio in proper format
def callback():
    if st.session_state.my_recorder_output:
        audio_bytes = st.session_state.my_recorder_output['bytes']
        # Specify the path and filename to save the file
        file_path = 'client_audio.wav'
        # Writing the bytes to a file
        with open(file_path, 'wb') as f:
            f.write(audio_bytes)


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


p =st.chat_input("Flow")
if p:
    response = ai_agent(p)
    st.write_stream(stream_data)
elif record:
    client_audio_prompt =transcribe_audio('client_audio.wav')
    response = ai_agent(client_audio_prompt)
    st.write_stream(stream_data)












