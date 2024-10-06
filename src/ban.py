#
#   Python 3.11.10
#

import os
import asyncio
import requests
from typing import Union

import pandas as pd         # typing: ignore
from pandas import DataFrame


class BanSheetWeb:
    """
    Estrutura de dados criada para lidar com requisicoes ao **google.sheet**,\n
    processamento de dados em rede e arquivos locais, ambos referente\n
    a banlist do Mochila Champions.

    ### ****Args:****
    - **sheet** : *str*\n
    Nome da folha na planilha que deve ser feita a requisicao.

    ### **Returns:**
    - *None*
    """
    def __init__(self, sheet: str = 'Home') -> None:
        self.__SHEET: str = sheet
        self.__TOKEN: str  = 'AKfycby08zhGHOhwy3iQEEnnFbmXmA9vr5pW4JS83Usgci1MsqMJbfiConDvX35vy5KJ5c3O'
        self.__END_POINT: str = f'https://script.google.com/macros/s/{self.__TOKEN}/exec?sheet={self.__SHEET}'

    def get_end_point(self) -> dict:
        """
        Retorna um dicionario com atributos da class.

        **Returns:**
        - *dict*
        ```python
        dicionario = {
            'sheet': __SHEET__,
            'token': __TOKEN__,
            'point': __END_POINT__
        }
        ```
        """
        return {
            'sheet': self.__SHEET,
            'token': self.__TOKEN,
            'point': self.__END_POINT
        }

    def request_frame(self, url: Union[str, None] = None) -> dict:
        """
        Faz um pedido ao servidor que contem a planilha do **google.sheet**.

        **Args:**
        - **url** : *Union[str, None]* = `None`\n
        Se for vazia requisita na folha principal do argumento sheet

        **Returns:**
        - *dict* \n
        Em caso de error -> ```{ 'error' : 400 }```
        """
        d = requests.get(self.__END_POINT) if url == None else requests.get(str(url))
        return dict(d.json()) if d.status_code == 200 else { 'error' : 400 }

    def clean_frame(
        self,
        data: dict,
        col: list[str] = ['Card Type', 'Card Name', 'Condition', 'Remarks']
    ) -> pd.DataFrame:
        """
        Limpa qualquer folha da planilha e retorna como DataFrame.

        **Args:**
        - **data** : *dict*\n
        Dicionario com dados da planilha
        - **col** : *list*\n
        Colunas que serao selecionadas

        **Returns:**
        - *DataFrame*
        """
        df = pd.DataFrame(data['folha'], columns=data['folha'][0])
        return df[col].copy()

    def save(self, data: pd.DataFrame) -> bool:
        """
        Cria o diretório `/var/` se nao existir e salva o DataFrame como CSV.

        **Args:**
        - **data** : *DataFrame*\n
        DataFrame que sera salvo como CSV separado por `;`

        **Returns:**
        - *bool*\n
        `True` se o arquivo for criado, `False` para falha.
        """
        var_dir = os.path.join(os.path.dirname(__file__), 'var')
        if not os.path.exists(var_dir):
            os.mkdir(var_dir)

        data.columns = data.columns.str.replace(' ', '_').str.lower()
        download = os.path.join(var_dir, f'{self.__SHEET}.csv')
        data.to_csv(download, sep=';', index=False)
        return os.path.exists(download)

    def download_banlist(self) -> bool:
        """
        Realiza o download dos dados da banlist

        **Returns:**
        - *bool*\n
        `False` para falha da requisicao, `True` se funcionar tudo perfeitamente
        """
        link = self.__END_POINT[0:self.__END_POINT.find('='):] + '=Home'
        dados = self.request_frame(link)
        return False if ('error' in dados) else self.save(self.clean_frame(dados))


class BanSheetWebAsync:
    """
    Estrutura de dados `Async` para Multiplas requisicoes a folhas 
    da planilha da Banlist.
    """
    def __init__(self) -> None:
        self.__BAN_SHEET_WEB__ = BanSheetWeb()

    def __mount_link__(self, frames: list[str]) -> list[str]:
        """
        Monta uma lista de end points para cada sheet na variavel frames.

        **Args:***
        - **frames** : *list[str]*\n
        Uma lista com o nome das `folhas/sheets` desejados

        **Returns:**
        - *list[str]*\n
        Lista com cada link de end point
        """
        dicionario = self.__BAN_SHEET_WEB__.get_end_point()
        sheet = dicionario['sheet']
        point = dicionario['point']
        return list(map(lambda x: point.replace(sheet, x), frames))

    async def fetch_data(self, links: list[str]) -> list[dict]:
        """
        Requisita uma serie de links, retorna uma lista com as respostas.

        **Args:**
        - **links** : *list[str]*\n
        Lista com cada link de requisicao de resposta `.json`

        **Returns:**
        - *list[dict]*\n
        Lista com as respostas em `dict`
        """
        function_ = self.__BAN_SHEET_WEB__.request_frame
        tasks = [asyncio.to_thread(function_, l) for l in links]
        result = await asyncio.gather(*tasks)
        return result

    async def mount_frame(self, sheet_dict: list[dict]) -> list[DataFrame]:
        """
        Limpa cada dicionario requisitado, retorna uma lista com DataFrame.

        **Args:**
        - **sheet_dict** : *list[dict]*\n
        Lista de dicionarios recebidos por requisicao async

        **Returns:**
        - *list[DataFrame]*\n
        Lista com os dados em forma de DataFrame
        """
        function_ = self.__BAN_SHEET_WEB__.clean_frame
        tasks = [asyncio.to_thread(function_, d) for d in sheet_dict]
        result = await asyncio.gather(*tasks)
        return result

    async def write_frame(
        self,
        frames: list[DataFrame],
        sheet_names: list[str]
    ) -> list[str]:
        """
        Cria o diretório `/var/` se nao existir e salva os DataFrames como CSV,\n
        os nomes dos arquivos serao passados em sheet_names.

        **Args:**
        - **frames** : *list[DataFrame]*\n
        Lista com uma sequencia de DataFrames para serem salvos
        - **sheet_names** : *list[str]*
        Lista com nomes de cda DataFrame em ordem

        **Returns:**
        - *None*
        """
        var_dir = str(os.path.join(os.path.dirname(__file__), 'var'))
        if not os.path.exists(var_dir):
            os.mkdir(var_dir)

        stack_paths = []
        for f, name in zip(frames, sheet_names):
            f.columns = f.columns.str.replace(' ', '_').str.lower()
            download_path = str(os.path.join(var_dir, f"{name}.csv"))
            stack_paths.append(download_path)
            f.to_csv(download_path, sep=';', index=False)

        return stack_paths

    async def creat_files(self, sheets: list[str]) -> bool:
        """
        Requisita cada sheet e cria uma pasta `/var/`, 
        retorna `True` se todos forem baixados.

        **Args:**
        - **link_sheet** : *list[str]*\n
        Lista com os end points de cada folha
        - **sheets** : *list[str]*
        Lista com os nomes de cada folha do sheet, tambem sera o nome do arquivo

        **Returns:**
        - None
        """
        lista_dicts = await self.fetch_data(self.__mount_link__(sheets))
        lista_dados = await self.mount_frame(lista_dicts)
        paths_files = await self.write_frame(lista_dados, sheets)
        return all(map(lambda x: os.path.exists(x), paths_files))

    def async_download_run(self, f: list[str]) -> bool:
        """
        Realiza o download Async para cada folha na banlist

        **Args:**
        - **f** : *list[str]*\n
        Lista com nome das folhas da planilha

        **Returns:**
        - *bool*
        `True` se todos forem baixados corretamente, `False` do contrario
        """
        return asyncio.run(self.creat_files(f))

if __name__ == '__main__':
    ban_web = BanSheetWeb()
    dados = ban_web.download_banlist()
    print('Baixei Home') if dados else print('Nao baixei Home')

    ban = BanSheetWebAsync()
    sheets = ['Forbbiden', 'Limited', 'Semi-limited', 'Unlimited']
    mult_dados = ban.async_download_run(sheets)
    print('Baixei todas da lista') if mult_dados else print('Nao baixei a lista')
