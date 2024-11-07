#
# Python 3.11.10
#
import re
import os
import math
from typing import List, Dict, Tuple, Union, Literal
import pprint
import pandas as pd
from pandas import DataFrame
import numpy as np
from matplotlib import pyplot
from sklearn.linear_model import LinearRegression

from ydke import CoreYDKE
from card import CardGameAsync
from ban import BanSheetWeb, BanSheetWebAsync


class MesaCore(CoreYDKE):
    def __init__(self) -> None:
        super().__init__()        
        self.__CARD_GAME_ASYNC__: CardGameAsync = CardGameAsync()
        self.__BANLIST_WEB__: BanSheetWeb = BanSheetWeb()
        self.__BANLIST_ASYNC__: BanSheetWebAsync = BanSheetWebAsync()

        self.__YDKE__: str = """
            ydke://G00sAYMdMQMAJIUDACSFAwAkhQN1/84Cdf/OArLJCQSyyQkET0hwA09IcANPS
            HADQhKIAkISiAKAoDYAgKA2AICgNgDGn24B51YtAU73dQFO93UBTvd1AbIyzAWyMswFs
            jLMBSh/EAMofxADKH8QA+OwKgOxYYMEsWGDBLFhgwQRuXEAQf/
            gAKeIZwFbCb4CJ5XuACeV7gA3ujsFN7o7BQ==!6DUqAug1KgLA9KEAwPShAMD0oQBt10
            MBbddDASOQswQjkLMEI5CzBB2IkgMdiJID!7I8BAOyPAQDsjwEAgx0xAzvfTAWyyQkEM
            xh3Auos+QQ3ujsF!
        """.replace('\n', '').replace('\t', '').replace(' ', '')

        self.card_not_cadastro = None

    def download_mesa(self) -> bool:
        """
        Baixa dados do jogo de cartas e salva as informações necessárias.

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

    def read_cache_data_frame(self, arq: str) -> DataFrame:
        """
        Lê um DataFrame de um arquivo CSV armazenado em cache.

        A função busca o arquivo especificado (`arq`) no diretório
        de cache e o carrega em um DataFrame.

        Args:
            arq (str): Nome do arquivo CSV a ser lido.

        Returns:
            DataFrame: DataFrame contendo os dados lidos do arquivo.
        """
        src = os.path.dirname(__file__)
        file = os.path.join(src, 'cache', arq)
        return pd.read_csv(
            file,
            sep=';',
            encoding='utf-8'
        )

    def read_var_data_frame(self, arq: str) -> DataFrame:
        """
        Lê um DataFrame de um arquivo CSV localizado na pasta 'var'.

        A função localiza o arquivo especificado (`arq`) e o carrega em um DataFrame, utilizando o caractere '|' como separador.

        Args:
            arq (str): Nome do arquivo CSV a ser lido.

        Returns:
            DataFrame: DataFrame contendo os dados lidos do arquivo.
        """
        src = os.path.dirname(__file__)
        file = os.path.join(src, 'var', arq)
        return pd.read_csv(
            file,
            sep='|',
            encoding='utf-8'
        )

    def mount_deck(self, cat: str, array: pd.Series | list) -> DataFrame:
        """
        Monta um DataFrame do deck com detalhes de cada carta e contagem de ocorrências.

        Args:
            cat (str): Categoria do deck ('main', 'extra', 'side').
            array (pd.Series | list): Códigos das cartas.

        Returns:
            DataFrame: DataFrame com informações das cartas, incluindo contagem e categoria.
        """
        complet = self.read_cache_data_frame('complet.csv')
        complet['cod'] = complet['cod'].astype(int)
        decklist = []
        for x in array:
            filtered_df = complet.loc[complet['cod'].isin([x])]

            if not filtered_df.empty:
                decklist.append(filtered_df.values[0].tolist())
            else:
                self.card_not_cadastro = True
                print(f"Warning: No matching 'cod' found for value: {x}")

        col_patt = ['cod', 'card_name', 'tipo', 'effect', 'arquetype']
        df = pd.DataFrame(decklist, columns=col_patt)
        df['qtd_copy'] = np.ones(df.shape[0], dtype=int)
        df = df.groupby(col_patt).sum().reset_index()
        df['categoria'] = np.full(df.shape[0], cat)

        df['cod'] = df['cod'].astype(int)
        df = df.sort_values(by=['cod'])
        df = df.reset_index(drop=True)
        return df

    def read_link_deck(self, link: str) -> Tuple[DataFrame]:
        """
        Lê dados de um deck, identifica arquétipos genéricos
        e monta as seções `main`, `extra` e `side`.

        Args:
            link (str): URL do deck.

        Returns:
            Tuple[DataFrame]: DataFrames `main`, `extra` e `side` com arquétipos ajustados.
        """
        link = link.replace('\n', '').replace(' ', '').replace('\t', '')
        deck = self.read_url(link)
        mini = self.read_cache_data_frame('min.csv')
        main = self.mount_deck('main', deck['main'])
        main['arquetype'] = list(map(
            lambda x: 'generic' if x in mini['name'].to_list() else x,
            main['arquetype']
        ))
        extra = self.mount_deck('extra', deck['extra'])
        extra['arquetype'] = list(map(
            lambda x: 'generic' if x in mini['name'].to_list() else x,
            extra['arquetype']
        ))
        side = self.mount_deck('side', deck['side'])
        side['arquetype'] = list(map(
            lambda x: 'generic' if x in mini['name'].to_list() else x,
            side['arquetype']
        ))
        return main, extra, side

    def frequence_weight(self, part_deck: DataFrame) -> DataFrame:
        """
        Calcula a frequência ajustada para cada arquétipo
        e atribui uma chave absoluta ordenada.

        Agrupa os dados por arquétipo (`arquetype`), soma as cópias (`qtd_copy`)
        para obter a frequência absoluta e classifica os arquétipos da maior
        para a menor frequência, atribuindo chaves absolutas (`key_abs`). 
        Se 'generic' tiver a maior frequência, o valor é ajustado para zero.

        Args:
            part_deck (DataFrame): Contém `arquetype` e `qtd_copy`, onde `arquetype`
            representa o tipo de arquétipo e `qtd_copy` a quantidade
            de cópias de cada arquétipo.

        Returns:
            DataFrame: Atualizado com as colunas:
                - 'freq_abs': Frequência ajustada (freq_abs / 10) de cada arquétipo.
                - 'key_abs': Chave numérica absoluta, ordenada da maior para a menor frequência.
        """
        pares_abs = part_deck[
            ['arquetype', 'qtd_copy']
        ].groupby(['arquetype']).sum().reset_index()
        pares_abs.columns = ['arquetype', 'freq_abs']
        pares_abs = pares_abs.sort_values(by=['freq_abs'], ascending=False)
        
        # Cria chaves absolutas do maio ao menor
        pares_abs['key_abs'] = range(len(pares_abs), 0, -1)

        array = pares_abs['freq_abs'].isin([pares_abs['freq_abs'].max()])
        array = pares_abs['arquetype'].loc[array].to_list()

        if array[0] == 'generic':
            pares_abs.loc[pares_abs['arquetype'] == 'generic', 'freq_abs'] = 0
        
        pares_abs['freq_abs'] = pares_abs['freq_abs'] / 10
        # print(pares_abs)
        df_merge = pd.merge(part_deck, pares_abs, how='left', on='arquetype')
        return df_merge.copy()

    def sub_frequence_weight(self, part_deck: DataFrame) -> DataFrame:
        """
        Calcula a frequência ajustada de sub-arquétipos em um conjunto
        de dados e atribui pesos para cada sub-arquétipo.

        A função extrai os sub-arquétipos de `part_deck`, calcula a frequência
        de cada um, e ajusta a frequência com base em uma escala de peso.
        Além disso, configura a chave `sub_key` para cada sub-arquétipo em
        ordem decrescente de frequência e garante que o valor `sub_key`
        do arquétipo 'generic' seja zero, caso seja o mais frequente.

        Args
        ----------
        part_deck : DataFrame
            DataFrame contendo uma coluna `arquetype`
            com sub-arquétipos em formato de string.

        Returns
        -------
        DataFrame
            DataFrame atualizado com duas novas colunas:
            - 'sub_key': Chave numérica associada a cada sub-arquétipo com base na frequência.
            - 'sub_freq': Frequência ajustada para cada sub-arquétipo.
        """
        alg_freq = pd.Series('|'.join(
            part_deck.arquetype).replace(' | ', '|').split('|')
        )
        alg_freq = alg_freq.str.split(' ').explode().value_counts(
            ).reset_index(name='freq')

        alg_freq.columns = ['arquetype', 'sub_freq']
        alg_freq['sub_freq'] = alg_freq['sub_freq'] / 10
        alg_freq['sub_key'] = range(len(alg_freq), 0, -1)
        
        # zera a combinacao linear de arquetipo generico se for o maior
        array = alg_freq['sub_key'] == alg_freq['sub_key'].max()
        array = alg_freq['arquetype'].loc[array].to_list()
        if array[0] == 'generic':
            alg_freq.loc[
                alg_freq['sub_key'].isin([alg_freq['sub_key'].max()]),
                'sub_key'
            ] = 0

        key = []
        frq = []
        # procura uma palavra menor no conjunto de palavras do arquetipo
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

    def categoria_linear(self, matrix: DataFrame) -> Dict:
        """
        Realiza uma classificação linear e aplica uma regressão
        linear em uma matriz de dados específica.
        
        A função calcula uma soma linear com base em colunas específicas
        do DataFrame `matrix`, define um valor de referência (meta) e 
        classifica os dados em três grupos (-1, 0, 1).
        Em seguida, ajusta um modelo de regressão linear
        para relacionar as variáveis `key_abs` e `freq_abs`.

        Args
        ----------
        matrix : DataFrame
            DataFrame contendo as colunas
            `key_abs`, `freq_abs`, `sub_key`, `sub_freq`, e `arquetype`.\n
            Essas colunas são utilizadas para cálculos de soma e modelo linear.

        Returns
        -------
        dict
            Retorna um dicionário com as seguintes chaves:
            - `'frame'` : DataFrame
                O DataFrame atualizado, incluindo as colunas
                `soma` e `cat_meta_dado` com os valores calculados.
            - `'model'` : LinearRegression
                O modelo de regressão linear ajustado
                às variáveis `key_abs` e `freq_abs`.
            - `'x'` : numpy.ndarray
                Valores de `key_abs` usados como variável independente.
            - `'y'` : numpy.ndarray
                Valores de `freq_abs` usados como variável dependente.
            - `'predict'` : numpy.ndarray
                Valores preditos pelo modelo de regressão linear
                para os valores de `key_abs`.
        """
        # modo de peso para classificacao linear
        col_linear = ['key_abs', 'freq_abs', 'sub_key', 'sub_freq']
        matrix['soma'] = matrix[col_linear].sum(axis=1)

        meta_dado = matrix.loc[
            matrix['arquetype'].isin(['generic'])]['soma'].max()
        if math.isnan(meta_dado):
            meta_dado = matrix['soma'].mean().round()
            meta_dado = int(meta_dado)
        else:
            meta_dado = meta_dado.round(2)
    
        # categorizacao linear do arquetipo
        cat_meta_dado = []
        for i, v in enumerate(matrix['soma']):
            if v == meta_dado:
                cat_meta_dado.append(0)
            elif v < meta_dado:
                cat_meta_dado.append(-1)
            else:
                cat_meta_dado.append(1)

        matrix['cat_meta_dado'] = cat_meta_dado
        
        # estrutura de dados de algebra linear
        x = matrix['key_abs']
        y = matrix['freq_abs']
        model = LinearRegression()
        model.fit(x.values.reshape(-1, 1), y)
        pred = model.predict(x.values.reshape(-1, 1))
        return {
            'frame': matrix.copy(),
            'model': model,
            'x': x.to_numpy(),
            'y': y.to_numpy(),
            'predict' : pred
        }

    def define_arquetype(self, matrix: DataFrame) -> DataFrame:
        """
        Define archetypes for the given DataFrame based
        on specific criteria and categorizes them.

        Args:
            matrix (DataFrame): The DataFrame containing the
            data with archetype information.

        Returns:
            DataFrame: A copy of the original DataFrame with added
            columns 'y' and 'valid' indicating archetype classification.
        """
        # Filter and process archetypes
        verificador_max = matrix.loc[matrix['cat_meta_dado'] == 1]
        fim_max_ver = verificador_max.arquetype.str.replace('|',' ')
        fim_max_ver = fim_max_ver.str.split(' ').explode(
            ).value_counts().reset_index(name='freq')

        # Determine the maximum frequency archetype
        fim_max = fim_max_ver.loc[
            fim_max_ver['freq'] == fim_max_ver['freq'].max()
            ]

        if len(set(fim_max['freq'])) == 1:
            arquetypo = ' '.join(fim_max['arquetype'])
        else:
            arquetypo = fim_max.iloc[0].values[0]

        # Classify archetypes
        matrix['y'] = matrix['arquetype'].apply(
            lambda i: 1 if arquetypo in i else (
                0 if i == 'generic' else -1)
            )

        # Map classifications to valid labels
        dicio_val = {0: 'generic', 1: arquetypo, -1: 'invalid'}
        matrix['y'] = matrix['y'].apply(lambda x: dicio_val[x])

        return {
            'main': matrix.copy(),
            'arquetype': arquetypo
        }

    def construct_deck(self, url_ydke: str) -> Dict:
        """
        Constrói uma estrutura de dados com informações detalhadas sobre o deck de Yu-Gi-Oh! baseado em um link YDKe.

        A função realiza as seguintes etapas:
        - Lê os dados do deck principal (main), extra e side deck a partir do link YDKe.
        - Identifica e categoriza as cartas do deck principal pelo arquétipo, cartas genéricas e cartas inválidas.
        - Processa as quantidades de cada tipo de carta para cada seção do deck (main, extra e side).
        - Retorna um dicionário contendo os dados organizados para fácil acesso e análise.

        Parâmetros:
        ----------
        url_ydke : str
            URL do link YDKe, que fornece a estrutura do deck.

        Retorno:
        --------
        Dict
            Um dicionário com as seguintes chaves e valores:
            - `arquetype`: str, o arquétipo principal identificado no deck.
            - `qtd_card_main`: int, quantidade total de cartas no main deck.
            - `qtd_card_arquetype_main`: int, quantidade de cartas do arquétipo no main deck.
            - `qtd_card_generic_main`: int, quantidade de cartas genéricas no main deck.
            - `qtd_card_invalid_main`: int, quantidade de cartas inválidas no main deck.
            - `arquetype_invalido_main`: str, cartas de arquétipos inválidos no main deck.
            - `contain_card_invalid_main`: bool, indica se há cartas inválidas no main deck.
            
            - `qtd_card_extra`: int, quantidade total de cartas no extra deck.
            - `qtd_card_arquetype_extra`: int, quantidade de cartas do arquétipo no extra deck.
            - `qtd_card_generic_extra`: int, quantidade de cartas genéricas no extra deck.
            - `qtd_card_invalid_extra`: int, quantidade de cartas inválidas no extra deck.
            - `arquetype_invalido_extra`: str, cartas de arquétipos inválidos no extra deck.
            - `contain_card_invalid_extra`: bool, indica se há cartas inválidas no extra deck.
            
            - `qtd_card_side`: int, quantidade total de cartas no side deck.
            - `qtd_card_arquetype_side`: int, quantidade de cartas do arquétipo no side deck.
            - `qtd_card_generic_side`: int, quantidade de cartas genéricas no side deck.
            - `qtd_card_invalid_side`: int, quantidade de cartas inválidas no side deck.
            - `arquetype_invalido_side`: str, cartas de arquétipos inválidos no side deck.
            - `contain_card_invalid_side`: bool, indica se há cartas inválidas no side deck.
            
        Exemplo de uso:
        ---------------
        ```
        deck_data = mont_deck('ydke_link')
        print(deck_data['arquetype'])  # Exibe o arquétipo principal do deck
        ```

        Considerações:
        --------------
        Esta função utiliza diversas funções auxiliares da biblioteca `mesa_core`:
        - `read_link_deck`: para obter dados do main, extra e side deck.
        - `sub_frequence_weight` e `frequence_weight`: para ajuste de frequência no deck principal.
        - `categoria_linear`: para categorizar as cartas do deck.
        - `define_arquetype`: para identificar o arquétipo principal e distinguir cartas genéricas e inválidas.
        
        Observação:
        -----------
        Para um deck bem estruturado e competitivo, recomenda-se que a quantidade de cartas inválidas seja zero, garantindo a consistência do arquétipo principal.
        """
        main, extra, side = mesa_core.read_link_deck(url_ydke)
        
        # limpando main
        main = mesa_core.sub_frequence_weight(mesa_core.frequence_weight(main))
        struct_deck = mesa_core.categoria_linear(main)
        main_arq = mesa_core.define_arquetype(struct_deck['frame'])
        main = main_arq['main']
        arquetype = main_arq['arquetype']

        qtd_card_main = main['qtd_copy'].sum()

        qtd_card_arquetype_main = main.loc[
            main['y'].isin([arquetype])]['qtd_copy'].sum()

        qtd_card_generic_main = main.loc[
            main['y'].isin(['generic'])]['qtd_copy'].sum()

        qtd_card_invalid_main = main.loc[
            main['y'].isin(['invalid'])]['qtd_copy'].sum()

        arquetype_invalido_main = main['y'].loc[
            ~main['y'].isin([arquetype, 'generic'])]

        contain_card_invalid_main = arquetype_invalido_main.values.size != 0
        if not contain_card_invalid_main:
            arquetype_invalido_main = ''

        data_main = {
            'qtd_card_main': int(qtd_card_main),
            'qtd_card_arquetype_main': int(qtd_card_arquetype_main),
            'qtd_card_generic_main': int(qtd_card_generic_main),
            'qtd_card_invalid_main': int(qtd_card_invalid_main),
            'arquetype_invalido_main': (arquetype_invalido_main),
            'contain_card_invalid_main': bool(contain_card_invalid_main)
        }

        # montando extra
        extra['y'] = extra['arquetype'].apply(
            lambda a: arquetype if arquetype in a else a)

        qtd_card_extra = extra['qtd_copy'].sum()

        qtd_card_arquetype_extra = extra.loc[
            extra['y'].isin([arquetype])]['qtd_copy'].sum()

        qtd_card_generic_extra = extra.loc[
            extra['y'].isin(['generic'])]['qtd_copy'].sum()

        arquetype_invalido_extra = extra['y'].loc[
            ~extra['y'].isin([arquetype, 'generic'])]

        contain_card_invalid_extra = arquetype_invalido_extra.values.size != 0

        qtd_card_invalid_extra = extra.loc[
            extra['y'].isin([arquetype_invalido_extra])]['qtd_copy'].sum()

        if not contain_card_invalid_extra:
            arquetype_invalido_extra = ''

        data_extra = {
            'qtd_card_extra': int(qtd_card_extra),
            'qtd_card_arquetype_extra': int(qtd_card_arquetype_extra),
            'qtd_card_generic_extra': int(qtd_card_generic_extra),
            'qtd_card_invalid_extra': int(qtd_card_invalid_extra),
            'arquetype_invalido_extra': arquetype_invalido_extra,
            'contain_card_invalid_extra': bool(contain_card_invalid_extra)
        }

        # montando side
        side['y'] = side['arquetype'].apply(
            lambda a: arquetype if arquetype in a else a)

        qtd_card_side = side['qtd_copy'].sum()

        qtd_card_arquetype_side = side.loc[
            side['y'].isin([arquetype])]['qtd_copy'].sum()

        qtd_card_generic_side = side.loc[
            side['y'].isin(['generic'])]['qtd_copy'].sum()

        arquetype_invalido_side = side['y'].loc[
            ~side['y'].isin([arquetype, 'generic'])]

        contain_card_invalid_side = arquetype_invalido_side.values.size != 0

        qtd_card_invalid_side = side.loc[
            side['y'].isin([arquetype_invalido_side])]['qtd_copy'].sum()

        if not contain_card_invalid_side:
            arquetype_invalido_side = ''

        data_side = {
            'qtd_card_side': int(qtd_card_side),
            'qtd_card_arquetype_side': int(qtd_card_arquetype_side),
            'qtd_card_generic_side': int(qtd_card_generic_side),
            'qtd_card_invalid_side': int(qtd_card_invalid_side),
            'arquetype_invalido_side': arquetype_invalido_side,
            'contain_card_invalid_side': bool(contain_card_invalid_side)
        }
        
        dados = {
            'arquetype': arquetype,
        }
        dados = dados | data_main | data_extra | data_side
        return dados

# class MasterMesa(MesaCore):


if __name__ == '__main__':
    mesa_core = MesaCore()
    LINK_YDKE: str = """
    ydke://G00sAcSMVgPEjFYDxIxWA4MdMQMAJIUDACSFAwAkhQN1/84Cdf/OArLJCQSyyQkET0hwA09IcANPSHADQhKIAkISiAKAoDYAgKA2AICgNgDGn24B51YtAU73dQFO93UBTvd1ASh/EAMofxADKH8QA+OwKgOxYYMEsWGDBLFhgwQRuXEAQf/gAKeIZwFbCb4CJ5XuACeV7gA3ujsFN7o7BQ==!6DUqAug1KgLA9KEAwPShAMD0oQAo29AE2NxoAW3XQwFt10MB0htBASOQswQjkLMEI5CzBB2IkgMdiJID!7I8BAOyPAQDsjwEAsskJBLIyzAWyMswFsjLMBaab9AEzGHcC6iz5BBLZoAIS2aACo2rUAqNq1AI3ujsF!
    """

    dados = mesa_core.construct_deck(LINK_YDKE)
    pprint.pprint(dados)
