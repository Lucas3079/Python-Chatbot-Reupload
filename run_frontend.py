#!/usr/bin/env python3
"""
Script para iniciar o servidor frontend na pasta correta
"""
import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def main():
    # Navega para a pasta frontend
    frontend_dir = Path(__file__).parent / "frontend"
    
    if not frontend_dir.exists():
        print("Pasta frontend nao encontrada!")
        return
    
    print("Iniciando servidor frontend...")
    print(f"Diretorio: {frontend_dir}")
    
    # Muda para o diretório frontend
    os.chdir(frontend_dir)
    
    # Inicia o servidor HTTP
    try:
        print("Servidor rodando em: http://localhost:3000")
        print("Abrindo navegador...")
        
        # Abre o navegador
        webbrowser.open("http://localhost:3000")
        
        # Inicia o servidor
        subprocess.run([sys.executable, "-m", "http.server", "3000"])
        
    except KeyboardInterrupt:
        print("\nServidor parado pelo usuario")
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    main()