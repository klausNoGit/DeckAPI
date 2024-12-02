#
# Python 3.11.10
#
# Pytest 8.3.3
#
import os
import pytest
from pandas import DataFrame
from src.deck import FrameDeck

LINK = """
ydke://ZgEeAGYBHgA8Vk4FPFZOBQckdALEO0cFxDtHBbLJCQSyyQkEkFaQAZBWkAGQVpAB3ADiAdwA4gHJPTIDyT0yA2KA1ATj1qQA49akAOPWpABO93UBTvd1AbIyzAWyMswFPkiiAT5IogE+SKIB47AqAybrAATV9tYA1fbWAA31DAEN9QwBDfUMAd8WLwPfFi8D3xYvA8/v0ATP79AEz+/QBA==!Ebm4BWHRwQHNW4wFzVuMBc1bjAXADkkCiVRyAaSaKwAAuQgEALkIBAC5CAT5UX8Ei0cbA6KjRATbI+sD!7I8BAOyPAQDsjwEAsskJBE73dQGyMswF7ydRAO8nUQDV9tYAI9adAiPWnQJoTEQDIe4tAyHuLQMh7i0D!
"""

def frame(dados) -> FrameDeck:
    return FrameDeck(dados)

def test_caches_deck():
    frame_deck = frame(LINK)
    main  = frame_deck.main.copy()
    extra = frame_deck.extra.copy()
    side  = frame_deck.side.copy()

    assert isinstance(main, DataFrame), "Tipo de dado alterado"
    assert isinstance(extra, DataFrame), "Tipo de dado alterado"
    assert isinstance(side, DataFrame), "Tipo de dado alterado"

    deck = frame_deck.decklist()
    assert isinstance(deck, DataFrame), "Tipo de dado alterado"

def test_full_cards():
    frame_deck = frame(LINK)
    assert isinstance(frame_deck.full_cards_main, int), None
    assert frame_deck._cache_full_main != None, type(None)

    assert isinstance(frame_deck.full_cards_extra, int), None
    assert frame_deck._cache_full_extra != None, type(None)

    assert isinstance(frame_deck.full_cards_side, int), None
    assert frame_deck._cache_full_side != None, type(None)

    assert isinstance(frame_deck.full_cards_arquetype, int), None
    assert frame_deck._cache_full_arquetype != None, type(None)

    assert isinstance(frame_deck.full_cards_generic, int), None
    assert frame_deck._cache_full_generic != None, type(None)

    assert isinstance(frame_deck.full_cards_invalid, int), None
    assert frame_deck._cache_full_invalid != None, type(None)

    assert isinstance(frame_deck.full_cards_deck, int), None
    assert frame_deck._cache_full_cards != None, type(None)

def test_dict_deck():
    frame_ = frame(LINK)
    dados = frame_.get_dict_deck()
    assert isinstance(dados, str) == False, "Dados incorretos"
    assert isinstance(dados, dict) == True, "Dados incorretos"
