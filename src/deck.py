#
# Python ^3.11
#

import pprint
from os import PathLike
from typing import (
    List,
    Union,
    Dict
)

import pandas as pd                                # type: ignore
from numpy import ndarray                          # type: ignore
from pandas import DataFrame                       # type: ignore

from mesa import Combination


class FrameDeck(Combination):
    def __init__(self, deck_list: Union[str, PathLike]) -> None:
        super().__init__(deck_list)
        # Cache de criptografia do deck, independente a arquivos passados como argumento
        self._cache_ydke: Union[None, str] = None

        # Cache para numeros já cálculados
        self._cache_full_main: Union[None, int] = None
        self._cache_full_extra: Union[None, int] = None
        self._cache_full_side: Union[None, int] = None
        self._cache_full_cards: Union[None, int] = None

        # Garante que arquetype no main deck original seja o nosso Y correto
        self._cache_number_cards_arquetype_main: Union[None, int] = None
        self._cache_number_cards_generic_main: Union[None, int] = None
        self._cache_number_cards_invalid_main: Union[None, int] = None

        # Garante que arquetype no extra deck original seja o nosso Y correto
        self._cache_number_cards_arquetype_extra: Union[None, int] = None
        self._cache_number_cards_generic_extra: Union[None, int] = None
        self._cache_number_cards_invalid_extra: Union[None, int] = None

        # Garante que arquetype no side deck original seja o nosso Y correto
        self._cache_number_cards_arquetype_side: Union[None, int] = None
        self._cache_number_cards_generic_side: Union[None, int] = None
        self._cache_number_cards_invalid_side: Union[None, int] = None

        # Caches de relacionamento full
        self._cache_full_arquetype: Union[None, int] = None
        self._cache_full_generic: Union[None, int] = None
        self._cache_full_invalid: Union[None, int] = None

        # Caches para quantidades detalhadas do deck
        self._cache_number_monster_main: Union[None, int] = None
        self._cache_number_monster_arquetype_main: Union[None, int] = None
        self._cache_number_monster_generic_main: Union[None, int] = None

        self._cache_number_spell_main: Union[None, int] = None
        self._cache_number_spell_arquetype_main: Union[None, int] = None
        self._cache_number_spell_generic_main: Union[None, int] = None

        self._cache_number_trap_main: Union[None, int] = None
        self._cache_number_trap_arquetype_main: Union[None, int] = None
        self._cache_number_trap_generic_main: Union[None, int] = None

        # Caches para banlist
        self._cache_number_cards_banlist: Union[None, int] = None
        self._cache_number_cards_banlist_main: Union[None, int] = None
        self._cache_number_cards_banlist_extra: Union[None, int] = None
        self._cache_number_cards_banlist_side: Union[None, int] = None

        self._cache_number_cards_invalid_banlist: Union[None, int] = None
        self._cache_cods: Union[None, List[int]] = None
        self._cache_conditions: Union[None, List[int]] = None

        # Cache da estrutura de dados do deck
        self._cache_strutura_deck: Union[None, dict] = None

    def decklist(self) -> DataFrame:
        """Retorna a deck-list completa, com main, extra e side."""
        return pd.concat([
            self.main,
            self.extra,
            self.side
        ], axis=0).reset_index(drop=True)

    @property
    def full_cards_main(self) -> int:
        """Retorna o número total de cartas do main deck."""
        if self._cache_full_main is None:
            self._cache_full_main = int(self.main['qtd_copy'].sum(axis=0))
        return self._cache_full_main

    @property
    def full_cards_extra(self) -> int:
        """Retorna o número total de cartas do extra deck."""
        if self._cache_full_extra is None:
            self._cache_full_extra = int(self.extra['qtd_copy'].sum(axis=0))
        return self._cache_full_extra

    @property
    def full_cards_side(self) -> int:
        """Retorna o total de cartas do side deck."""
        if self._cache_full_side is None:
            self._cache_full_side = int(self.side['qtd_copy'].sum(axis=0))
        return self._cache_full_side

    @property
    def full_cards_arquetype(self) -> int:
        """Retorna o total de cartas do arquétipo em todo o deck."""
        if self._cache_full_arquetype is None:
            self._cache_full_arquetype = self.number_cards_arquetype_main + \
                                            self.number_cards_arquetype_extra + \
                                                self.number_cards_arquetype_side
        return self._cache_full_arquetype

    @property
    def full_cards_generic(self) -> int:
        """Retorna o total de cartas genericas em todo o deck."""
        if self._cache_full_generic is None:
            self._cache_full_generic = self.number_cards_generic_main + \
                                            self.number_cards_generic_extra + \
                                                self.number_cards_generic_side
        return self._cache_full_generic

    @property
    def full_cards_invalid(self) -> int:
        """Retorna o total de cartas invalidas em todo o deck."""
        if self._cache_full_invalid is None:
            self._cache_full_invalid = self.number_cards_invalid_main + \
                                            self.number_cards_invalid_extra + \
                                                self.number_cards_invalid_side
        return self._cache_full_invalid

    @property
    def full_cards_deck(self) -> int:
        """Retorna o número total de cartas do deck."""
        if self._cache_full_cards is None:
            self._cache_full_cards = self.full_cards_main + \
                                            self.full_cards_extra + \
                                                self.full_cards_side
        return self._cache_full_cards

    @property
    def number_cards_arquetype_main(self) -> int:
        """Retorna o número total de cartas do arquetipo no main deck."""
        if self._cache_number_cards_arquetype_main is None:
            if self.arquetype == 'generic':
                self._cache_number_cards_arquetype_main = 0
            else:
                self._cache_number_cards_arquetype_main = int(
                    self.main.loc[
                        self.main['arquetype'] == self.arquetype
                    ]['qtd_copy'].sum(axis=0)
                )
        return self._cache_number_cards_arquetype_main

    @property
    def number_cards_generic_main(self) -> int:
        """Retorna o número total de cartas genericas no main deck."""
        if self._cache_number_cards_generic_main is None:
            self._cache_number_cards_generic_main = int(
                self.main.loc[
                    self.main['arquetype'] == 'generic'
                ]['qtd_copy'].sum(axis=0)
            )
        return self._cache_number_cards_generic_main

    @property
    def number_cards_invalid_main(self) -> int:
        """Retorna o número total de cartas invalidas no main deck."""
        if self._cache_number_cards_invalid_main is None:
            self._cache_number_cards_invalid_main = int(
                self.main.loc[
                    self.main['arquetype'] == 'invalid'
                ]['qtd_copy'].sum(axis=0)
            )
        return self._cache_number_cards_invalid_main

    @property
    def number_cards_arquetype_extra(self) -> int:
        """Retorna o número total de cartas do arquetipo no extra deck."""
        if self._cache_number_cards_arquetype_extra is None:
            if self.arquetype == 'generic':
                self._cache_number_cards_arquetype_extra = 0
            else:
                self._cache_number_cards_arquetype_extra = int(
                    self.extra.loc[
                        self.extra['arquetype'] == self.arquetype
                    ]['qtd_copy'].sum(axis=0)
                )
        return self._cache_number_cards_arquetype_extra

    @property
    def number_cards_generic_extra(self) -> int:
        """Retorna o número total de cartas genericas no extra deck."""
        if self._cache_number_cards_generic_extra is None:
            self._cache_number_cards_generic_extra = int(
                self.extra.loc[
                    self.extra['arquetype'] == 'generic'
                ]['qtd_copy'].sum(axis=0)
            )
        return self._cache_number_cards_generic_extra

    @property
    def number_cards_invalid_extra(self) -> int:
        """Retorna o número total de cartas invalidas no extra deck."""
        if self._cache_number_cards_invalid_extra is None:
            self._cache_number_cards_invalid_extra = int(
                self.extra.loc[
                    self.extra['arquetype'] == 'invalid'
                ]['qtd_copy'].sum(axis=0)
            )
        return self._cache_number_cards_invalid_extra

    @property
    def number_cards_arquetype_side(self) -> int:
        """Retorna o número total de cartas do arquetipo no side deck."""
        if self._cache_number_cards_arquetype_side is None:
            if self.arquetype == 'generic':
                self._cache_number_cards_arquetype_side = 0
            else:
                self._cache_number_cards_arquetype_side = int(
                    self.side.loc[
                        self.side['arquetype'] == self.arquetype
                    ]['qtd_copy'].sum(axis=0)
                )
        return self._cache_number_cards_arquetype_side

    @property
    def number_cards_generic_side(self) -> int:
        """Retorna o número total de cartas genericas no side deck."""
        if self._cache_number_cards_generic_side is None:
            self._cache_number_cards_generic_side = int(
                self.side.loc[
                    self.side['arquetype'] == 'generic'
                ]['qtd_copy'].sum(axis=0)
            )
        return self._cache_number_cards_generic_side

    @property
    def number_cards_invalid_side(self) -> int:
        """Retorna o número total de cartas invalidas no side deck."""
        if self._cache_number_cards_invalid_side is None:
            self._cache_number_cards_invalid_side = int(
                self.side.loc[
                    self.side['arquetype'] == 'invalid'
                ]['qtd_copy'].sum(axis=0)
            )
        return self._cache_number_cards_invalid_side

    @property
    def number_monster_main(self) -> int:
        """Retorna o número de monstros no main deck pela quantidade de copias."""
        if self._cache_number_monster_main is None:
            self._cache_number_monster_main = int(
                self.main.loc[
                    self.main['tipo'].apply(lambda x: 'Monster' in x)
                ]['qtd_copy'].sum(axis=0)
            )
        return self._cache_number_monster_main

    @property
    def number_monster_arquetype_main(self) -> int:
        """Retorna o número de monstros do arquetipo no main deck pela quantidade de copias."""
        if self._cache_number_monster_arquetype_main is None:
            if self.arquetype == 'generic':
                self._cache_number_monster_arquetype_main = 0
            else:
                self._cache_number_monster_arquetype_main = int(
                    self.main.loc[
                        (self.main['tipo'].apply(lambda x: 'Monster' in x)) &
                        (self.main['arquetype'].isin([self.arquetype]))
                    ]['qtd_copy'].sum(axis=0)
                )
        return self._cache_number_monster_arquetype_main

    @property
    def number_monster_generic_main(self) -> int:
        """Retorna o número de monstros genericos do main deck pela quantidade de copias."""
        if self._cache_number_monster_generic_main is None:
            self._cache_number_monster_generic_main = int(
                self.main.loc[
                    (self.main['tipo'].apply(lambda x: 'Monster' in x)) &
                    (self.main['arquetype'].isin(['generic']))
                ]['qtd_copy'].sum(axis=0)
            )
        return self._cache_number_monster_generic_main

    @property
    def number_spell_main(self) -> int:
        """Retorna o número de cartas magicas do main deck."""
        if self._cache_number_spell_main is None:
            self._cache_number_spell_main = int(
                self.main.loc[
                    self.main['tipo'] == 'Spell'
                ]['qtd_copy'].sum(axis=0)
            )
        return self._cache_number_spell_main

    @property
    def number_spell_arquetype_main(self) -> int:
        """Retorna o número de cartas magicas do arquetipo no main deck."""
        if self._cache_number_spell_arquetype_main is None:
            if self.arquetype == 'generic':
                self._cache_number_spell_arquetype_main = 0
            else:
                self._cache_number_spell_arquetype_main = int(
                    self.main.loc[
                        (self.main['tipo'] == 'Spell') &
                        (self.main['arquetype'].isin([self.arquetype]))
                    ]['qtd_copy'].sum(axis=0)
                )
        return self._cache_number_spell_arquetype_main

    @property
    def number_spell_generic_main(self) -> int:
        """Retorna o número de cartas magicas genericas do main deck."""
        if self._cache_number_spell_generic_main is None:
            self._cache_number_spell_generic_main = int(
                self.main.loc[
                    (self.main['tipo'] == 'Spell') &
                    (self.main['arquetype'].isin(['generic']))
                ]['qtd_copy'].sum(axis=0)
            )
        return self._cache_number_spell_generic_main

    @property
    def number_trap_main(self) -> int:
        """Retorna o número de cartas de armadilha do main deck."""
        if self._cache_number_trap_main is None:
            self._cache_number_trap_main = int(
                self.main.loc[
                    self.main['tipo'] == 'Trap'
                ]['qtd_copy'].sum(axis=0)
            )
        return self._cache_number_trap_main

    @property
    def number_trap_arquetype_main(self) -> int:
        """Retorna o número de cartas de armadilha do arquetipo no main deck."""
        if self._cache_number_trap_arquetype_main is None:
            if self.arquetype == 'generic':
                self._cache_number_trap_arquetype_main = 0
            else:
                self._cache_number_trap_arquetype_main = int(
                    self.main.loc[
                        (self.main['tipo'] == 'Trap') &
                        (self.main['arquetype'].isin([self.arquetype]))
                    ]['qtd_copy'].sum(axis=0)
                )
        return self._cache_number_trap_arquetype_main

    @property
    def number_trap_generic_main(self) -> int:
        """Retorna o número de cartas de armadilha genericas do main deck."""
        if self._cache_number_trap_generic_main is None:
            self._cache_number_trap_generic_main = int(
                self.main.loc[
                    (self.main['tipo'] == 'Trap') &
                    (self.main['arquetype'].isin(['generic']))
                ]['qtd_copy'].sum(axis=0)
            )
        return self._cache_number_trap_generic_main

    def cards_invalids_banlist(self) -> DataFrame:
        """Retorna o frame de cartas invalidas da banlist."""
        cache = self.decklist()
        return cache.loc[~(cache['qtd_copy'] <= cache['condition'])].reset_index(drop=True)

    def cards_invalids_banlist_dict(self) -> Dict:
        """Retornas as cards invalids do deck em relação a banlist em dicionário."""
        return self.cards_invalids_banlist().to_dict(orient='list')

    @property
    def number_cards_banlist(self) -> int:
        """Retorna o número de cartas na banlist inseridas na deck-list."""
        if self._cache_number_cards_banlist is None:
            cache = self.decklist()
            cod_banlist = self.BANLIST['cod'].astype(int).unique()
            cards_na_lista = cache.loc[cache['cod'].isin(cod_banlist)]
            self._cache_number_cards_banlist = int(cards_na_lista['qtd_copy'].sum(axis=0))
        return self._cache_number_cards_banlist

    @property
    def number_cards_banlist_main(self) -> int:
        """Retorna o número de cartas na banlist, apenas no main deck."""
        if self._cache_number_cards_banlist_main is None:
            cache = self.main.copy()
            cod_banlist = self.BANLIST['cod'].astype(int).unique()
            cards_na_lista = cache.loc[cache['cod'].isin(cod_banlist)]
            self._cache_number_cards_banlist_main = int(cards_na_lista['qtd_copy'].sum(axis=0))
        return self._cache_number_cards_banlist_main

    @property
    def number_cards_banlist_extra(self) -> int:
        """Retorna o número de cartas na banlist, apenas no extra deck."""
        if self._cache_number_cards_banlist_extra is None:
            cache = self.extra.copy()
            cod_banlist = self.BANLIST['cod'].astype(int).unique()
            cards_na_lista = cache.loc[cache['cod'].isin(cod_banlist)]
            self._cache_number_cards_banlist_extra = int(cards_na_lista['qtd_copy'].sum(axis=0))
        return self._cache_number_cards_banlist_extra

    @property
    def number_cards_banlist_side(self) -> int:
        """Retorna o número de cartas na banlist, apenas no side deck."""
        if self._cache_number_cards_banlist_side is None:
            cache = self.side.copy()
            cod_banlist = self.BANLIST['cod'].astype(int).unique()
            cards_na_lista = cache.loc[cache['cod'].isin(cod_banlist)]
            self._cache_number_cards_banlist_side = int(cards_na_lista['qtd_copy'].sum(axis=0))
        return self._cache_number_cards_banlist_side

    @property
    def number_cards_invalid_banlist(self) -> int:
        """Retorna o número de cartas que estão invalidadas pela banlist no deck."""
        if self._cache_number_cards_invalid_banlist is None:
            self._cache_number_cards_invalid_banlist = self.cards_invalids_banlist().shape[0]
        return self._cache_number_cards_invalid_banlist

    def cards_banlist_no_deck(self) -> Dict[str, List]:
        """Retorna um dicionário com a lista dos códigos, quantidade de copias e condicoes de copias no deck."""
        cache = self.decklist()
        cache = cache.loc[cache['cod'].isin(self.VETOR_COD_BANLIST)]
        cache = cache.groupby('cod', as_index=False).agg({
            'qtd_copy': 'sum',
            'condition': 'first'
        })
        return cache.to_dict(orient='list')

    @property
    def cod_cards_banlist_no_deck(self) -> List[int]:
        """Retorna os códigos das cartas que estão na banlist incluidas no deck."""
        if self._cache_cods is None:
            self._cache_cods = self.cards_banlist_no_deck()['cod']
        return self._cache_cods

    @property
    def vetor_condition_cards_banlist(self) -> List[int]:
        """Retorna em cada index o valor correspondente a copias permitidas por cópia em relação ao código."""
        if self._cache_conditions is None:
            self._cache_conditions = self.cards_banlist_no_deck()['condition']
        return self._cache_conditions

    def cards_invalids(self) -> DataFrame:
        """Analisa todo o deck em busca de cartas invalidas por arquétipo."""
        deck_completo = self.decklist()
        return deck_completo.loc[deck_completo['arquetype'] == 'invalid'].reset_index(drop=True)

    def cards_invalids_dict(self) -> Dict:
        """Retorna todas as cartas invalidas do arquétipo como dicionário."""
        return self.cards_invalids().to_dict(orient='list')

    def get_deck(self) -> Dict:
        """Retorna o dicionario do deck, sendo o dicionário códido das cartas."""
        return self.read_url(self.YDKE)

    def get_dict_deck(self) -> Dict:
        """
        Retorna todos os dados da deck-list como dicionário.
        
        Returns:
            Dict:
                - arquetype (str)
                - ydke (str)
                - decklist (Dict)
                - full_cards (Dict)
                - number_copy_cards (Dict)
                - cards_invalids (Dict)
                - cards_banlist_no_deck (Dict)
        """
        if self._cache_strutura_deck is None:
            self._cache_strutura_deck = {
                'arquetype': self.arquetype,
                'ydke': self.YDKE,
                'decklist': self.read_url(self.YDKE),
                'full_cards': {
                    'deck': self.full_cards_deck,
                    'main': self.full_cards_main,
                    'extra': self.full_cards_extra,
                    'side': self.full_cards_side,

                    'arquetype': self.full_cards_arquetype,
                    'generic': self.full_cards_generic,
                    'arquetypes_invalidos': self.full_cards_invalid
                },

                'number_copy_cards': {
                    'monster_main': self.number_monster_main,
                    'monster_arquetype_main': self.number_monster_arquetype_main,
                    'monster_generic_main': self.number_monster_generic_main,

                    'spell_main': self.number_spell_main,
                    'spell_arquetype_main': self.number_spell_arquetype_main,
                    'spell_generic_main': self.number_spell_generic_main,

                    'trap_main': self.number_trap_main,
                    'trap_arquetype_main': self.number_trap_arquetype_main,
                    'trap_generic_main': self.number_trap_generic_main,

                    'arquetype_main': self.number_cards_arquetype_main,
                    'generic_main': self.number_cards_generic_main,
                    'invalids_main': self.number_cards_invalid_main,

                    'arquetype_extra': self.number_cards_arquetype_extra,
                    'generic_extra': self.number_cards_generic_extra,
                    'invalids_extra': self.number_cards_invalid_extra,

                    'arquetype_side': self.number_cards_arquetype_side,
                    'generic_side': self.number_cards_generic_side,
                    'invalids_side': self.number_cards_invalid_side,

                    'banlist': self.number_cards_banlist,
                    'banlist_main': self.number_cards_banlist_main,
                    'banlist_extra': self.number_cards_banlist_extra,
                    'banlist_side': self.number_cards_banlist_side
                },

                'cards_invalids': {
                    'cod_arquetype': self.cards_invalids_dict()['cod'],
                    'cod_banlist': self.cards_invalids_banlist_dict()['cod']
                },

                'cards_banlist_no_deck': {
                    'cod_condition': list(map(
                        lambda a, b: str(a) + ':' + str(b),
                        self.cod_cards_banlist_no_deck,
                        self.vetor_condition_cards_banlist
                    ))
                }
            }
        return self._cache_strutura_deck

    def get_dict_card(self, cod: int) -> Dict:
        """Retorna um dicionário com os dados da carta na deck-list."""
        frame = self.decklist()
        return frame.loc[frame['cod'].isin([cod])].to_dict(orient='records')[0]

    def show_dados(self) -> None:
        """Mostra todas as estruturas de dados do deck como tabelas."""
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        print(DataFrame(self.get_dict_deck().items(), columns=['status', 'quant']))

if __name__ == '__main__':
    URL_DECK = """
    ydke://Tk8mBZbF4gOWxeIDlsXiA8GnQAXBp0AFwadABX8x+QJ/MfkCfzH5AqTz0wBrMXACeHPdAHhz3QB4c90A5XdoAeV3aAHld2gB3VExBU73dQFO93UBsjLMBbIyzAWyMswF47AqA/4KgATV9tYA1fbWAHtkHQJ7ZB0CrmAJBFhkfwSNVlcBjVZXAY1WVwHzVbAA81WwAPNVsAAxMnIDInLNAQ==!O39gA3zSJwR80icE4HAkBeBwJAXxZd0C8WXdAtZ2wQCfkGoAMqpZAZuSugWbkroFOGOBAzhjgQM4Y4ED!YofGAk5PJgXhWJ0DPCOgBSTeVwAk3lcAJN5XAIQlfgCEJX4AhCV+APkyxQAh7i0DIe4tAyHuLQOD1/EF!
    """

    core_deck = FrameDeck(URL_DECK)
    dados = core_deck.get_dict_deck()
    pprint.pprint(dados)
