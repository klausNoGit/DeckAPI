#
#   Python 3.11.10
#

import os
import re
from bs4 import BeautifulSoup

src = str(os.path.dirname(__file__))
html = str(src.replace('src', 'html'))

arq1 = os.path.join(html, os.listdir(html)[0])

with open(arq1, 'r') as file:
    soup = BeautifulSoup(file.read(), 'html.parser')
    dados = soup.find('div', id='card_list')
    print(re.sub(r'\s+', ' ', dados.text).strip())

