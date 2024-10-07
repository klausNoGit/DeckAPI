#
#   Python 3.11.10
#
import os
from os import PathLike
from os.path import join, dirname, abspath, exists

from pathlib import Path
from itertools import chain
from typing import Union

import numpy as np
from pandas import DataFrame, concat


class StructureFile:
    def cd_dir(self, dir: Union[str, PathLike]) -> list:
        """
        Lista caminhos absolutos de cada diretorio dentro de `dir`.
        
        **Args:**
        - **dir** : *Union[str, PathLike]*\n
        Diretorio raiz que sera lido
        
        **Returns:**
        - *list*\n
        Lista com os caminhos em `string` ordenada, ou uma lista vazia
        """
        dir = abspath(dir)
        if exists(dir):
            dir_path = [
                str(d.absolute()) for d in Path(dir).iterdir() if d.is_dir()
            ]
            dir_path.sort()
            return dir_path
        else:
            return []
    
    def path_files(self, iter: Union[str, list[str], PathLike]) -> list:
        """
        Lista de caminhos absolutos de cada arquivo em sub-diretorio.
        
        **Args:**
        - **iter** : *Union[str, list[str], PathLike]*
        Um diretorio literal de mapeamento, ou um diretorio com sub-diretorios
        
        **Returns:**
        - *list*
        Lista com caminhos absolutos de cada arquivo
        """
        if isinstance(iter, str) or isinstance(iter, PathLike):
            dir_ = abspath(iter)
            lista_dir = list(map(lambda x: join(dir_, x), os.listdir(dir_)))
            lista_dir.sort()
            return lista_dir
        else:
            dir_ = list(map(lambda x: abspath(x), iter))
            dir_.sort()

            funct_ = lambda d, f: list(map(lambda x: join(d, x), f))
            return list(chain(*map(
                lambda d: funct_(d, os.listdir(d)), dir_)
            ))

    def read_file_arquetype(self, file: Union[str, PathLike]) -> DataFrame:
        """
        Le um arquivo `TXT` referente aos arquetipos, retorna um DataFrame.
        
        **Args:**
        - **file** : *Union[str, PathLike]*
        
        **Returns**:
        - *DataFrame*
        """
        file = Path(file)
        arquetipo = file.name.replace('.txt', '')
        arquivo = open(file.absolute(), 'r', encoding='utf-8')
        conteudo = arquivo.readlines()
        arquivo.close()

        def limpar_conteudo(string: str) -> str:
            if 'Main Deck:\n' in string \
                or 'Extra Deck:\n' in string or 'Side Deck:\n' in string:
                return '\n'
            else:
                string = string.replace(' x1\n', '')
                string = string.replace(' x2\n', '')
                return string.replace(' x3\n', '')

        dados = list(filter(
            lambda x: '\n' not in x, list(map(limpar_conteudo, conteudo))
        ))
        return DataFrame({
            'card': dados,
            'arquetype': np.full(len(dados), arquetipo)
        })

    def in_csv(self, df: DataFrame, out: Union[str, PathLike], name: str) -> None:
        """
        Baixa DataFrame como `CSV` com diretorio e nomes especificos.
        
        **Args:**
        - **df** : DataFrame\n
        DataFrame que sera salvo
        - **out** : *Union[str, PathLike]*\n
        Diretorio de saida do arquivo
        - **name** : *str*\n
        Nome do arquivo com `.csv` no fim

        **Returns:**
        - None
        """
        out = Path(out).absolute()
        if not os.path.exists(out):
            os.mkdir(out)
        df.to_csv(join(out, name), sep='|', index=False)

if __name__ == '__main__':
    struct = StructureFile()
    SRC = dirname(__file__)
    CSV = join(SRC, 'csv')
    ARQUETYPES = SRC.replace('src', 'arquetypes')

    lista_dir = struct.cd_dir(ARQUETYPES)
    arquivos = struct.path_files(lista_dir)
    dfs = [struct.read_file_arquetype(f) for f in arquivos]
    struct.in_csv(concat(dfs, axis=0), CSV, 'abs.csv')
