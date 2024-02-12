import streamlit as st
import os
import json
import uuid
from customgpt_client import CustomGPT


from dotenv import load_dotenv
import os

load_dotenv()  # Lädt die Variablen aus der .env-Datei

customgpt_api_key = os.getenv('CUSTOMGPT_API_KEY')
activation_code_1 = st.secrets['ACTIVATION_CODE_FAC']
activation_code_2 = st.secrets['ACTIVATION_CODE_SIN']
activation_code_3 = st.secrets['ACTIVATION_CODE_DSO']
firma = "Robot"
funktion = "my_Website"
#st.write("new_secret",st.secrets["voucher100"]) schreiben und nutzen von secrets innergalb der APP

# App title
st.set_page_config(page_title="Datasmith - GPT Chatbot",page_icon='assets/datasmith.ico')




## entwickler optionen sandwichmenue ausblenden
st.markdown("""
<style>
    .stActionButton
            {
                visibility:hidden;
            }    

    

</style>

""",unsafe_allow_html=True)


default_title = 'assets/datasmith.ico'
customer_1 = 'assets/factor.ico'
customer_2 = 'assets/sintronics.ico'


st.markdown("""
    <style>
        @keyframes typewriter {
            from { 
                width: 0; 
            }
            to { 
                width: 100%; 
            }
        }

        @keyframes blink {
            from, to {
                border-color: transparent;
            }
            50% {
                border-color: black;
            }
   
     
        }

        .typewriter-text {
            display: inline-block;
            overflow: hidden;
            border-right: 0.05em solid black;  /* Cursor-Effekt */
            white-space: nowrap;
            font-size: 0.9rem; 
            
            animation: 
        typewriter 5s steps(50, end), 
        blink .75s step-end 13, 
        fadeOutCursor 0.25s forwards 10s;
        }
    </style>
""", unsafe_allow_html=True)

#st.markdown('<div class="typewriter-text">💬 Datasmith-GPT</div>', unsafe_allow_html=True)



#logo_chat = st.image(default_title,width=33,caption = "GPT")
#st.caption("🚀 A chatbot powered by OpenAI LLM and Datasmith Office")


# Erstellen Sie zwei Spalten im Layout
col1, col2 = st.columns([1, 20])  # Die Zahlen bestimmen das Verhältnis der Spaltenbreiten

# Erste Spalte für das Bild
with col1:
    logo_chat = st.image(default_title, width=32)  # Stellen Sie die Breite des Bildes ein

# Zweite Spalte für den Text
with col2:
    st.write(f"{funktion} - GPT")
    st.caption('<div class="typewriter-text">🚀 A chatbot powered by OpenAI LLM and Datasmith Office</div>', unsafe_allow_html=True)

st.markdown("---")

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
    st.session_state.messages = [{"role": "assistant", "content": f"Moin , ich bin {firma}-GPT , na?"}]



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
    activation_code = st.text_input('Enter youre activation_code : ',type = 'password',on_change=clear_chat_history)
    
   
    selected_index = ''
    if activation_code == activation_code_1:
        selected_index = 1
        st.success("Activated")
        sidebar_header.header("Factor-GPT (Activated)")
        logo_chat.image(customer_1)
        firma = "Factor"
        clear_chat_history()
        

    elif activation_code == activation_code_2:
        selected_index = "0"
        st.success("Activated")
        sidebar_header.header("Sintronics-GPT (Activated)")
        logo_chat.image(customer_2)
        firma = "Sintronics"
        clear_chat_history()
        
        


    elif activation_code == activation_code_3:
        selected_index = 77
        st.success("Activated")
        sidebar_header.header("Datasmith-GPT (Admin-Mode)")
        logo_chat.image(default_title)
        firma = "Robot"
        clear_chat_history()

    else : st.error('No projects found. Please check your actication key.', icon='❌')
    
    


    if customgpt_api_key and selected_index:
        st.subheader('Select Project')
        listProject = get_projectList(customgpt_api_key)
        
        # Check if projects are available
        if listProject is not None:
            projectNames = [projt.project_name for projt in listProject]
            
            selected_index = selected_index # Auswahl je nach Activation Codes
            if selected_index == "0":
                selected_model = st.sidebar.selectbox('Select Model', options=[projectNames[int(selected_index)]], key='selected_model')
                index = projectNames.index(selected_model)
                selected_project = listProject[index]
            elif selected_index == 1:
                selected_model = st.sidebar.selectbox('Select Model', options=[projectNames[selected_index]],key='selected_model')
                index = projectNames.index(selected_model)
                selected_project = listProject[index]
            else: 
                selected_model = st.sidebar.selectbox('Select Model', projectNames, key='selected_model') # admin für alle projekte
                index = projectNames.index(selected_model)
                selected_project = listProject[index]
            
            
        else:
            st.error('No projects found. Please check your API key.', icon='❌')
        
        # Button to reset chat
        st.sidebar.button('Reset Chat', on_click=clear_chat_history)

if activation_code:
# Check if messages is not in session_state.keys(), initialize it
    if "messages" not in st.session_state.keys():
        
        st.session_state.messages = [{"role": "assistant", "content": f"Moin , ich bin {firma}-GPT , na?"}]

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
