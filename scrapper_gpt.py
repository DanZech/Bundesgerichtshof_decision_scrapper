import requests
from bs4 import BeautifulSoup

# webpage_url da página
url_base = "https://juris.bundesgerichtshof.de"
document_path = "/cgi-bin/rechtsprechung/document.py?Gericht=bgh&Art=pm&pm_nummer="
year = "/24"

for i in range(1, 100):
    unique_id = f"{i:04d}" 

    # Restante do código aqui
    webpage_url = f"{url_base}{document_path}{unique_id}{year}"

    # Fazer requisição à página
    response = requests.get(webpage_url)

    # Verificar se a requisição foi bem-sucedida
    if response.status_code == 200:

        # Extrair o conteúdo HTML da página
        html_content = response.text

        # Criar um objeto BeautifulSoup a partir do HTML
        soup = BeautifulSoup(html_content, "html.parser")

        # Extrair o título da decisão
        court = soup.find("h1").text.strip()
        print(court)

        objet = soup.find("h2").text.strip()
        print(objet)

        brief = []
        for item in soup.find_all("div", align="center"):
            brief.append(item.text.strip())
            brief_string = ' '.join(brief)
        print("Case brief:", brief_string)


        # Extrair os detalhes da decisão
        detalhes = []
        for item in soup.find_all("p", align="justify"):
            detalhes.append(item.text.strip())

        # Exibir os dados extraídos
        print("Detalhes:")
        for detalhe in detalhes:
            print("-", detalhe)

    else:
        print("Erro ao acessar a página:", response.status_code)
