#
#   Python 3.11.10
#

import os
import re
import pandas as pd
from bs4 import BeautifulSoup


class ScrapDefault:
    def _dir_file(self, path: str | os.PathLike) -> list[str] | str:
        """
        Retorna uma lista de caminhos absoluto dos arquivos.
        
        **Args:**
        - **path** : *str | os.PathLike*\n
            Caminho do diretorio com os arquivos
        
        **Exception:**
        - **ValueError** : Path "{path}" not found\n
            Diretorio passado como argumento esta incorreto
        
        **Returns:**
        - *list[str]*\n
            Lista com os caminhos completos dos arquivos
        - *str*\n
            Excessao de ValueError 
        """
        try:
            if not os.path.exists(path):
                raise ValueError(f'Path "{path}" not found')

            path = os.path.abspath(path)
            paths = list(map(lambda f: os.path.join(path, f), os.listdir(path)))
            paths.sort()
            return paths
        except Exception as e:
            return str(e)

    def scrap_data_html_yghpro(
        self,
        files: list[str],
        path_out: str | os.PathLike
    ) -> None:
        """
        Cria um arquivo `.txt` com dados de arquivos HTMLs
        
        **Args:**
        - **files** : *list[str]*\n
        Lista com caminho dos arquivos que serao raspados
        - **path_out** : *str* | *os.PathLike*\n
        Diretorio de saida do arquivo com os dados
        
        **Returns:**
        - *None*
        """
        path_out = os.path.abspath(path_out)
        path_out = os.path.join(path_out, 'file_out.txt')
        for file in files:
            with open(file, 'r', encoding='utf-8') as arquivo:
                conteudo = arquivo.read()

            soup = BeautifulSoup(conteudo, 'html.parser')
            html_cartas = list(soup.find_all('div', class_="item-area"))
            html_cartas = list(map(lambda x: re.sub('\s+', ' ', str(x)), html_cartas))

            with open(path_out, 'a', encoding='utf-8') as file_out:
                file_out.writelines([string + '\n' for string in html_cartas])    

    def show_html(self, iter: str | list) -> None:
        """
        Formata a apresentacao de um arquivo HTML.
        
        **Args:**
        - **iter** : *str* | *list*\n
        String explicita do HTML ou uma Lista de arquivos HTMLs.
        
        **Returns:**
        - *None*
        """
        if isinstance(iter, str):
            soup = BeautifulSoup(iter, 'html.parser')
            print(soup.prettify())
        else:
            for string in iter:
                soup = BeautifulSoup(string, 'html.parser')
                print(soup.prettify())

    def get_data(self, iter: list | tuple) -> list[tuple]:
        """
        Retorna uma matriz com dados do arquivo HTML no diretorio scrap/Home
        
        **Args:**
        - **iter** : *list | tuple*\n
        Lista ou Tupla com caminhos completo dos arquivos
        
        **Returns:**
        - *list[tuple]*\n
        Matriz com dados de cada arquivo em linhas da matriz
        """
        def __coleta_dados__(string: str) -> tuple:
            soup = BeautifulSoup(string, 'html.parser')
            link_img = soup.find('span', class_='item-img')
            link = link_img.find('img').attrs.get('src')
            nome_card = soup.find('h1').text.strip()
            tipo_card = soup.find('span', class_="item-misc small")
            item = re.sub(r'\s+', ' ', tipo_card.text.replace('\n', '|'))
            efeito = re.sub('\s+', ' ', str(soup.find('p').text.strip()))
            return (link, nome_card, item, efeito)

        return list(map(__coleta_dados__, iter))

if __name__ == '__main__':
    scrap = ScrapDefault()
    src = os.path.dirname(__file__)
    tx = os.path.join(src.replace('src', 'scrap'), 'tx')
  
    _file_ = os.path.join(tx, 'file_out_copy.txt')
    with open(_file_, 'r', encoding='utf-8') as file:
        cards = file.readlines()

    dados = scrap.get_data(cards)
    _name_ = os.path.join(src, 'estatistica', 'data_card.xlsx')
    pd.DataFrame(dados).to_excel(_name_, index=False)
