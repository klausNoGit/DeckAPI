#
# Python ^3.11
#

from os import PathLike
from typing import (
    Union,
    Literal,
    Dict
)

import numpy as np                  # type: ignore
import pandas as pd                 # type: ignore
from pandas import DataFrame        # type: ignore

from mesa import Combination


class FrameDeck(Combination):
    def __init__(self, deck_list: Union[str, PathLike]) -> None:
        super().__init__(deck_list)
        # Cache de criptografia do deck, independente a arquivos passados como argumento
        self._cache_ydke: Union[None, str] = None

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

        # Caches de relacionamento total
        self._cache_total_arquetipo: Union[None, int] = None
        self._cache_total_generic: Union[None, int] = None
        self._cache_total_invalid: Union[None, int] = None

    @property
    def ydke(self) -> str:
        """Retorna a criptografica do deck."""
        if self._cache_ydke is None:
            main = np.repeat(
                self._cache_main['cod'], self._cache_main['qtd_copy']
            ).tolist()

            extra = np.repeat(
                self._cache_extra['cod'], self._cache_extra['qtd_copy']
            ).tolist()

            side = np.repeat(
                self._cache_side['cod'], self._cache_side['qtd_copy']
            ).tolist()

            self._cache_ydke = self.to_url({
                'main': main,
                'extra': extra,
                'side': side
            })
        return self._cache_ydke

    def cache_main(self) -> DataFrame:
        """Retorna o frame do main deck mais atualizado em cache."""
        return self._cache_main

    def cache_extra(self) -> DataFrame:
        """Retorna o frame do extra deck mais atualizado em cache."""
        return self._cache_extra

    def cache_side(self) -> DataFrame:
        """Retorna o frame do side deck mais atualizado em cache."""
        return self._cache_side

    def decklist(self) -> DataFrame:
        """Retorna a deck-list completa, com main, extra e side."""
        return pd.concat([self._cache_main, self._cache_extra, self._cache_side], axis=0)

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
    def total_cartas_arquetipo(self) -> int:
        """Retorna o total de cartas do arquétipo em todo o deck."""
        if self._cache_total_arquetipo is None:
            self._cache_total_arquetipo = self.qtd_cartas_arquetype_main + \
                                            self.qtd_cartas_arquetype_extra + \
                                                self.qtd_cartas_arquetype_side
        return self._cache_total_arquetipo

    @property
    def total_cartas_generic(self) -> int:
        """Retorna o total de cartas genericas em todo o deck."""
        if self._cache_total_generic is None:
            self._cache_total_generic = self.qtd_cartas_generic_main + \
                                            self.qtd_cartas_generic_extra + \
                                                self.qtd_cartas_generic_side
        return self._cache_total_generic

    @property
    def total_cartas_invalid(self) -> int:
        """Retorna o total de cartas invalidas em todo o deck."""
        if self._cache_total_invalid is None:
            self._cache_total_invalid = self.qtd_cartas_invalid_main + \
                                            self.qtd_cartas_invalid_extra + \
                                                self.qtd_cartas_invalid_side
        return self._cache_total_invalid

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

    def cartas_invalidas(self) -> DataFrame:
        """Analisa todo o deck em busca de cartas invalidas por arquétipo."""
        deck_completo = self.decklist()
        return deck_completo.loc[deck_completo['arquetype'] == 'invalid'].reset_index(drop=True)

    def cartas_invalidas_dict(self) -> Dict:
        """Retorna todas as cartas invalidas do arquétipo como dicionário."""
        return self.cartas_invalidas().to_dict(orient='list')

    def get_dados_deck(self) -> Dict:
        """Pega todos os dados quantitativos do deck."""
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

    def show_dados(self) -> None:
        """Mostra todas as estruturas de dados do deck como tabelas."""
        print(DataFrame(self.get_dados_deck().items(), columns=['status', 'quant']))

if __name__ == '__main__':
    URL_DECK = """
    ydke://+RBYBPkQWARmAR4AZgEeADxWTgU8Vk4FByR0AsQ7RwXEO0cFsskJBLLJCQSQVpABkFaQAZBWkAHcAOIB3ADiAck9MgPJPTIDYoDUBOPWpADj1qQA49akAE73dQFO93UBsjLMBbIyzAU+SKIBPkiiAT5IogHjsCoDJusABNX21gDV9tYAI9adAiPWnQLfFi8D3xYvA8/v0ATP79AEz+/QBA==!Ebm4BWHRwQHNW4wFzVuMBc1bjAXADkkCiVRyAaSaKwAAuQgEALkIBAC5CAT5UX8Ei0cbA6KjRATbI+sD!sskJBE73dQGyMswF2FMgAdhTIAHV9tYAI9adAmhMRAPfFi8DZJ/NBGSfzQRkn80EIe4tAyHuLQMh7i0D!
    """

    core_deck = FrameDeck(URL_DECK)
    core_deck.show_dados()