import requests
from bs4 import BeautifulSoup
import os
import webbrowser

# Definindo os diretórios base para salvar os arquivos HTML e PDF
BASE_DIR = 'bundesgerichtshof_local'
HTML_DIR = os.path.join(BASE_DIR, 'data/html')
PDF_DIR = os.path.join(BASE_DIR, 'data/pdfs')

# Certifique-se de que os diretórios existam
os.makedirs(HTML_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

#https://juris.bundesgerichtshof.de
#/cgi-bin/rechtsprechung/document.py?Gericht=bgh&Art=en&Datum=Aktuell&Sort=12288&nr=136469

# URL base e caminho para os documentos
url_base = "https://juris.bundesgerichtshof.de"
document_path = "/cgi-bin/rechtsprechung/document.py?Gericht=bgh&Art=en"

# Solicitar a unique_id ao usuário
unique_id = input("Digite a unique_id: ")

file_name = "juris_bundesgerichtshof_" + str(unique_id)
html_file_name = file_name + ".html"
pdf_file_name = file_name + ".pdf"

webpage_url = f"{url_base}{document_path}&nr={unique_id}"
pdf_url = f"{url_base}{document_path}&nr={unique_id}&Frame=4&.pdf"

# Abrir a página no navegador
webbrowser.open(webpage_url)
