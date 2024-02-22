import requests
from bs4 import BeautifulSoup
import pandas as pd

#/html/body/table[2]/tbody/tr[1]/td[4]/table/tbody/tr[2]/td/form/table/thead

# webpage_url da página
url_base = "https://juris.bundesgerichtshof.de"
document_path = "/cgi-bin/rechtsprechung/list.py?Gericht=bgh&Art=en&Datum=Aktuell&Sort=12288"
webpage_url = f"{url_base}{document_path}"

response = requests.get(webpage_url)

decisions = []

if response.status_code == 200:
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
  
    # Find all rows in the table
    rows = soup.find("tbody").find_all("tr")

    # Iterate over the rows and extract the text (exclude the thead and tfoot rows)  

    for row in rows:
        # Extract the text from each cell
        cells = row.find_all("td")

        if len(cells) == 5: # garantir 5 colunas (senado, data da decisão, data de publicação, número do processo, adtional info)
            decision = {
                "Senat": cells[0].text.strip(),
                "Entscheidungsdatum": cells[1].text.strip(),
                "Einspieldatum": cells[2].text.strip(),
                "Aktenzeichen": cells[3].text.strip(),
                "Zusatzinformationen": cells[4].text.strip()
            }

            decisions.append(decision)

df = pd.DataFrame(decisions)

# print(df)

# Save the dataframe to a csv file
local_path= "bundesgerichtshof_local/data/decisions_table.csv"
working_path = "//mnt/c/Users/daniz/OneDrive/Documentos/iur.crowd/decisions_table.csv"
df.to_csv(local_path, index=False, encoding='utf-8')  # Save without index and with utf-8 encoding
df.to_csv(working_path, index=False, encoding='utf-8')  # Save without index and with utf-8 encoding


