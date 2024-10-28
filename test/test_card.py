#
# Python 3.11.10
#
# Pytest 8.3.3
#
import pytest
from src.card import CardGame, CardGameAsync

@pytest.fixture()
def card():
    return CardGame()

@pytest.fixture()
def card_async():
    return CardGameAsync()

# Testes para CardGame (sincrono)
def test_card_initialization(card):
    assert isinstance(card, CardGame), "A instância não foi inicializada."

def test_card_get_end_point(card):
    result = card.get_end_point()
    assert isinstance(result, dict), f"Esperado: {dict}, mas obteve: {result}"
    assert 'sheet' in result, 'Nao encontrada a folha'
    assert 'token' in result, 'Nao encontrado o token'
    assert 'point' in result, 'Nao encontrado o endpoint'

def test_card_request_frame(card):
    r = card.request_frame() # Requisicao ao end-point padrao (complet)
    assert 'error' not in r, f'Error : {r}'
    assert 'folha' not in r, f'Nao existe a chave "Folha"'
    assert 'complet' in r, f'Existe chave complet em {r}'


# Testes para CardGameAsync (assíncrono)
def test_card_async_initialization(card_async):
    assert isinstance(card_async, CardGameAsync), "A instância não foi inicializada."

@pytest.mark.asyncio
async def test_card_async_creat_files(card_async):
    s = ['complet', 'monster', 'spell', 'trap']
    result = await card_async.creat_files(s)
    assert isinstance(result, bool)
    assert result == True, f"Esperado: {True}, mas obteve: {result}"
    assert result != False, f"Esperado: {True}, mas obteve: {result}"
