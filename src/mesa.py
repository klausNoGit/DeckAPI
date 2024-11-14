#
# Python 3.11.10
#
import os
import math
from os import PathLike
from typing import List, Dict, Tuple, Union, Literal

import numpy as np
import pandas as pd
from pandas import DataFrame

from ydke import CoreYDKE
from card import CardGameAsync
from ban import BanSheetWeb, BanSheetWebAsync


class MesaCore(CoreYDKE):
    def __init__(self) -> None:
        super().__init__()        
        self.__CARD_GAME_ASYNC__: CardGameAsync = CardGameAsync()
        self.__BANLIST_WEB__: BanSheetWeb = BanSheetWeb()
        self.__BANLIST_ASYNC__: BanSheetWebAsync = BanSheetWebAsync()

    def download_async_dependencias(self) -> bool:
        """
        Baixa dados do jogo e salva as informações necessárias em `cache/` e `var/`.

        Returns:
            bool: True se todos os downloads forem bem-sucedidos, False caso contrário.
        """
        sheet_ban = ['Forbidden', 'Limited', 'Semi-limited', 'Unlimited']
        sheet_card = ['min', 'complet', 'monster', 'spell', 'trap']
        return all([
            self.__CARD_GAME_ASYNC__.async_save_run(sheet_card),
            self.__BANLIST_WEB__.request_frame(),
            self.__BANLIST_ASYNC__.async_download_run(sheet_ban)
        ])

    def read_cache(self, arq: str, lim: str = ';') -> DataFrame:
        """
        Lê um DataFrame de um arquivo CSV armazenado em cache.

        A função busca o arquivo especificado (`arq`) no diretório
        de cache e o carrega em um DataFrame.

        Args:
            arq (str): Nome do arquivo CSV a ser lido.

        Returns:
            DataFrame: DataFrame contendo os dados lidos do arquivo.
        """
        file = os.path.join(os.path.dirname(__file__), 'cache', arq)
        data_frame_cache = pd.read_csv(file, sep=lim, encoding='utf-8')
        return data_frame_cache

    def monta_parte_deck(
        self,
        part: Literal['main', 'side', 'extra'],
        array: List[int]
    ) -> DataFrame:
        """
        Monta uma das partes do deck passada como argumento, retorna como DataFrame.
        
        Args:
            part (Literal['main', 'side', 'extra']) : Parte que será montada.
            array (List[int]) : Código base 32 bits das cartas.
        
        Returns:
            Dataframe: Conjunto de dados da parte do deck.
            - Colunas **constantes** do conjunto retornado:
                - cod
                - card_name
                - tipo
                - effect
                - arquetype
                - qtd_copy
                - categoria
        """
        data_frame_complet = self.read_cache('complet.csv')
        data_frame_complet['cod'] = data_frame_complet['cod'].astype(int)

        dados_deck_list = []
        for x in array:
            carta_encontrada = data_frame_complet.loc[
                data_frame_complet['cod'].isin([x])]

            if not carta_encontrada.empty:
                dados_deck_list.append(carta_encontrada.values[0].tolist())
            else:
                # Se o código da carta não estiver cadastrado no cache
                print(f"Warning: Não encontrei em 'cod' o valor: {x}")

        colunas_uteis = ['cod', 'card_name', 'tipo', 'effect', 'arquetype']
        df = DataFrame(dados_deck_list, columns=colunas_uteis)

        # descobrindo a quantidade de copias de cards
        df['qtd_copy'] = np.ones(df.shape[0], dtype=int)
        df = df.groupby(colunas_uteis).sum().reset_index()
        df['categoria'] = np.full(df.shape[0], part)
        df['cod'] = df['cod'].astype(int)
        return df.sort_values(by=['cod']).reset_index(drop=True)

    def read_link_deck_ydke(self, link: str) -> Tuple[DataFrame, DataFrame, DataFrame]:
        """
        Lê dados de um deck com criptografia YDKE,\n
        identifica arquétipos genéricos como mini-arquetipos e monta as
        seções `main`, `extra` e `side`.

        Args:
            link (str): URL do deck.

        Returns:
            Tuple[DataFrame]: DataFrames `main`, `extra` e `side` com arquétipos ajustados.
        """
        link = link.replace('\n', '').replace(' ', '').replace('\t', '')
        deck = self.read_url(link)
        mini_arquetipos = self.read_cache('min.csv')

        classificador = lambda x: 'generic' if any(
            min in x for min in mini_arquetipos['name']
        ) else x

        main = self.monta_parte_deck('main', deck['main'])
        main['arquetype'] = main['arquetype'].apply(classificador)

        extra = self.monta_parte_deck('extra', deck['extra'])
        extra['arquetype'] = extra['arquetype'].apply(classificador)

        side = self.monta_parte_deck('side', deck['side'])
        side['arquetype'] = side['arquetype'].apply(classificador)

        return main, extra, side


class Combination(MesaCore):
    """
    Estrutura de dados criada para realizar o cálculo de probabilidade de maior
    frequência de arquétipo no main deck do player. Consiste em atribuições de classificação
    conforme a regra 2.0 vigente do Mochila Champions acesse -> 
    (https://encurtador.com.br/eWXru)
    """
    def __init__(self, decklist: Union[str, PathLike]) -> None:
        """
        Contem estrutura de atributos para facil ascesso na classe filha `Mesa`
        
        Args:
            decklist (Union[str, PathLike]) : Link YDKE do deck ou arquivo.
        """
        super().__init__()

        if 'ydke://' in decklist:
            self.main, self.extra, self.side = self.read_link_deck_ydke(decklist)
            self.arquetipo, self.linear_main = self._construct_main_deck(self.main)
            self.linear_extra = self._construct_vetor(self.extra)
            self.linear_side  = self._construct_vetor(self.side)

    def _conta_frequencia_arquetipo_main_deck(self, part_deck: DataFrame) -> DataFrame:
        """
        Realiza a separação das colunas essenciais que se relacionam e faz a contagem
        com chave e valor de frequencia dividida pela base 10 Float.
        
        Args:
            part_deck (DataFrame) : Conjunto de dados do main deck.
        
        Returns:
            DataFrame : Main deck com novas colunas de frequencia e chave absoluta
        """
        pares_abs = part_deck[
            ['arquetype', 'qtd_copy']
        ].groupby(['arquetype']).sum().reset_index()
        pares_abs.columns = ['arquetype', 'freq_abs']
        pares_abs = pares_abs.sort_values(by=['freq_abs'], ascending=False)
        
        # Cria chaves absolutas do maior ao menor
        pares_abs['key_abs'] = range(len(pares_abs), 0, -1)

        # Encontra a maior ocorrencia de arquetipo
        array = pares_abs['freq_abs'].isin([pares_abs['freq_abs'].max()])
        array = pares_abs['arquetype'].loc[array].to_list()

        # Confere se o maior for generic, se for zera ele
        if array[0] == 'generic':
            pares_abs.loc[pares_abs['arquetype'] == 'generic', 'freq_abs'] = 0
        
        # Coloca em base 10 float e une com merge na parte principal
        pares_abs['freq_abs'] = pares_abs['freq_abs'] / 10
        df_merge = pd.merge(part_deck, pares_abs, how='left', on='arquetype')
        return df_merge.copy()

    def _conta_sub_frequence_main_deck(self, part_deck: DataFrame) -> DataFrame:
        """
        Executa a contagem de sub palavras no arquetipo divida por tabulação.
        Zera a combinação se o arquetipo de maior frequencia for 'generic',
        então cria duas colunas com chave e valor de frequencia
        dividida pela base 10 Float.
        
        Args:
            part_deck (DataFrame) : Conjunto de dados do main deck.
        
        Returns:
            DataFrame : Main deck com novas colunas de frequencia e chave absoluta
        """
        # Descompacta string de multiplos arquetipos
        # em uma lista de contagem de frequencia
        alg_freq = pd.Series('|'.join(
            part_deck.arquetype).replace(' | ', '|').split('|')
        )
        alg_freq = alg_freq.str.split(' ').explode().value_counts(
            ).reset_index(name='freq')

        # Coloca em base 10 float e cria chave de sub frequencia
        alg_freq.columns = ['arquetype', 'sub_freq']
        alg_freq['sub_freq'] = alg_freq['sub_freq'] / 10
        alg_freq['sub_key'] = range(len(alg_freq), 0, -1)
        
        # Zera a combinacao linear de arquetipo do 
        # tipo 'generic' se ele ainda for o maior
        array = alg_freq['sub_key'] == alg_freq['sub_key'].max()
        array = alg_freq['arquetype'].loc[array].to_list()
        if array[0] == 'generic':
            alg_freq.loc[alg_freq['sub_key'] == alg_freq['sub_key'].max(), 'sub_key'] = 0

        key = []
        frq = []
        # Procura uma palavra menor no conjunto de palavras do arquetipo
        # Para criar uma chave e valor da ocorrencia
        for j in part_deck.arquetype:
            for i in alg_freq.arquetype:
                if i in j:
                    key.append(
                        alg_freq.loc[
                            alg_freq['arquetype'].isin([i])
                        ].iloc[0].to_numpy()[2]
                    )
                    frq.append(
                        alg_freq.loc[
                            alg_freq['arquetype'].isin([i])
                        ].iloc[0].to_numpy()[1]
                    )
                    break

        part_deck['sub_key'] = key
        part_deck['sub_freq'] = frq
        return part_deck.copy()

    def _soma_linear_linhas_matrix(self, matriz: DataFrame) -> DataFrame:
        """
        Recolhe das colunas geradas em chave e frequência em uma soma em linhas,
        depois, cria mais uma coluna com a classificação.
        
        Args:
            matriz (DataFrame) : Frame completo do main deck.
        
        Returns:
            DataFrame: Matriz com mais duas colunas, 'soma' e 'cat_meta_dado'.
        """
        # Recolhe a matriz de frequencia e chaves 
        col_linear = ['key_abs', 'freq_abs', 'sub_key', 'sub_freq']
        matriz['soma'] = matriz[col_linear].sum(axis=1) # soma das linhas

        # Recolhe o escalar 'generic', se não tiver 
        # card 'generic' recolhe a media como escalar
        escalar_mediunico = matriz.loc[
            matriz['arquetype'].isin(['generic'])]['soma'].max()

        if math.isnan(escalar_mediunico):
            escalar_mediunico = int(matriz['soma'].mean().round())
        else:
            escalar_mediunico = escalar_mediunico.round(2)

        # Primeira categorização do arquetipo com base no escalar
        cat_meta_dado = []
        for v in matriz['soma']:
            if v == escalar_mediunico:
                cat_meta_dado.append(0)
            elif v < escalar_mediunico:
                cat_meta_dado.append(-1)
            else:
                cat_meta_dado.append(1)

        matriz['cat_meta_dado'] = cat_meta_dado        
        return matriz.copy()

    def _define_meta_dados_arquetipo(self, matriz: DataFrame) -> Tuple[str, DataFrame, DataFrame]:
        """
        Define a criação da coluna 'Y' com meta dados de classificação da carta,
        se ela é do arquetipo, generica ou invalida: [1, 0, -1]
        
        Args:
            matriz (DataFrame) : Frame completo com todas as chaves
                previamente calculadas.
        
        Returns:
            (Tuple[str, DataFrame, DataFrame]):
                - str Nome do arquétipo.
                - DataFrame Frame do deck main original.
                - DataFrame Matriz linear com eixo Y de classificação.
        """
        # Filtra todas as cartas do arquetipo se nao tiver
        # Então tudo é 'generic'
        frame_maior_ocorrencia = matriz.loc[matriz['cat_meta_dado'] == 1]
        if frame_maior_ocorrencia.shape[0] == 0:
            # Se as linhas forem zero significa que tudo é generico
            shape_matriz = matriz.shape[0]
            matriz['y'] = np.zeros(shape_matriz)
            matriz['arquetype_y'] = np.full(shape_matriz, 'generic')

            # Seleciona conjunto de dados
            colunas_separadas = [
                'freq_abs', 'key_abs', 'sub_key',
                'sub_freq', 'soma', 'cat_meta_dado',
                'y', 'arquetype_y'
            ]
            return 'generic', matriz[colunas_separadas].copy()
        else:
            ver_freq = frame_maior_ocorrencia['arquetype'].str.replace('|',' ')
            ver_freq = ver_freq.str.split(' ')
            ver_freq = ver_freq.explode().value_counts()
            ver_freq = ver_freq.reset_index(name='freq')

            # Determina maxima frequencia do arquetipo
            determinante = ver_freq.loc[ver_freq['freq'] == ver_freq['freq'].max()]

            # Se a frequencia forem iguais concatena e descobre o arquetipo
            # Se nao, recolhe a maior ocorrencia na primeira posição
            if len(set(determinante['freq'])) == 1:
                arquetypo = ' '.join(determinante['arquetype'])
            else:
                arquetypo = str(determinante['arquetype'].unique()[0])

            # Classifica arquetipo no DataFrame principal
            matriz['y'] = matriz['arquetype'].apply(
                lambda i: 1 if arquetypo in i else (
                    0 if i == 'generic' else -1)
                )

            # Mapeia as colunas de classificação com
            # base no arquetipo encontrado
            dicio_val = {0: 'generic', 1: arquetypo, -1: 'invalid'}
            matriz['arquetype_y'] = matriz['y'].apply(lambda x: dicio_val[x])

            # Seleciona conjunto de dados
            colunas_separadas = [
                'freq_abs', 'key_abs', 'sub_key',
                'sub_freq', 'soma', 'cat_meta_dado',
                'y', 'arquetype_y'
            ]
            return arquetypo, matriz[colunas_separadas].copy()

    def _construct_main_deck(self, main_deck: DataFrame) -> Tuple:
        """
        Constrói estrutura de dados do deck através do link passado,
        retorna uma tupla com sequencia de dados do deck. Sendo: **Arquetipo**,
        **main deck** e **matriz linear**.

        Args:
            url_ydke (str) : Link criptografado YDKE do deck.

        Returns:
            (Tuple[str, DataFrame, DataFrame]):
                - str Nome do arquétipo.
                - DataFrame Matriz linear com eixo Y de classificação.
        """
        main = self._conta_frequencia_arquetipo_main_deck(main_deck)
        main = self._conta_sub_frequence_main_deck(main)
        main = self._soma_linear_linhas_matrix(main)
        return self._define_meta_dados_arquetipo(main)

    def _construct_vetor(self, matrix: DataFrame) -> np.ndarray:
        """
        Cria o vetor linear correspondente ao Y. Função desenvolvida para
        extra e side.
        
        Args:
            matrix (DataFrame) : Frame do extra ou side deck.
        
        Returns:
            ndarray : Vetor com classificação de arquétipo em [0, 1, -1].
        """
        return np.select([
            matrix['arquetype'] == self.arquetipo,
            matrix['arquetype'] == 'generic',
            ~matrix['arquetype'].isin([self.arquetipo, 'generic'])
        ], [1, 0, -1], default=-1)


class Mesa(Combination):
    def __init__(self, deck_list: Union[str, PathLike]) -> None:
        super().__init__(deck_list)
        # Cache para numeros já cálculados
        self._cache_total_main: Union[None, int] = None
        self._cache_total_extra: Union[None, int] = None
        self._cache_total_side: Union[None, int] = None
        self._cache_total_cartas: Union[None, int] = None

        # Garante que arquetype no main deck original seja o nosso Y correto
        main_ = self.main.copy()
        main_['arquetype'] = self.linear_main['arquetype_y']
        self._cache_main = main_.copy()
        self._cache_qtd_cartas_arquetype_main: Union[None, int] = None
        self._cache_qtd_cartas_generic_main: Union[None, int] = None
        self._cache_qtd_cartas_invalid_main: Union[None, int] = None

        # Garante que arquetype no extra deck original seja o nosso Y correto
        extra_ = self.extra.copy()
        extra_['arquetype'] = pd.Series(self.linear_extra).map(
            {1: self.arquetipo, 0: 'generic', -1: 'invalid'}
        )
        self._cache_extra = extra_.copy()
        self._cache_qtd_cartas_arquetype_extra: Union[None, int] = None
        self._cache_qtd_cartas_generic_extra: Union[None, int] = None
        self._cache_qtd_cartas_invalid_extra: Union[None, int] = None

        # Garante que arquetype no side deck original seja o nosso Y correto
        side_ = self.side.copy()
        side_['arquetype'] = pd.Series(self.linear_side).map(
            {1: self.arquetipo, 0: 'generic', -1: 'invalid'}
        )
        self._cache_side = side_.copy()
        self._cache_qtd_cartas_arquetype_side: Union[None, int] = None
        self._cache_qtd_cartas_generic_side: Union[None, int] = None
        self._cache_qtd_cartas_invalid_side: Union[None, int] = None

    def _soma_qtd_cartas_frame(self, frame: Literal['main', 'extra', 'side'], comp: str) -> int:
        """
        Metodo interno para somar a quantidade de copias das cartas com base no parametro.
        
        Args:
            frame (Literal['main', 'extra', 'side']) : Quadro que será usado no cálculo.
            comp (str) : String de busca por igualdade -> arquetipo, 'generic' ou 'invalid'
        
        Returns:
            int : Soma quantitativa, resultado da algebra.
        """
        if frame == 'main':
            return int(
                self._cache_main.loc[
                    self._cache_main['arquetype'] == comp]['qtd_copy'].sum()
            )
        elif frame == 'extra':
            return int(
                self._cache_extra.loc[
                    self._cache_extra['arquetype'] == comp]['qtd_copy'].sum()
            )
        elif frame == 'side':
            return int(
                self._cache_side.loc[
                    self._cache_side['arquetype'] == comp]['qtd_copy'].sum()
            )

    @property
    def total_cartas_main(self) -> int:
        """Retorna a quantidade total de cartas do main deck."""
        if self._cache_total_main is None:
            self._cache_total_main = int(self.main['qtd_copy'].sum(axis=0))
        return self._cache_total_main

    @property
    def total_cartas_extra(self) -> int:
        """Retorna a quantidade total de cartas do extra deck."""
        if self._cache_total_extra is None:
            self._cache_total_extra = int(self.extra['qtd_copy'].sum(axis=0))
        return self._cache_total_extra

    @property
    def total_cartas_side(self) -> int:
        """Retorna a quantidade total de cartas do side deck."""
        if self._cache_total_side is None:
            self._cache_total_side = int(self.side['qtd_copy'].sum(axis=0))
        return self._cache_total_side

    @property
    def total_cartas_deck(self) -> int:
        """Retorna a quantidade total de cartas do deck."""
        if self._cache_total_cartas is None:
            self._cache_total_cartas = self.total_cartas_main + \
                                            self.total_cartas_extra + \
                                                self.total_cartas_side
        return self._cache_total_cartas

    @property
    def qtd_cartas_arquetype_main(self) -> int:
        """Retorna a quantidade total de cartas do arquetipo no main deck."""
        if self._cache_qtd_cartas_arquetype_main is None:
            self._cache_qtd_cartas_arquetype_main = self._soma_qtd_cartas_frame('main', self.arquetipo)
        return self._cache_qtd_cartas_arquetype_main

    @property
    def qtd_cartas_generic_main(self) -> int:
        """Retorna a quantidade total de cartas genericas no main deck."""
        if self._cache_qtd_cartas_generic_main is None:
            self._cache_qtd_cartas_generic_main = self._soma_qtd_cartas_frame('main', 'generic')
        return self._cache_qtd_cartas_generic_main

    @property
    def qtd_cartas_invalid_main(self) -> int:
        """Retorna a quantidade total de cartas invalidas no main deck."""
        if self._cache_qtd_cartas_invalid_main is None:
            self._cache_qtd_cartas_invalid_main = self._soma_qtd_cartas_frame('main', 'invalid')
        return self._cache_qtd_cartas_invalid_main

    @property
    def qtd_cartas_arquetype_extra(self) -> int:
        """Retorna a quantidade total de cartas do arquetipo no extra deck."""
        if self._cache_qtd_cartas_arquetype_extra is None:
            self._cache_qtd_cartas_arquetype_extra = self._soma_qtd_cartas_frame('extra', self.arquetipo)
        return self._cache_qtd_cartas_arquetype_extra

    @property
    def qtd_cartas_generic_extra(self) -> int:
        """Retorna a quantidade total de cartas genericas no extra deck."""
        if self._cache_qtd_cartas_generic_extra is None:
            self._cache_qtd_cartas_generic_extra = self._soma_qtd_cartas_frame('extra', 'generic')
        return self._cache_qtd_cartas_generic_extra

    @property
    def qtd_cartas_invalid_extra(self) -> int:
        """Retorna a quantidade total de cartas invalidas no extra deck."""
        if self._cache_qtd_cartas_invalid_extra is None:
            self._cache_qtd_cartas_invalid_extra = self._soma_qtd_cartas_frame('extra', 'invalid')
        return self._cache_qtd_cartas_invalid_extra

    @property
    def qtd_cartas_arquetype_side(self) -> int:
        """Retorna a quantidade total de cartas do arquetipo no side deck."""
        if self._cache_qtd_cartas_arquetype_side is None:
            self._cache_qtd_cartas_arquetype_side = self._soma_qtd_cartas_frame('side', self.arquetipo)
        return self._cache_qtd_cartas_arquetype_side

    @property
    def qtd_cartas_generic_side(self) -> int:
        """Retorna a quantidade total de cartas genericas no side deck."""
        if self._cache_qtd_cartas_generic_side is None:
            self._cache_qtd_cartas_generic_side = self._soma_qtd_cartas_frame('side', 'generic')
        return self._cache_qtd_cartas_generic_side

    @property
    def qtd_cartas_invalid_side(self) -> int:
        """Retorna a quantidade total de cartas invalidas no side deck."""
        if self._cache_qtd_cartas_invalid_side is None:
            self._cache_qtd_cartas_invalid_side = self._soma_qtd_cartas_frame('side', 'invalid')
        return self._cache_qtd_cartas_invalid_side

    def get_dados_deck(self) -> Dict:
        """Pega dados quantitativos do deck"""
        return {
            'arquetype_main': self.qtd_cartas_arquetype_main,
            'generic_main': self.qtd_cartas_generic_main,
            'invalid_main': self.qtd_cartas_invalid_main,

            'arquetype_extra': self.qtd_cartas_arquetype_extra,
            'generic_extra': self.qtd_cartas_generic_extra,
            'invalid_extra': self.qtd_cartas_invalid_extra,

            'arquetype_side': self.qtd_cartas_arquetype_side,
            'generic_side': self.qtd_cartas_generic_side,
            'invalid_side': self.qtd_cartas_invalid_side
        }

    def show_dados(self):
        """Mostra dados do deck como tabelas."""
        valores = self.get_dados_deck()
        return DataFrame(valores.items(), columns=['status', 'quant'])

if __name__ == '__main__':
    URL_DECK = """
    ydke://C48wAfuScQP7knEDzjaEA842hAPONoQDCHOfBAhznwQIc58Eb6yZAPqbiwP6m4sD+puLA5GVXASRlVwEkZVcBISkEQK7osEFu6LBBbuiwQUGB1kDR0WxBUdFsQVHRbEFRdxkAtWOCgDVjgoA1Y4KAIaSaADZVx8EitmnBYrZpwWK2acFxpwjA8acIwMbzoABG86AARvOgAEeC/IDHgvyAw==!l77AApuGHwGbhh8BL+9IAC/vSADOAs0Dyj9gAZ+QagBes+cCT+HsBEdMywFHTMsB0htBATrQ2AU60NgF!sskJBLLJCQSyyQkEleL6BLIyzAWyMswFsjLMBZuGHwFHTMsBI9adAiPWnQIj1p0CJNYmAh4L8gM=!
    """

    mesa_core = Mesa(URL_DECK)
    print(mesa_core.show_dados())
    print(mesa_core._cache_main)
    print(mesa_core._cache_extra)
    print(mesa_core._cache_side)
