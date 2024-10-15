#
#   Python 3.11.10
#

import re
import struct
import base64
from typing import List, Dict


class CodeBase:
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
        if not all(key in deck for key in ['main', 'extra', 'side']):
            raise KeyError("Patter key 'main', 'extra' e 'side'.")

        return 'ydke://' + \
            self.__create_code_(deck['main']) + '!' + \
            self.__create_code_(deck['extra']) + '!' + \
            self.__create_code_(deck['side']) + '!'

    def read_url(self, ydke: str) -> Dict[str, List[int]]:
        """
        Converte uma URL YDKE em um dicionário com as três partes do deck.

        Args:
            ydke (str): A URL YDKE -> `'ydke://mainDeck!extraDeck!sideDeck!'`.

        Returns:
            (Dict[str, List[int]]): Um dicionário contendo três listas de inteiros,
                representando os decks 'main', 'extra' e 'side'.

        Raises:
            ValueError: Se a URL não começar com `'ydke://'` ou se não contiver 
                pelo menos três componentes separados por `'!'`.
        """
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

    def extract_urls(self, text: str) -> List[str]:
        """
        Extrai todas as URLs YDKE de um texto.

        Args:
            text (str): Texto que sera mapeado na verificacao.

        Returns:
            List[str]: Lista com link(s) dentro do texto.
        """
        pat = r'ydke:\/\/[A-Za-z0-9+/=]*![A-Za-z0-9+/=]*![A-Za-z0-9+/=]*!'
        ydke_pattern = re.compile(pat)
        return ydke_pattern.findall(text)


if __name__ == '__main__':
    codebase = CodeBase()
    
