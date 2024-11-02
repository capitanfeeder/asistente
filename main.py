import subprocess
import sys
import os
import time
import streamlit as st
import requests
import google.generativeai as genai
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from streamlit_chat import message

# Configuración del backend
app = FastAPI()

# Obtener la API key de la variable de entorno
gemini_api_key = st.secrets.get("gemini_api_key")

genai.configure(api_key=gemini_api_key)

model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Endpoint para interactuar con el chatbot
@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        question = data.get("prompt")
        if not question:
            return JSONResponse(content={"error": "No se proporcionó una pregunta"}, status_code=400)
        
        response = model.generate_content(question)
        return JSONResponse(content={"response": response.text}, status_code=200)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return JSONResponse(content={"error": "Error interno del servidor"}, status_code=500)

# Configuración del frontend
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

# Función principal para iniciar la aplicación
def main():
    print("Iniciando la aplicación...")
    
    # Iniciar el servidor FastAPI en un proceso separado
    backend_process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8000', '--reload'])
    
    # Esperar un poco para asegurarse de que el backend esté listo
    time.sleep(5)
    
    # Iniciar la aplicación Streamlit
    frontend_process = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', 'main.py', '--server.port', '8501'])
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDeteniendo la aplicación...")
    
    backend_process.terminate()
    frontend_process.terminate()

if __name__ == "__main__":
    main()