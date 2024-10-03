#
#   Python 3.11.10
#

import os
import sqlite3
import asyncio
import requests
import pandas as pd         # typing: ignore


class BanSheetWeb:
    """
    Estrutura de dados criada para lidar com requisicoes ao google.sheet,
    processamento de dados em rede e arquivos locais, ambos referente
    a banlist do Mochila Champions.
    
    Args:
    -----
    - `sheet` str: Nome da folha da planilha que deve ser feita a requisicao.
    
    Returns:
    --------
    - None
    """
    def __init__(self, sheet: str = 'Home') -> None:
        self.__SHEET: str = sheet
        self.__TOKEN: str  = 'AKfycby08zhGHOhwy3iQEEnnFbmXmA9vr5pW4JS83Usgci1MsqMJbfiConDvX35vy5KJ5c3O'
        self.__END_POINT: str = f'https://script.google.com/macros/s/{self.__TOKEN}/exec?sheet={self.__SHEET}'

    def mount_link(self, frames: list[str]) -> list[str]:
        """
        Monta uma lista de end points para cada sheet dentro do Frame.
        
        Args:
        -----
        - frames : list[str]
            Uma lista com o nome dos sheets desejados
        
        Returns:
        --------
        - list[str] : lista com cada link de end point
        """
        return list(map(
            lambda x: self.__END_POINT.replace(self.__SHEET, x), frames
        ))

    def request_frame(self, url: str = '') -> dict:
        """
        Faz um pedido ao servidor que contem a planilha do google.sheet.
        
        Args:
        -----
        - url : str
            Se for vazia requisita na folha principal do argumento sheet
        
        Returns:
        --------
        - dict : Com dados ou error -> { 'error' : 400 }
        """
        d = requests.get(self.__END_POINT) if url == '' else requests.get(url)
        return dict(d.json()) if d.status_code == 200 else { 'error' : 400 }

    def clean_frame(
        self,
        data: dict,
        col: list = [
            'Card Type',
            'Card Name',
            'Condition',
            'Remarks'
        ]
    ) -> pd.DataFrame:
        """
        Limpa qualquer folha do parametro data e retorna como DataFrame.
        
        Args:
        -----
        - data : dict
            Dicionario com dados da folha passada como argumento para class
        
        Returns:
        --------
        - DataFrame
        """
        df = pd.DataFrame(data['folha'], columns=data['folha'][0])
        return df[col].copy()

    def save(
        self,
        data: pd.DataFrame
    ) -> None:
        """
        Salva o DataFrame em `.csv` com nome do paramentro em BanSheetWeb.

        Returns:
        --------
        - bool: True se o arquivo for criado, False para falha.
        """
        var_dir = str(os.path.join(os.path.dirname(__file__), 'var'))
        if not os.path.exists(var_dir):
            os.mkdir(var_dir)

        data.columns = data.columns.str.replace(' ', '_').str.lower()
        download = str(os.path.join(var_dir, f'{self.__SHEET}.csv'))
        data.to_csv(download, sep=';', index=False)


class BanSheetWebAsync:
    """
    Estrutura de dados Asyncio para Multiplas requisicoes
    """
    def __init__(self) -> None:
        self.__BAN_SHEET_WEB__ = BanSheetWeb()

    async def fetch_data(
        self,
        links: list[str]
    ) -> list[dict]:
        """
        Requisita uma serie de links, retorna uma lista com as respostas.
        
        Args:
        -----
        - links : list[str]
            Lista com cada link de requisicao com resposta `.json`
        
        Returns:
        --------
        - list[str] : Lista com as respostas em dict
        """
        function_ = self.__BAN_SHEET_WEB__.request_frame
        tasks = [asyncio.to_thread(function_, l) for l in links]
        result = await asyncio.gather(*tasks)
        return result

    async def mount_frame(
        self,
        sheet_dict: list[dict]
    ) -> list[pd.DataFrame]:
        """
        Limpa cada dicionario requisitado, retorna uma lista com DataFrame.
        
        Args:
        -----
        - sheet_dict: list[dict]
            Lista de dicionarios recebidos por requisicao em processo async
        
        Returns:
        --------
        - list[pd.DataFrame] : Lista com os dados em forma de DataFrame
        """
        function_ = self.__BAN_SHEET_WEB__.clean_frame
        tasks = [asyncio.to_thread(function_, d) for d in sheet_dict]
        result = await asyncio.gather(*tasks)
        return result

    async def write_frame(
        self,
        frames: list[pd.DataFrame],
        sheet_names: list[str]
    ) -> None:
        """
        Salva DataFrames em arquivos CSV com nomes fornecidos em sheet_names.
        
        Args:
        -----
        - frames : list[pd.DataFrame]
            Lista com uma sequencia de DataFrames para serem salvos
        - sheet_names : list[str]
            Lista com nomes de cda DataFrame em ordem
        
        Returns:
        --------
        - None
        """
        var_dir = str(os.path.join(os.path.dirname(__file__), 'var'))
        if not os.path.exists(var_dir):
            os.mkdir(var_dir)

        for f, name in zip(frames, sheet_names):
            f.columns = f.columns.str.replace(' ', '_').str.lower()
            download_path = str(os.path.join(var_dir, f"{name}.csv"))
            f.to_csv(download_path, sep=';', index=False)

    async def creat_files(
        self,
        links_sheet: list[str],
        sheets: list[str]
    ) -> None:
        """
        Requisita cada link sheet e baixa o `.csv` de cada DataFrame
        
        Args:
        -----
        - link_sheet: list[str]
            Lista com os end points de cada folha
        - sheets: list[str]
            Lista com os nomes de cada folha do sheet, tambem sera o nome do arquivo
        
        Returns:
        --------
        - None
        """
        lista_dicts = await self.fetch_data(links_sheet)
        lista_dados = await self.mount_frame(lista_dicts)
        await self.write_frame(lista_dados, sheets)


if __name__ == '__main__':
    ban_web = BanSheetWeb()
    sheets = ['Home', 'Forbbiden', 'Limited', 'Semi-limited', 'Unlimited']
    lista = ban_web.mount_link(sheets)
    ban = BanSheetWebAsync()
    asyncio.run(ban.creat_files(lista, sheets))
    