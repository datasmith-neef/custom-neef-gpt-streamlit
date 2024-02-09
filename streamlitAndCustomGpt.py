import streamlit as st
import os
import json
import uuid
from customgpt_client import CustomGPT


from dotenv import load_dotenv
import os

load_dotenv()  # Lädt die Variablen aus der .env-Datei

customgpt_api_key = os.getenv('CUSTOMGPT_API_KEY')
activation_code_1 = os.getenv('ACTIVATION_CODE_FAC')
activation_code_2 = os.getenv('ACTIVATION_CODE_SIN')
activation_code_3 = os.getenv('ACTIVATION_CODE_DSO')

# App title
st.set_page_config(page_title="Datasmith - GPT Chatbot",page_icon='💬')

st.markdown('<div class="typewriter-text">👾 Factor.Design-GPT</div>', unsafe_allow_html=True)
st.caption("🚀 A chatbot powered by OpenAI LLM and Datasmith Office")

# Function to retrieve citations using CustomGPT API
def get_citations(api_token, project_id, citation_id):
    CustomGPT.api_key = api_token

    try:
        response_citations = CustomGPT.Citation.get(project_id=project_id, citation_id=citation_id)
        if response_citations.status_code == 200:
            try:
                citation = response_citations.parsed.data
                if citation.url is not None:
                    source = {'title': citation.title, 'url': citation.url}
                else:
                    source = {'title': 'source', 'url': ""}
            except:
                if citation.page_url is not None:
                    source = {'title': citation.title, 'url': citation.page_url}
                else:
                    source = {'title': 'source', 'url': ""}
            
            return source
        else:
            return []
    except Exception as e:
        print(f"error::{e}")

# Function to query the chatbot using CustomGPT API
def query_chatbot(api_token, project_id, session_id, message, stream=True, lang='de'):
    CustomGPT.api_key = api_token
    try:
        stream_response = CustomGPT.Conversation.send(project_id=project_id, session_id=session_id, prompt=message, stream=stream, lang=lang)
        return stream_response
    except Exception as e:
        return [f"Error:: {e}"]

# Function to get the list of projects using CustomGPT API
def get_projectList(api_token):
    CustomGPT.api_key = api_token
    try:
        projects = CustomGPT.Project.list()
        if projects.status_code == 200:
            return projects.parsed.data.data
        else:
            return []
    except Exception as e:
        print(f"error:get_projectList:: {e}")

# Function to clear chat history
def clear_chat_history():
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = [{"role": "assistant", "content": "Moin , ich bin Factor-GPT , na?"}]



# Check if session_id is not in session_state, initialize it
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# CustomGPT Credentials
with st.sidebar:
    ts = 'Datasmith-GPT (Settings)'
    sidebar_header = st.header(ts)
    st.image("compressed_office_image.jpg")
   
    st.markdown("Hier können X weitere Projekte hinzugefügt werden - Demoversion - Datasmith Office")
    #customgpt_api_key = st.text_input('Enter CustomGPT API Key:', type='password')
    customgpt_api_key = customgpt_api_key
    activation_code = st.text_input('Enter youre activation_code : ',type = 'password')

    selected_index = ''
    if activation_code == activation_code_1:
        selected_index = 1
        st.success("Activated")
        sidebar_header.header("Factor.design-GPT (Activated)")
        
    elif activation_code == activation_code_2:
        selected_index = 0
        st.success("Activated")
        sidebar_header.header("Sintronics-GPT (Activated)")

    elif activation_code == activation_code_3:
        selected_index = 77
        st.success("Activated")
        sidebar_header.header("Datasmith-GPT (Admin-Mode)")

    else : st.error('No projects found. Please check your actication key.', icon='❌')
    
    


    if customgpt_api_key and selected_index:
        st.subheader('Select Project')
        listProject = get_projectList(customgpt_api_key)
        
        # Check if projects are available
        if listProject is not None:
            projectNames = [projt.project_name for projt in listProject]
            
            selected_index = selected_index # Auswahl je nach Activation Codes
            if selected_index != 77:
                selected_model = st.sidebar.selectbox('Select Model', options=[projectNames[selected_index]], index=0, key='selected_model')
            
            else: selected_model = st.sidebar.selectbox('Select Model', projectNames, key='selected_model') # admin für alle projekte
            index = projectNames.index(selected_model)
            selected_project = listProject[index]
            
        else:
            st.error('No projects found. Please check your API key.', icon='❌')
        
        # Button to reset chat
        st.sidebar.button('Reset Chat', on_click=clear_chat_history)

# Check if messages is not in session_state.keys(), initialize it
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Moin , ich bin Factor-GPT , na?"}]

# Display or clear chat messages
for index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        # Display the message content
        st.write(f"{message['content']}")

# User-provided prompt
if prompt := st.chat_input(disabled=not customgpt_api_key):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        # Display the user's message
        st.write(prompt)

# Generate a new response if the last message is not from the assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("RatterRatter..."):
            client = query_chatbot(customgpt_api_key, selected_project['id'], st.session_state.session_id, prompt)
            placeholder = st.empty()
            full_response = ""
            
            for event in client.events():
                print(event.data)
                resp_data = eval(event.data.replace('null', 'None'))
                
                # Check different status types
                if resp_data is not None:
                    if resp_data.get('status') == 'error':
                        full_response += resp_data.get('message', '')
                        placeholder.markdown(full_response + "▌")

                    if resp_data.get('status') == 'progress':
                        full_response += resp_data.get('message', '')
                        placeholder.markdown(full_response + "▌")

                    if resp_data.get('status') == 'finish' and resp_data.get('citations') is not None:
                        citation_ids = resp_data.get('citations', [])

                        citation_links = []
                        count = 1
                        
                        # Process citation links
                        for citation_id in citation_ids:
                            citation_obj = get_citations(customgpt_api_key, selected_project['id'], citation_id)
                            url = citation_obj.get('url', '')
                            title = citation_obj.get('title', '')
                            
                            if len(url) > 0:
                                formatted_url = f"{count}. [{title or url}]({url})"
                                count += 1
                                citation_links.append(formatted_url)

                        # if citation_links:
                        #     cita = "\n\nSources:\n"
                        #     for link in citation_links:
                        #         cita += f"{link}\n"
                        #     full_response += cita
                        #     placeholder.markdown(full_response + "▌")
                           
            placeholder.markdown(full_response)
            
    if full_response == "":
        full_response = "Oh no! Unbekannter Fehler.Kontaktiere den Administrator."
        placeholder.markdown(full_response)
    
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
