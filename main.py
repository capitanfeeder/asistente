import subprocess
import sys
import os
import time
import streamlit as st
from streamlit_chat import message
import requests
import google.generativeai as genai
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Clase para gestionar la aplicación
class AppManager:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None

    # Método de gestión de proceso backend
    def start_backend(self):
        """
        Inicia el servidor backend utilizando FastAPI.

        Este método cambia al directorio del backend, inicia el servidor FastAPI en el puerto 8000,
        y luego vuelve al directorio raíz.

        Returns:
            subprocess.Popen: El proceso del servidor backend.
        """
        os.chdir('back')
        self.backend_process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'assistant:app', '--host', '127.0.0.1', '--port', '8000', '--reload'])
        os.chdir('..')
        return self.backend_process

    # Método de gestión de proceso frontend
    def start_frontend(self):
        """
        Inicia la aplicación frontend utilizando Streamlit.

        Este método cambia al directorio del frontend, inicia la aplicación Streamlit en el puerto 8501,
        y luego vuelve al directorio raíz.

        Returns:
            subprocess.Popen: El proceso de la aplicación frontend.
        """
        os.chdir('front')
        self.frontend_process = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', 'interface.py', '--server.port', '8501'])
        os.chdir('..')
        return self.frontend_process

    # Método principal de gestión de la aplicación
    def run(self):
        """
        Función principal que inicia y gestiona la aplicación completa.

        Esta función inicia tanto el backend como el frontend, espera a que el backend esté listo,
        y luego mantiene la aplicación en ejecución hasta que se interrumpa manualmente (Ctrl+C).
        Finalmente, termina los procesos del backend y frontend.
        """
        print("Iniciando la aplicación...")
        
        self.start_backend()
        time.sleep(5)  # Tiempo para asegurarse de que el backend esté listo antes de iniciar el frontend
        
        self.start_frontend()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nDeteniendo la aplicación...")
        
        self.backend_process.terminate()
        self.frontend_process.terminate()

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

if __name__ == "__main__":
    app_manager = AppManager()
    app_manager.run()