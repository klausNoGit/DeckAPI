#
# Python 3.11.10
#
import re
import os
from typing import List, Dict, Tuple, Union, Literal

import pandas as pd
import numpy as np

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

    def download_mesa(self) -> bool:
        sheet_ban = ['Forbidden', 'Limited', 'Semi-limited', 'Unlimited']
        sheet_card = ['min', 'complet', 'monster', 'spell', 'trap']
        return all([
            self.__CARD_GAME_ASYNC__.async_save_run(sheet_card),
            self.__BANLIST_WEB__.request_frame(),
            self.__BANLIST_ASYNC__.async_download_run(sheet_ban)
        ])

if __name__ == '__main__':
    mesa_core = MesaCore()
    mesa_core.download_mesa()
