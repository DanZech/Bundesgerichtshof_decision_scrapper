import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse, parse_qs

#/html/body/table[2]/tbody/tr[1]/td[4]/table/tbody/tr[2]/td/form/table/thead

# webpage_url da página
url_base = "https://juris.bundesgerichtshof.de/"
document_path = "cgi-bin/rechtsprechung/list.py?Gericht=bgh&Art=en&Datum=Aktuell&Seite="
pages = range(0,43) # 


def unique_nr_extract(href):
    query_string = urlparse(href).query # Retorna a query string da URL
    parametros = parse_qs(query_string)     # Retorna um dicionário com os parâmetros da query string
    numero_nr = parametros.get('nr', [None])[0]  # Retorna None se 'nr' não existir
    return numero_nr

decisions = []

for page in pages:
    webpage_url = f"{url_base}{document_path}{page}"
    response = requests.get(webpage_url)
    
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")

        columms = soup.find("tbody").find_all("tr")

        for columm in columms:
            cells = columm.find_all("td")
            if len(cells) == 5:
                
                all_links_aktenzeichen = cells[3].find_all("a")
                print(len(all_links_aktenzeichen))
                link_to_parse = all_links_aktenzeichen[1] if all_links_aktenzeichen else None
                link = (link_to_parse['href']) if link_to_parse else None
                unique_nr = unique_nr_extract(link) if link else None

                decision = {
                    "Senat": cells[0].text.strip(),
                    "Entscheidungsdatum": cells[1].text.strip(),
                    "Einspieldatum": cells[2].text.strip(),
                    "Aktenzeichen": cells[3].text.strip(),
                    "Link_Aktenzeichen": f"{url_base}{link}",
                    "Zusatzinformationen": cells[4].text.strip(),
                    "Unique_nr": unique_nr
                   
                }

                decisions.append(decision)
                print(unique_nr)

df = pd.DataFrame(decisions)

# print(df)


# Save the dataframe to a csv file
local_path= "bundesgerichtshof_local/data/decisions_table.csv"
working_path = "//mnt/c/Users/daniz/OneDrive/Documentos/iur.crowd/decisions_table.csv"
df.to_csv(local_path, index=False, encoding='utf-8', sep=';')  # Save without index and with utf-8 encoding using semicolon (;) as separator
df.to_csv(working_path, index=False, encoding='utf-8', sep=';')  # Save without index and with utf-8 encoding using semicolon (;) as separator

print(f"File saved to {local_path}")