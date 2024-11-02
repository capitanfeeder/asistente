import os
import json
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("assistant:app", host="127.0.0.1", port=8000, reload=True)
