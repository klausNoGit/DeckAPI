#
#   Python 3.11.10
#
import os
import re
import struct
import base64

from os import PathLike
from typing import List, Dict, Union


class CoreYDKE:
    def __to_pass_code_(self, base64_str: str) -> List[int]:
        """
        Converte uma string codificada em base64 para uma lista
        de inteiros de 32 bits `(little-endian)`.

        Args:
            base64_str (str): Código do deck.

        Returns:
            List[int]: Uma lista de inteiros de 32 bits.

        Raises:
            struct.error: Se a decodificação ou desempacotamento dos bytes falhar.
            binascii.Error: Se a string base64 for malformada.
        """
        byte_data = base64.b64decode(base64_str)
        return list(struct.unpack("<" + "I" * (len(byte_data) // 4), byte_data))

    def __create_code_(self, passcodes: List[int]) -> str:
        """
        Converte uma lista de inteiros de 32 bits para uma string codificada em base64.

        A função usa o módulo `struct` para empacotar os inteiros de 32 bits em bytes,\n 
        e em seguida, usa a codificação base64 para converter os bytes em uma string.

        Args:
            passcodes (List[int]): Uma lista de inteiros de 32 bits.

        Returns:
            str: A string codificada da conversão dos inteiros de 32 bits.

        Raises:
            struct.error: Se o empacotamento dos inteiros em bytes falhar.
        """
        byte_data = struct.pack("<" + "I" * len(passcodes), *passcodes)
        return base64.b64encode(byte_data).decode('utf-8')

    def to_url(self, deck: Dict[str, List[int]]) -> str:
        """
        Converte um dicionário de deck em uma URL YDKE.

        Args:
            deck (Dict[str, List[int]]): Um dicionário contendo três listas de inteiros, 
                representando os decks 'main', 'extra', e 'side'.

        Returns:
            str: A URL YDKE gerada a partir das listas de inteiros.

        Raises:
            KeyError: Patter key 'main', 'extra' e 'side'.
        """
        try:
            if not all(key in deck for key in ['main', 'extra', 'side']):
                raise KeyError("Patter key 'main', 'extra' e 'side'.")

            return 'ydke://' + \
                self.__create_code_(deck['main']) + '!' + \
                self.__create_code_(deck['extra']) + '!' + \
                self.__create_code_(deck['side']) + '!'
        except KeyError as e:
            return str(e)

    def read_url(self, ydke: str) -> Dict[str, List[int]] | str:
        """
        Converte uma URL YDKE em um dicionário com as três partes do deck.

        Args:
            ydke (str): A URL YDKE -> `'ydke://mainDeck!extraDeck!sideDeck!'`.

        Returns:
            -Dict[str, List[int]] | str: Um dicionário contendo três listas de inteiros,
                representando os decks `'main', 'extra'` e `'side'`. Ou String de `error`.

        Raises:
            ValueError: Se a URL não começar com `'ydke://'` ou se não contiver\n
                pelo menos três componentes separados por `'!'`.
        """
        try:
            if not ydke.startswith("ydke://"):
                raise ValueError("Unrecognized URL protocol")

            components = ydke[len("ydke://"):].split("!")
            if len(components) < 3:
                raise ValueError("Missing ydke URL component")

            return {
                "main": self.__to_pass_code_(components[0]),
                "extra": self.__to_pass_code_(components[1]),
                "side": self.__to_pass_code_(components[2])
            }
        except ValueError as e:
            return str(e)

    def extract_urls(self, text: str) -> List[str] | List:
        """
        Extrai todas as URLs YDKE de um texto.

        Args:
            text (str): Texto que sera mapeado na verificacao.

        Returns:
            List[str]: Lista com link(s) dentro do texto.
        """
        pat = r'ydke:\/\/[A-Za-z0-9+/=]*![A-Za-z0-9+/=]*![A-Za-z0-9+/=]*!'
        ydke_pattern = re.compile(pat)
        result = ydke_pattern.findall(text)
        return list(map(lambda x: str(x), result)) if result else []

    def read_file_deck(self, file: Union[str, PathLike]) -> Dict[str, List[int]] | str:
        """
        Lê um arquivo `.ydk` de deck e retorna suas informações em um\n
        dicionário estruturado ou uma string de erro.

        O arquivo deve conter:
        - `#created by ` seguido do nome do criador.
        - Seções `#main`, `#extra` e `!side` listando os códigos das cartas.

        Args:
            file (Union[str, PathLike]): Caminho para o arquivo `.ydk`.

        Returns:
            (Dict[str, List[int]] | str): 
                - Chaves: 'created', 'main', 'extra', 'side' e códigos das cartas.
                - String de erro em caso de falha.

        Exemplo:
            >>> read_file_deck("exemplo.ydk")
            {'created': 'Criador', 'main': [123], 'extra': [456], 'side': [789]}
        """
        try:
            abs_file = str(os.path.abspath(file))
            if not os.path.exists(abs_file):
                raise ValueError(f'{file} not accessible')

            _, extensao = os.path.splitext(abs_file)
            if '.ydk' != extensao:
                raise ValueError(f'Not a ydk file: {extensao}')

            with open(abs_file, 'r', encoding='utf-8') as deck_file:
                deck = deck_file.readlines()

            # Constantes do arquivo
            name = deck[0].replace('#created by ', '').replace('\n', '')
            imain = deck.index('#main\n')
            iextra = deck.index('#extra\n')
            iside = deck.index('!side\n')

            main = [] if imain == 1 and iextra == 2 else deck[imain+1:iextra]
            extra = [] if iextra == 2 and iside == 3 else deck[iextra+1:iside]
            side = [] if iside == len(deck)-1 else deck[iside+1:]

            fun_number = lambda x: int(str(x).replace('\n', ''))
            return {
                'created' : name,
                'main': list(map(fun_number, main)),
                'extra': list(map(fun_number, extra)),
                'side': list(map(fun_number, side))
            }
        except Exception as e:
            return str(e)

if __name__ == '__main__':
    base_ydke = CoreYDKE()
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
    dicio = base_ydke.read_url(deck_ex)
    if isinstance(dicio, Dict):
        print('Decode Kernel Operation!!')
        link = base_ydke.to_url(dicio)
        if 'Patter key' in link:
            print('Not Decode!!!')
        else:
            print('YDKE Kernel Operation!!')
    else:
        print(f'Not Decode Kernel Operation!!')
