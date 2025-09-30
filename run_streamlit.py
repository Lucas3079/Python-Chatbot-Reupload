"""Script para executar a interface Streamlit."""
import subprocess
import sys
import os

def main():
    """Executa a interface Streamlit."""
    try:
        # Verifica se o arquivo existe
        streamlit_app_path = os.path.join("app", "streamlit_app.py")
        if not os.path.exists(streamlit_app_path):
            print(f"Arquivo nao encontrado: {streamlit_app_path}")
            sys.exit(1)
        
        print("Iniciando interface Streamlit...")
        print("Acesso: http://localhost:8501")
        print("Certifique-se de que a API esta rodando em http://localhost:8000")
        
        # Executa Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            streamlit_app_path,
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
        
    except KeyboardInterrupt:
        print("\nInterface Streamlit encerrada pelo usuario")
    except Exception as e:
        print(f"Erro ao executar Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
