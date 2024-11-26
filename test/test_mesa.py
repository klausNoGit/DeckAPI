#
# Python 3.11.10
#
# Pytest 8.3.3
#
import os
import pytest

from numpy import ndarray
from pandas import DataFrame
from src.mesa import MesaCore, Combination

LINK = """ydke://ZgEeAGYBHgA8Vk4FPFZOBQckdALEO0cFxDtHBbLJCQSyyQkEkFaQAZBWkAGQVpAB3ADiAdwA4gHJPTIDyT0yA2KA1ATj1qQA49akAOPWpABO93UBTvd1AbIyzAWyMswFPkiiAT5IogE+SKIB47AqAybrAATV9tYA1fbWAA31DAEN9QwBDfUMAd8WLwPfFi8D3xYvA8/v0ATP79AEz+/QBA==!Ebm4BWHRwQHNW4wFzVuMBc1bjAXADkkCiVRyAaSaKwAAuQgEALkIBAC5CAT5UX8Ei0cbA6KjRATbI+sD!7I8BAOyPAQDsjwEAsskJBE73dQGyMswF7ydRAO8nUQDV9tYAI9adAiPWnQJoTEQDIe4tAyHuLQMh7i0D!
"""

FILE_TRUE  = os.path.dirname(__file__).replace('test', 'decks/_deck_false.txt')
FILE_FALSE = os.path.dirname(__file__).replace('test', 'decks/_deck_false.txt')

@pytest.fixture()
def mesa():
    return MesaCore()

def comb(data):
    return Combination(data)

def test_read_cache(mesa):
    df = mesa.read_cache('complet.csv')
    assert isinstance(df, DataFrame) is True, \
        "Dados de complet.csv não montados!"
    df = mesa.read_cache('min.csv')
    assert isinstance(df, DataFrame) is True, \
        "Dados de min.csv não montados!"
    df = mesa.read_cache('monster.csv')
    assert isinstance(df, DataFrame) is True, \
        "Dados de monster.csv não montados!"
    df = mesa.read_cache('spell.csv')
    assert isinstance(df, DataFrame) is True, \
        "Dados de spell.csv não montados!"
    df = mesa.read_cache('trap.csv')
    assert isinstance(df, DataFrame) is True, \
        "Dados de trap.csv não montados!"

def test_read_var(mesa):
    df = mesa.read_var('Forbidden.csv')
    assert isinstance(df, DataFrame) is True, \
        "Dados de Forbidden.csv não montados!"
    df = mesa.read_var('Home.csv')
    assert isinstance(df, DataFrame) is True, \
        "Dados de Home.csv não montados!"
    df = mesa.read_var('Limited.csv')
    assert isinstance(df, DataFrame) is True, \
        "Dados de Limited.csv não montados!"
    df = mesa.read_var('Semi-limited.csv')
    assert isinstance(df, DataFrame) is True, \
        "Dados de Semi-limited.csv não montados!"
    df = mesa.read_var('Unlimited.csv')
    assert isinstance(df, DataFrame) is True, \
        "Dados de Unlimited.csv não montados!"

def test_monta_parte_deck(mesa):
    deck_bits = mesa.read_url(LINK)
    main = deck_bits['main']
    extra = deck_bits['extra']
    side = deck_bits['side']
    
    df = mesa.monta_parte_deck('main', main)
    assert isinstance(df, DataFrame) is True, "Main deck não Montado"
    df = mesa.monta_parte_deck('extra', extra)
    assert isinstance(df, DataFrame) is True, "Extra deck não Montado"
    df = mesa.monta_parte_deck('side', side)
    assert isinstance(df, DataFrame) is True, "Side deck não Montado"

def test_read_link_deck_ydke(mesa):
    dados = mesa.read_link_deck_ydke(LINK)
    assert isinstance(dados, tuple), "É uma tupla"
    assert len(dados) == 3, "Não é 3"
    main, extra, side = dados
    assert isinstance(main, DataFrame) is True, "Não é um DataFrame"
    assert isinstance(extra, DataFrame) is True, "Não é um DataFrame"
    assert isinstance(side, DataFrame) is True, "Não é um DataFrame"

def test_banlist_reornado(mesa):
    assert isinstance(mesa.BANLIST, DataFrame) is True, "Nao é um DataFrame"


# Combination possui atributos uteis, gerado pelas funções internas
# esse atributos serão testados na função abaixo
# ele se trata exclusivamente sobre a algebra relacional da montagem
# de uma combinação linear para arquetipo de acordo com o formato
# do Mochila Champions 2.0

def test_class_combination_file_false():
    try:
        estrutura = comb(FILE_TRUE)
        tipo = "Tipo de dado incorreto"
        assert isinstance(estrutura.BANLIST, DataFrame) is True, tipo
        assert isinstance(estrutura.arquetipo, str) is True, tipo
        assert isinstance(estrutura.YDKE, str) is True, tipo

        assert isinstance(estrutura.main, DataFrame) is True, tipo
        assert isinstance(estrutura.extra, DataFrame) is True, tipo
        assert isinstance(estrutura.side, DataFrame) is True, tipo

        assert isinstance(estrutura.linear_main, DataFrame) is True, tipo
        assert isinstance(estrutura.linear_extra, ndarray) is True, tipo
        assert isinstance(estrutura.linear_side, ndarray) is True, tipo

        estrutura = comb(LINK)
        assert isinstance(estrutura.BANLIST, DataFrame) is True, tipo
        assert isinstance(estrutura.arquetipo, str) is True, tipo
        assert isinstance(estrutura.YDKE, str) is True, tipo

        assert isinstance(estrutura.main, DataFrame) is True, tipo
        assert isinstance(estrutura.extra, DataFrame) is True, tipo
        assert isinstance(estrutura.side, DataFrame) is True, tipo

        assert isinstance(estrutura.linear_main, DataFrame) is True, tipo
        assert isinstance(estrutura.linear_extra, ndarray) is True, tipo
        assert isinstance(estrutura.linear_side, ndarray) is True, tipo

        estrutura = comb(FILE_FALSE) # deve falhar
    except Exception as e:
        assert 'Parameter invalid : ' in str(e), "Mensagem de error incorreta"
        assert FILE_FALSE in str(e), "O path não está presente"
