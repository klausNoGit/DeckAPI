#
# Python 3.11.10
#
# Pytest 8.3.3
#
import pytest
import asyncio
from src.ban import BanSheetWeb, BanSheetWebAsync

@pytest.fixture()
def ban():
    return BanSheetWeb()

@pytest.fixture()
def ban_async():
    return BanSheetWebAsync()

# Testes para BanSheetWeb (sincrono)
def test_ban_initialization(ban):
    assert isinstance(ban, BanSheetWeb), "A instância não foi inicializada."

def test_ban_get_end_point(ban):
    result = ban.get_end_point()
    assert isinstance(result, dict), f"Esperado: {dict}, mas obteve: {result}"
    assert 'sheet' in result, 'Nao encontrada a folha'
    assert 'token' in result, 'Nao encontrado o token'
    assert 'point' in result, 'Nao encontrado o endpoint'

def test_ban_request_frame(ban):
    r = ban.request_frame() # Requisicao ao end-point padrao (Home)
    assert 'error' not in r, f'Error : {r}'
    assert 'Home' not in r, f'Existe chave Home em {r}'
    assert 'folha' in r, f'Nao existe a chave "Folha"'


# Testes para BanSheetWebAsync (assíncrono)
def test_ban_async_initialization(ban_async):
    assert isinstance(ban_async, BanSheetWebAsync), "A instância não foi inicializada."

@pytest.mark.asyncio
async def test_ban_async_creat_files(ban_async):
    s = ['Home', 'Forbidden', 'Limited', 'Semi-limited', 'Unlimited']
    result = await ban_async.creat_files(s)
    assert isinstance(result, bool)
    assert result == True, f"Esperado: {True}, mas obteve: {result}"
    assert result != False, f"Esperado: {True}, mas obteve: {result}"
