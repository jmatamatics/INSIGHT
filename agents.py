from langchain.tools import tool #make pydanic function to tool
from langchain.schema.runnable import RunnablePassthrough #takes intiial input and passes it through
from pydantic.v1 import BaseModel, Field # create pydanic function
from langchain.memory import ConversationBufferMemory #memory
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_functions # take messagelog from result1 and put in history
from langchain.prompts import MessagesPlaceholder #to add sratchpasd to message
from langchain_core.utils.function_calling import convert_to_openai_function #convert tool to openai function
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder, #to add sratchpasd to message
)
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
import os
import time
import re
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import streamlit as st


# Load environment variables from .env file
load_dotenv()

# access the environment variable
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI()



def transcribe_audio(audio_file_path):
    with open(audio_file_path, 'rb') as audio_file:
        transcription = client.audio.transcriptions.create(
            model = "whisper-1", 
            file= audio_file,
            response_format="text"
        )
    return transcription





# Define the input schema
class AI(BaseModel):
    human_input: str = Field(..., description="A string that describes what the length and tyoe of meditation.")

@tool(args_schema=AI)
def med_script(human_input):
    """
    You are a meditation teacher. You create scripts of guided breathwork and meditations. 
    Return only the script. If the user does not specify length of time, then create a 5 
    minute script that contains 2000 to 3000 words.  If the user does not specify whether 
    they want breathwork or a meditation, then create a meditation.
    """
    
    sentiment_prompt  =  """You are a meditation teacher. You create scripts of guided breathwork and meditations. Return only the script. If the user does not specify length of time, then create a 5 minute script that contains 2000 to 3000 words.  If the user does not specify whether they want breathwork or a meditation, then create a meditation."""
    chatprompt =ChatPromptTemplate.from_messages([
    ('system', sentiment_prompt),
    ('human', human_input)

    ])
    llm = ChatOpenAI(model='gpt-4', streaming =True) #play with temperature

    chat_llm_chain = LLMChain(
        llm=llm,
        prompt=chatprompt,
       # verbose=True,
       )
    response = chat_llm_chain.predict(human_input=human_input)
    #print(response)
    if len(response) < 200:
        return f'return only the generated script: {response}'
    else:
        audio = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=response,
        )
        audio.write_to_file("script.mp3")
        #return f'audio file is ready {response}'
        audio_file = 'script.mp3'
        st.audio(audio_file, format='audio/mp3', start_time=0)
        return f'return only the generated script: {response}'
    





# Define the input schema
class A(BaseModel):
    ai_input: str = Field(..., description="Content to be converted an audio file.")

@tool(args_schema=A)
def audio(ai_input):
    """Creates an audio file for anything the user suggests.
    input (str): The content to be converted an audio file.
    """
    with st.spinner("Creaating the audio..."):

        response = client.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=ai_input,
            )
        response.write_to_file("script.mp3")
    #st.write(ai_input)
    #return f'audio file is ready {response}'
    audio_file = 'script.mp3'
    st.audio(audio_file, format='audio/mp3', start_time=0)
    return f'the audio file is complete. Do not return a link to the audio file' 



memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
#prompt with agent_scratpad
ai_prompt = ChatPromptTemplate.from_messages([
    ("system",
     '''
    INSIGHT is an AI wellness coach providing deep and meaningful guidance on personal growth, wellness, and self-reflection. Drawing inspiration from a wide range of philosophical and psychological sources, INSIGHT offers insightful, contemplative, and practical advice. For each query, it responds in three sections: Wisdom, The Practice, and Hidden Geometries.

    Wisdom: INSIGHT offers philosophical responses to queries, presenting thought-provoking and motivational insights in a contemplative style.

    The Practice: Following the wisdom, INSIGHT suggests practical tools and resources, including a breathing technique and a movement suggestion, to help users apply the philosophical insights in their daily lives.

    Hidden Geometries: This section delves into the principles and benefits of the suggested techniques, enhancing understanding and application. INSIGHT will conclude this section with a thought-provoking question.

    After Hidden Geometries and before asking if the user desires more in-depth details, INSIGHT will say, "Remember... ALL IS WITHIN" reinforcing the central theme of internal reflection and growth.

    INSIGHT aims to engage users interactively, promoting self-awareness and personal development.
    '''),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])






def ai_agent(human_input):
    #tools = [create_image,audio, med_script, sleep, retriever_tool] #genImage]
    tools = [audio, med_script] #genImage]
    #Step 4: create RunnablePassthrough for format_to_openai_functions([(result1, observation)])
    functions = [convert_to_openai_function(f) for f in tools]
    model = ChatOpenAI(temperature=0, streaming=True).bind(functions=functions)

    agent_chain = RunnablePassthrough.assign(
        agent_scratchpad= lambda x: format_to_openai_functions(x["intermediate_steps"])
    ) | ai_prompt | model | OpenAIFunctionsAgentOutputParser()
    agent_executor = AgentExecutor(agent=agent_chain, tools=tools, verbose=True, memory=memory)
    response= agent_executor.invoke({"input": human_input})['output']
 
    return response #agent_executor.invoke({"input": human_input})['output']

