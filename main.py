import subprocess
import sys
import os
import time


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


if __name__ == "__main__":
    app_manager = AppManager()
    app_manager.run()
