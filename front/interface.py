import streamlit as st
from streamlit_chat import message
import requests

# Configuración de la página
st.set_page_config(page_title="Chatbot", page_icon="🤖")

# Endpoint del chatbot
API_URL = "http://localhost:8000/chat"

# Función para enviar la pregunta al chatbot y obtener la respuesta
def get_response(prompt):
    response = requests.post(API_URL, json={"prompt": prompt})
    if response.status_code == 200:
        json_response = response.json()
        return json_response.get("response", "No se pudo obtener una respuesta.")
    else:
        return "Error al comunicarse con el servidor."

# Inicializar el estado de la conversación
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

# Título del chatbot
st.title("Chatbot Interactivo")

# Mostrar la conversación
for i in range(len(st.session_state['generated'])):
    message(st.session_state['past'][i], is_user=True, key=f"past_{i}")
    message(st.session_state['generated'][i], key=f"generated_{i}")

# Área de entrada de texto
if prompt := st.chat_input("¿En qué puedo ayudarte?"):
    st.session_state.past.append(prompt)
    message(prompt, is_user=True, key=f"past_{len(st.session_state.past) - 1}")

    with st.spinner("Generando respuesta..."):
        response = get_response(prompt)
        st.session_state.generated.append(response)
        message(response, key=f"generated_{len(st.session_state.generated) - 1}")
