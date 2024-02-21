import requests
from bs4 import BeautifulSoup
import os

# Definindo os diretórios base para salvar os arquivos HTML e PDF
BASE_DIR = 'bundesgerichtshof_local'
HTML_DIR = os.path.join(BASE_DIR, 'data/html')
PDF_DIR = os.path.join(BASE_DIR, 'data/pdfs')

# Certifique-se de que os diretórios existam
os.makedirs(HTML_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

# URL base e caminho para os documentos
url_base = "https://juris.bundesgerichtshof.de"
document_path = "/cgi-bin/rechtsprechung/document.py?Gericht=bgh&Art=en"

# Identificador único para o documento
unique_id = 0

file_name = "juris_bundesgerichtshof_" + str(unique_id)
htmal_file_name = file_name + ".html"
pdf_file_name = file_name + ".pdf"

webpage_url = f"{url_base}{document_path}&nr={unique_id}"
pdf_url = f"{url_base}{document_path}&nr={unique_id}&Frame=4&.pdf"





'''
def download_pdf_local(url, file_name):
    """
    Faz o download de um PDF da URL fornecida e salva localmente.
    """
    response = requests.get(url)
    if response.status_code == 200:
        pdf_path = os.path.join(PDF_DIR, file_name)
        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(response.content)
        print(f"PDF salvo localmente em {pdf_path}")
    else:
        print(f"Erro ao baixar o PDF de {url}")

def main():
    # Substitua por sua lógica para determinar estes valores, se necessário
    unique_id = "123456"  # Exemplo de um identificador único
    base_url = "https://juris.bundesgerichtshof.de"
    document_path = "/cgi-bin/rechtsprechung/document.py?Gericht=bgh&Art=en"
    
    # Construindo a URL para a página e o PDF
    webpage_url = f"{base_url}{document_path}&nr={unique_id}"
    pdf_url = f"{base_url}{document_path}&nr={unique_id}&Frame=4&.pdf"

    # Nome base para os arquivos
    base_file_name = f"juris_bundesgerichtshof_{unique_id}"

    # Download e salvamento do PDF localmente
    download_pdf_local(pdf_url, f"{base_file_name}.pdf")

if __name__ == "__main__":
    main()
'''