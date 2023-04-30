from bs4 import BeautifulSoup
import requests
import pandas as pd
import tabula
import datetime
import numpy as np
from utils import dt_now

class Scraping:
    def __init__(self):
        self.endpoint = "http://www.propaae.uefs.br/modules/conteudo/conteudo.php?conteudo=15"

    def retrieve_html(self) -> BeautifulSoup:
        r = requests.get(self.endpoint)
        return BeautifulSoup(r.text, 'html.parser')

    def find_pdf_link(self, soup):
        # faça aqui a logica para encontrar o link do pdf na página
        img_tag = soup.find('img', {'alt': 'Cardápio'})
        link_tag = img_tag.parent
        return link_tag['href']

    def download_pdf(self, pdf_link):
        response = requests.get(pdf_link)
        with open('cardapio.pdf', 'wb') as f:
            f.write(response.content)

    def extract_pdf(self) -> pd.DataFrame:
        df = tabula.read_pdf('cardapio.pdf', pages='all', multiple_tables=True)
        df = pd.concat(df)
        df = df.reset_index(drop=True)
        df = df.replace(np.nan, '', regex=True)
        return df

teste = Scraping()
print(1)
soup = teste.retrieve_html()
print(2)
pdf_link = teste.find_pdf_link(soup)
print(3)
teste.download_pdf(pdf_link)
print(4)
df = teste.extract_pdf()
print(df)
