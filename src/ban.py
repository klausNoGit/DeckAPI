#
#   Python 3.11.10
#

import os
import shutil
import asyncio
import requests
from typing import Union

import pandas as pd         # typing: ignore
from pandas import DataFrame


class BanSheetWeb:
    """
    Estrutura de dados responsável pelo gerenciamento de requisições ao Google Sheets e
    processamento de dados em rede e arquivos locais, ambos relacionados à banlist do Mochila Champions.

    Args:
        sheet (str): Nome da folha (sheet) na planilha do Google Sheets para a qual será feita a requisição.

    Returns:
        None: Não retorna valores, apenas executa operações relacionadas à requisição dos dados.
    """
    def __init__(self, sheet: str = 'Home') -> None:
        self.__SHEET: str = sheet
        self.__TOKEN: str  = 'AKfycby08zhGHOhwy3iQEEnnFbmXmA9vr5pW4JS83Usgci1MsqMJbfiConDvX35vy5KJ5c3O'
        self.__END_POINT: str = f'https://script.google.com/macros/s/{self.__TOKEN}/exec?sheet={self.__SHEET}'

    def get_end_point(self) -> dict:
        """
        Retorna um dicionário contendo os atributos da classe.

        Returns:
            dict: Dicionário com os atributos da classe, conforme exemplo abaixo:
        ```python
        {
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
        Faz uma requisição ao servidor que contém a planilha do Google Sheets.

        Args:
            url (Union[str, None], opcional): URL do servidor da planilha.
                Se não fornecido, a requisição será feita na folha principal do argumento `sheet`.

        Returns:
            dict: Dicionário contendo os dados da requisição.\n
            Em caso de erro, retorna:
        ```python
        { 'error': 400 }
        ```
        """
        d = requests.get(self.__END_POINT) if url == None else requests.get(str(url))
        return dict(d.json()) if d.status_code == 200 else { 'error' : 400 }

    def clean_frame(
        self,
        data: dict,
        col: list[str] = ['Card Type', 'Card Name', 'Condition', 'Remarks']
    ) -> pd.DataFrame:
        """
        Limpa qualquer folha da planilha e retorna os dados como um DataFrame.

        Args:
            data (dict): Dicionário contendo os dados da planilha.
            col (list): Colunas que serão selecionadas para o DataFrame.

        Returns:
            DataFrame: Um DataFrame com os dados da planilha,
            filtrados pelas colunas especificadas.
        """
        df = pd.DataFrame(data['folha'], columns=data['folha'][0])
        return df[col].copy()

    def save(self, data: pd.DataFrame) -> bool:
        """
        Cria o diretório `/var/` se não existir e salva o DataFrame como um arquivo CSV.

        Args:
            data (DataFrame): DataFrame que será salvo como CSV, com separador `|`.

        Returns:
            bool: Retorna `True` se o arquivo for criado com sucesso, ou `False` em caso de falha.
        """
        var_dir = os.path.join(os.path.dirname(__file__), 'var')
        if not os.path.exists(var_dir):
            os.mkdir(var_dir)

        data.columns = data.columns.str.replace(' ', '_').str.lower()
        download = os.path.join(var_dir, f'{self.__SHEET}.csv')
        data.to_csv(download, sep='|', index=False)
        return os.path.exists(download)

    def download_banlist(self) -> bool:
        """
        Realiza o download dos dados da banlist.

        Returns:
            bool: Retorna `False` em caso de falha na requisição,
            ou `True` se o download for bem-sucedido.
        """
        link = self.__END_POINT[0:self.__END_POINT.find('='):] + '=Home'
        dados = self.request_frame(link)
        return False if ('error' in dados) else self.save(self.clean_frame(dados))

    def var_delete(self) -> bool:
        """
        Deleta o diretório 'var' com todo o seu conteúdo,
        localizado no mesmo diretório deste arquivo.

        Returns:
            bool: `True` se o diretório foi deletado com sucesso,
            `False` se o diretório não existir.
        """
        atual_dir = os.path.dirname(__file__)
        dir_var = str(os.path.join(atual_dir, 'var'))
        if os.path.exists(dir_var) and os.path.isdir(dir_var):
            shutil.rmtree(dir_var)
            return True
        return False

class BanSheetWebAsync:
    """
    Estrutura de dados assíncrona (Async) para realizar múltiplas requisições
    às folhas da planilha da Banlist.
    """
    def __init__(self) -> None:
        self.__BAN_SHEET_WEB__ = BanSheetWeb()

    def __mount_link__(self, frames: list[str]) -> list[str]:
        """
        Monta uma lista de endpoints para cada sheet na variável `frames`.

        Args:
            frames (list[str]): Nomes das `folhas/sheets` desejadas.

        Returns:
            list[str]: Lista contendo os links de endpoint para cada folha.
        """
        dicionario = self.__BAN_SHEET_WEB__.get_end_point()
        sheet = dicionario['sheet']
        point = dicionario['point']
        return list(map(lambda x: point.replace(sheet, x), frames))

    async def fetch_data(self, links: list[str]) -> list[dict]:
        """
        Requisita uma série de links e retorna uma lista com as respostas.

        Args:
            links (list[str]): Lista com os links de requisição
                que retornam respostas no formato `.json`.

        Returns:
            list[dict]: Lista com as respostas em formato `dict` para cada link.
        """
        function_ = self.__BAN_SHEET_WEB__.request_frame
        tasks = [asyncio.to_thread(function_, l) for l in links]
        result = await asyncio.gather(*tasks)
        return result

    async def mount_frame(self, sheet_dict: list[dict]) -> list[DataFrame]:
        """
        Limpa cada dicionário requisitado e retorna uma lista com DataFrames.

        Args:
            sheet_dict (list[dict]): Lista de dicionários recebidos por requisição assíncrona.

        Returns:
            list[DataFrame]: Lista contendo os dados em formato de DataFrame.
        """
        function_ = self.__BAN_SHEET_WEB__.clean_frame
        tasks = [asyncio.to_thread(function_, d) for d in sheet_dict]
        result = await asyncio.gather(*tasks)
        return result

    async def write_frame(self, frames: list[DataFrame], sheet_names: list[str]) -> list[str]:
        """
        Cria o diretório `/var/` se não existir e salva os DataFrames como arquivos CSV.\n
        Os nomes dos arquivos serão passados na lista `sheet_names`.

        Args:
            frames (list[DataFrame]): Sequência de DataFrames que serão salvos como CSV.
            sheet_names (list[str]): Nomes de cada DataFrame, na ordem correspondente.

        Returns:
            list[str]: Lista com os caminhos completos
            dos arquivos CSV salvos no diretório `/var/`.
        """
        var_dir = str(os.path.join(os.path.dirname(__file__), 'var'))
        if not os.path.exists(var_dir):
            os.mkdir(var_dir)

        stack_paths = []
        for f, name in zip(frames, sheet_names):
            f.columns = f.columns.str.replace(' ', '_').str.lower()
            download_path = str(os.path.join(var_dir, f"{name}.csv"))
            stack_paths.append(download_path)
            f.to_csv(download_path, sep='|', index=False)
        return stack_paths

    async def creat_files(self, sheets: list[str]) -> bool:
        """
        Requisita os dados de cada folha do Google Sheets e cria uma pasta `/var/`.\n
        Retorna `True` se todos os arquivos forem baixados com sucesso.

        Args:
            sheets (list[str]): Lista com os nomes de cada folha do Google Sheets.\n
                Esses nomes também serão usados como nomes dos arquivos.

        Returns:
            bool: Retorna `True` se todos os arquivos forem n\
            baixados e salvos corretamente, `False` caso contrário.
        """
        lista_dicts = await self.fetch_data(self.__mount_link__(sheets))
        lista_dados = await self.mount_frame(lista_dicts)
        paths_files = await self.write_frame(lista_dados, sheets)
        return all(map(lambda x: os.path.exists(x), paths_files))

    def async_download_run(self, f: list[str]) -> bool:
        """
        Realiza o download assíncrono de dados para cada folha da banlist.

        Args:
            f (list[str]): Nomes das folhas da planilha que serão baixadas.

        Returns:
            bool: Retorna `True` se todos os arquivos forem \n
            baixados corretamente, `False` caso contrário.
        """
        return asyncio.run(self.creat_files(f))

    def var_delete(self) -> bool:
        """
        Deleta o diretório 'var' com todo o seu conteúdo,
        localizado no mesmo diretório deste arquivo.

        Returns:
            bool: `True` se o diretório foi deletado com sucesso,
            `False` se o diretório não existir.
        """
        return self.__BAN_SHEET_WEB__.var_delete()

if __name__ == '__main__':
    ban_web = BanSheetWeb()
    if ban_web.var_delete():
        print('"/VAR/" sucess delet')
    else:
        print('"/VAR/" not delet')

    dados = ban_web.download_banlist()
    if ban_web.download_banlist():
        print('Operation success!!!')
    else:
        print('Not operation success!!!')

    ban = BanSheetWebAsync()
    ban.var_delete()
    sheets = ['Home', 'Forbidden', 'Limited', 'Semi-limited', 'Unlimited']
    if ban.async_download_run(sheets):
        print('Async operation success!!!')
    else:
        print('Async not operation success!!!')
