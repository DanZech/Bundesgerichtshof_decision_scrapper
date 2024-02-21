import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import re
from datetime import datetime
import json

# Diretórios base para salvar HTML e PDFs
HTML_DIR = 'bundesgerichtshof_local/data/html'
PDF_DIR = 'bundesgerichtshof_local/data/pdfs'
DB_PATH = 'bundesgerichtshof_local/database/data.db'

# Verifica e cria diretórios, se necessário
os.makedirs(HTML_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

# Função para salvar HTML localmente
def save_html_local(file_name, html_content):
    file_path = os.path.join(HTML_DIR, file_name)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html_content)
    print(f"HTML content saved locally in '{file_path}'")

# Função para salvar PDF localmente
def save_pdf_local(file_name, pdf_content):
    file_path = os.path.join(PDF_DIR, file_name)
    with open(file_path, 'wb') as file:
        file.write(pdf_content)
    print(f"Downloaded PDF saved locally in '{file_path}'")

# Função para criar o banco de dados SQLite e tabela de documentos
def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY,
        unique_id TEXT,
        aktenzeichen TEXT,
        dataset_id INTEGER,
        document_type TEXT,
        database_title TEXT,
        senat TEXT,
        veroeffentlichung TEXT,
        KZR_in_aktenzeichen BOOLEAN,
        aktenzeichen_already_existed BOOLEAN
    )
    ''')
    conn.commit()
    conn.close()
    print("Database and table created successfully.")

# Função para inserir dados de documentos no banco de dados
def insert_document(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO documents (unique_id, aktenzeichen, dataset_id, document_type, database_title, senat, veroeffentlichung, KZR_in_aktenzeichen, aktenzeichen_already_existed)
    VALUES (:unique_id, :aktenzeichen, :dataset_id, :document_type, :database_title, :senat, :veroeffentlichung, :KZR_in_aktenzeichen, :aktenzeichen_already_existed)
    ''', data)
    conn.commit()
    conn.close()
    print("Document data inserted successfully.")

# Função principal para iniciar o processo de scraping
def main(url):
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        # Aqui você faria o scraping de fato, extraindo as informações necessárias
        # Por exemplo, extrair o título para usar como nome do arquivo HTML/PDF
        title = soup.find('title').text if soup.find('title') else 'Untitled'

        # Salvando o HTML localmente
        save_html_local(f"{title}.html", html_content)

        # Suponha que encontramos um URL de PDF para download no conteúdo da página
        pdf_url = "https://juris.bundesgerichtshof.de/cgi-bin/rechtsprechung/document.py?Gericht=bgh&Art=en&Datum=Aktuell&nr=136468&pos=0&anz=1261"
        pdf_response = requests.get(pdf_url)
        if pdf_response.status_code == 200:
            save_pdf_local(f"{title}.pdf", pdf_response.content)

        # Inserindo dados no banco de dados
        document_data = {
            'unique_id': '123',  # Exemplo, ajuste conforme necessário
            'aktenzeichen': 'XYZ',  # Exemplo, ajuste conforme necessário
            'dataset_id': 1,  # Exemplo, ajuste conforme necessário
            'document_type': 'Tipo',  # Exemplo, ajuste conforme necessário
            'database_title': title,
            'senat': 'Senado',  # Exemplo, ajuste conforme necessário
            'veroeffentlichung': datetime.now().strftime('%Y-%m-%d'),  # A data de hoje como exemplo
            'KZR_in_aktenzeichen': False,
            'aktenzeichen_already_existed': False
        }
        insert_document(document_data)
    else:
        print(f"Failed to retrieve {url}")

if __name__ == "__main__":
    create_database()  # Garante que o banco de dados e a tabela estejam criados
    main('https://juris.bundesgerichtshof.de/cgi-bin/rechtsprechung/document.py?Gericht=bgh&Art=en&Datum=Aktuell&nr=136468&pos=0&anz=1261')  # Substitua pela URL real que você deseja fazer scraping
