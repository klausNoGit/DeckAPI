#
# Python 3.11.10
#
# Pytest 8.3.3
#
import os
import pytest
from src.ydke import CoreYDKE

@pytest.fixture()
def ydk():
    return CoreYDKE()

def test_ydke_to_url(ydk):
    # cartas do dogmatica
    deck = {
        'main': [69680031, 95679145, 60303688],
        'extra': [93053159, 24915933, 41373230],
        'side': [99735427, 14087893, 67750322]
    }
    
    link = ydk.to_url(deck)
    assert isinstance(link, str), "O retor nao foi string"
    assert 'ydke://' in link, "Nao e um link valido"
    del deck['main']
    
    # Deve gerar um error na funcao
    error = ydk.to_url(deck)
    assert isinstance(error, str), f"{error} nao e string"
    assert 'Patter key' in error, "Error nao deu error"

def test_ydke_read_url(ydk):
    # tem que da sucesso na funcao
    deck_ex = """
        ydke://T+rhBE/q4QRP6uEEZkhVA2ZIVQNmSFUDSNtkAEjbZAAtTsoALU7KAC1OygDMvQQD
        zL0EA4/c4wSP3OMETRcqAU0XKgFNFyoBsPMNAaBT8QKgU/ECoFPxArqWmgK6lpo
        CsskJBLLJCQRO93UBTvd1AbIyzAWyMswFJjzNASY8zQH
        jsCoDWXtjBO8nUQDvJ1EA1fbWANX21gDV9tYArmAJBA==!Vm8XAVZvFwF
        WbxcBOjGqAjoxqgI6MaoCWmixAVposQHKg4kC1m/tA9H6jAXKP2AB
        Ebm4BRHqPQTrK/8C!7I8BAOyPAQDsjwEAWmHoBSbrAATvJ1EAo2rUAqNq
        1ALDLy0Ewy8tBCHuLQMh7i0DIe4tA4PX8QWD1/EF!
    """
    deck_ex = deck_ex.replace(' ', '').replace('\n', '').replace('\t', '')
    deck = ydk.read_url(deck_ex)
    assert isinstance(deck, dict), f"{deck}, nao e um dicionario"
    assert isinstance(deck['main'], list), "Nao e uma lista de inteiros"
    assert isinstance(deck['extra'], list), "Nao e uma lista de inteiros"
    assert isinstance(deck['side'], list), "Nao e uma lista de inteiros"

    # tem que da error na funcao
    protocol = deck_ex.replace('ydke://', '')
    assert 'URL protocol' in ydk.read_url(protocol), "Protocolo sem alvo"
    component = deck_ex.replace('!', '#')
    assert 'URL component' in ydk.read_url(component), "Componente sem alvo"


def test_ydke_extract_urls(ydk):
    deck = """
        ydke://sO3fAhdb8gOKGRAFIE7rBYk4dAT4NdICKfasACdEqwBOE4UEZV2NADUz/
        ADxvpsBAr8WAA==!6QYzAg==!!
    """
    deck = deck.replace(' ', '').replace('\n', '').replace('\t', '')
    texto = """
        No coração da floresta, as árvores sussurravam segredos antigos ao
        vento. Um riacho serpenteava pelo terreno, refletindo o brilho do sol 
        que filtrava entre as folhas. Pássaros coloridos dançavam no céu,
        preenchendo o ar com melodias suaves. Em meio a esse cenário, uma
        pequena clareira revelava flores silvestres em plena floração. A
        natureza, com sua beleza exuberante, convidava todos a desacelerar e
        apreciar o momento.
    """
    texto = texto.replace('\n', '').replace('\t', '')
    texto_random = texto.replace(' ', deck)
    result_falso = ydk.extract_urls(texto)
    result_true  = ydk.extract_urls(texto_random)

    # deve retornar lista vazia
    assert isinstance(result_falso, list), "Nao retornou uma lista vazia"
    assert [] == result_falso, "Nao e uma lista vazia"
    
    # deve retorna os links
    assert isinstance(result_true, list), "Nao retornou uma lista"
    assert len(result_true) > 0, "Nenhum link encontrado"

def test_ydke_read_file_deck(ydk):
    # deve falhar
    path_false = 'test/test.txt'
    result = ydk.read_file_deck(path_false)
    assert isinstance(result, str), "Nao gerou uma excessao"
    assert 'not accessible' in result
    
    test = os.path.dirname(__file__)
    arq_false = str(test).replace('test', 'decks/_deck_false.txt')
    result = ydk.read_file_deck(arq_false)
    assert isinstance(result, str), "Nao gerou uma excessao"
    assert 'Not a ydk file:' in result, "Error desconhecido"
    
    # deve funcionar perfeitamente
    arq_true = str(test).replace('test', 'decks/_dogmatica.ydk')
    result = ydk.read_file_deck(arq_true)
    assert isinstance(result, dict), "Nao gerou um dicionario"
    assert isinstance(result['created'], str), "Nao e uma string"
    assert isinstance(result['main'], list), "Nao e uma lista python"
    assert isinstance(result['extra'], list), "Nao e uma lista python"
    assert isinstance(result['side'], list), "Nao e uma lista python"
