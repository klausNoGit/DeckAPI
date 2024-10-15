#
# Python 3.11.10
#

import os
import asyncio
import requests
from os.path import join, exists, abspath, dirname

from typing import Union, Literal, List, Dict
from pandas import DataFrame

class CardGame:
    """
    Estrutura de dados criada para lidar com requisicoes ao google.sheet,
    processamento de dados em rede e arquivos locais, ambos referente
    ao Card Game do YU-GI-OH.

    Args:
        sheet (str) : Nome da folha na planilha que deve ser feita a requisicao.

    Returns:
        None
    """
    def __init__(self, sheet: str = 'monster') -> None:
        self.__SHEET: str = sheet
        self.__TOKEN: str = 'AKfycbxMNLxw_szg45McBHh6sajiiuOiJyVkgFvnAp3vaY70E9xWw8_XMj4SGZ0A5_5x_gIezg'
        self.__END_POINT: str = f'https://script.google.com/macros/s/{self.__TOKEN}/exec?sheet={self.__SHEET}'

    def get_end_point(self) -> dict:
        """
        Retorna um dicionario com atributos da class.

        Returns:
            dict:
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
        Faz um pedido ao servidor que contem a planilha do google.sheet.

        Args:
            url (Union[str, None]): `None` por padrao. Se for vazia requisita na folha principal do argumento sheet

        Returns:
            dict : Em caso de error -> ```{ 'error' : 400 }```
        """
        d = requests.get(self.__END_POINT) if url == None else requests.get(str(url))
        return dict(d.json()) if d.status_code == 200 else { 'error' : 400 }

    def mount_frame(self, data: dict, sheet: str = 'monster') -> DataFrame:
        """
        Monta uma folha da planilha e retorna como DataFrame.

        Args:
            data (dict) : Dicionario com dados da planilha.
            sheet (str) : Folha padrao da planilha.

        Returns:
            DataFrame
        """
        return DataFrame(data[sheet], columns=data['col'])

    def save(self, data: DataFrame, name: str) -> bool:
        """
        Cria o diretório `/cache/` se nao existir e salva o DataFrame como CSV.

        Args:
            data (DataFrame): DataFrame que sera salvo como CSV separado por `|`
            name (str): Nome do CSV que sera salvo.

        Returns:
            bool :
                `True` se o arquivo for criado, `False` para falha.
        """
        cache_dir = join(dirname(__file__), 'cache')
        if not exists(cache_dir):
            os.mkdir(cache_dir)

        download = join(cache_dir, f'{name}.csv')
        data.to_csv(download, sep='|', index=False)
        return exists(download)

class CardGameAsync:
    """
    Estrutura de dados `Async` para Multiplas requisicoes a folhas 
    da planilha do Card Game.
    """
    def __init__(self) -> None:
        self.__CARD_GAME__ = CardGame()

    def __mount_link__(self, frames: list[str]) -> list[str]:
        """
        Monta uma lista de end points para cada sheet na cacheiavel frames.

        Args:
            frames (list[str]): Nome das `folhas/sheets` desejados

        Returns:
            list[str]: Lista com cada link de end point
        """
        dicionario = self.__CARD_GAME__.get_end_point()
        sheet = dicionario['sheet']
        point = dicionario['point']
        return list(map(lambda x: point.replace(sheet, x), frames))

    async def fetch_data(self, links: list[str]) -> list[dict]:
        """
        Requisita uma serie de links, retornando uma lista com as respostas.

        Args:
            links (list[str]): Lista com cada link da requisicao em resposta JSON.

        Returns:
            list[dict]: Lista com as respostas em `dict`.
        """
        function_ = self.__CARD_GAME__.request_frame
        tasks = [asyncio.to_thread(function_, l) for l in links]
        result = await asyncio.gather(*tasks)
        return result

    async def mount_frames(
        self,
        sheet_dict: list[dict],
        names: list[str]
    ) -> list[DataFrame]:
        """
        Limpa cada dicionario requisitado, retorna uma lista com DataFrame.

        Args:
            sheet_dict (list[dict]): Lista de dicionarios recebidos por requisicao async

        Returns:
            list[DataFrame]: Lista com os dados em forma de DataFrame
        """
        function_ = self.__CARD_GAME__.mount_frame
        tasks = []
        for s, n in zip(sheet_dict, names):
            tasks.append(asyncio.to_thread(function_, s, n))

        result = await asyncio.gather(*tasks)
        return result

    async def save_frames(self, frames: list[DataFrame], sheet_names: list[str]) -> list[str]:
        """
        Cria o diretório `/cache/` se nao existir e salva os DataFrames como CSV,
        os nomes dos arquivos serao passados em sheet_names.

        Args:
            frames (list[DataFrame]): Sequencia de DataFrames para serem salvos.
            sheet_names (list[str]): Lista com nomes de cada DataFrame em ordem.

        Returns:
            None
        """
        cache_dir = str(join(dirname(__file__), 'cache'))
        if not exists(cache_dir):
            os.mkdir(cache_dir)

        stack_paths = []
        for f, name in zip(frames, sheet_names):
            f.columns = f.columns.str.replace(' ', '_').str.lower()
            download_path = str(join(cache_dir, f"{name}.csv"))
            stack_paths.append(download_path)
            f.to_csv(download_path, sep='|', index=False)

        return stack_paths

    async def creat_files(self, sheets: list[str]) -> bool:
        """
        Requisita cada sheet e cria uma pasta `/cache/`, 
        retorna `True` se todos forem baixados.

        Args:
            sheets (list[str]): Nomes de cada folha do sheet, sera o nome dos arquivos.

        Returns:
            bool
                `True` se todos os arquivos foram criados, `False` para falha.
        """
        lista_dicts = await self.fetch_data(self.__mount_link__(sheets))
        lista_dados = await self.mount_frames(lista_dicts, sheets)
        paths_files = await self.save_frames(lista_dados, sheets)
        return all(map(lambda x: exists(x), paths_files))

    def async_save_run(self, f: list[str]) -> bool:
        """
        Realiza o download Async para cada folha de Card Game.

        Args:
            f (list[str]): Nomes das folhas da planilha

        Returns:
            bool
                `True` se todos forem baixados corretamente, `False` do contrario
        """
        return asyncio.run(self.creat_files(f))

if __name__ == '__main__':
    card_game = CardGameAsync()
    sheets = ['monster', 'spell', 'trap']
    print(card_game.async_save_run(sheets))
