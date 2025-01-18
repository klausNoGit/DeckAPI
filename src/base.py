import os
import json
import sqlite3
from pprint import pprint
from typing import List, Dict, Union
from datetime import datetime

import requests
import numpy as np
import pandas as pd

try:
    from card import CardGame, CardGameAsync
except:
    from src.card import CardGame, CardGameAsync
    

class CardInfoOfficial:
    def __init__(self, cod: Union[int, None] = None):
        self.cod: Union[int, None] = cod
        self.id: Union[int, None] = None
        self.name: Union[str, None] = None
        self.desc: Union[str, None] = None
        self.race: Union[str, None] = None
        self.type: Union[str, None] = None
        self.frame_type: Union[str, None] = None
        self.class_card: Union[str, None] = None
        self.attack: Union[str, None] = None
        self.defense: Union[str, None] = None
        self.arquetype_official: Union[str, None] = None
        self.arquetype_mc: Union[str, None] = None
        self.attribute: Union[str, None] = None
        self.level: Union[int, None] = None
        self.type_set: Union[List, None] = None
        self.url_target: Union[str, None] = None
        self.name_ygopro: Union[str, None] = None
        self.id_sets: Union[List, None] = None
        self.cardmarket_price: Union[str, None] = None
        self.tcgplayer_price: Union[str, None] = None
        self.ebay_price: Union[str, None] = None
        self.amazon_price: Union[str, None] = None
        self.coolstuffinc_price: Union[str, None] = None
        self.image_url: Union[str, None] = None
        self.image_url_small: Union[str, None] = None
        self.image_url_cropped: Union[str, None] = None
        
        self.info_card = self.__data_card_query()
        if self.info_card:
            for key, value in self.info_card.items():
                if hasattr(self, key):
                    setattr(self, key, value)

    def __data_card_query(self) -> Dict:
        """Query letter no dice bank cardgame.db e obtem as dictionary."""
        SRC = os.path.dirname(__file__)
        DATA = os.path.join(SRC, 'data')
        FILE_DB = os.path.join(DATA, 'cardgame.db')
        conx = sqlite3.connect(FILE_DB)
        cur = conx.cursor()
        query = f"""SELECT * FROM cards WHERE id = '{self.cod}'"""
        cur.execute(query)
        if datas := cur.fetchall():
            query = f"""PRAGMA table_info(cards)"""
            cur.execute(query)
            columns = [coluna[1] for coluna in cur.fetchall()]
            return dict(zip(columns, datas[0]))
        return {}

class CardBaseInfo:
    def __init__(self):
        self.SRC = os.path.dirname(__file__)
        self.directory_data = os.path.join(self.SRC, 'data')
        self.directory_json = os.path.join(self.SRC, 'json')
        self.path_file_data = os.path.join(self.directory_data, 'date.txt')
        self.date: str = str(datetime.now().strftime(r'%d/%m/%Y'))

        if not os.path.exists(self.path_file_data):
            with open(self.path_file_data, 'w', encoding='utf-8') as file:
                file.write(self.date)

        if not self.directory_data:
            os.mkdir(self.directory_data)

        if not self.directory_json:
            os.mkdir(self.directory_json)
        
        self.__update_db()

    def __load_api(self) -> np.ndarray:
        file_path = os.path.join(self.directory_json, 'data_cards_official.json')
        if os.path.exists(self.path_file_data):
            if os.path.exists(file_path):
                with open(self.path_file_data, 'r', encoding='utf-8') as file:
                    content = file.read().strip()
                
                data_fornecida = datetime.strptime(content, r'%d/%m/%Y')
                data_atual = datetime.now()
                diferenca = data_atual - data_fornecida
                dias_passados = diferenca.days
                if dias_passados > 10:
                    r = requests.get('https://db.ygoprodeck.com/api/v7/cardinfo.php')
                    if r.status_code == 200:
                        data = r.json()
                        data = data['data']

                    with open(file_path, 'w', encoding='utf-8') as file:
                        json.dump(data, file, ensure_ascii=False, indent=4)
                    
                    with open(self.path_file_data, 'w', encoding='utf-8') as file:
                        file.write(str(data_atual.strftime(r'%d/%m/%Y')))
                else:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
            else:
                r = requests.get('https://db.ygoprodeck.com/api/v7/cardinfo.php')
                if r.status_code == 200:
                    data = r.json()
                    data = data['data']

                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)

        return np.array(data)

    def __load_card_game_api(self) -> pd.DataFrame:
        with open(self.path_file_data, 'r', encoding='utf-8') as file:
            content = file.read().strip()
        
        data_fornecida = datetime.strptime(content, r'%d/%m/%Y')
        data_atual = datetime.now()
        diferenca = data_atual - data_fornecida
        dias_passados = diferenca.days
        if dias_passados > 10:
            card = CardGame()
            complet = card.request_frame()
            frame = card.mount_frame(complet)
            frame = frame[['cod', 'arquetype']].copy()
            frame['cod'] = frame['cod'].astype(int)
            return frame

        if not os.path.exists(os.path.join(self.SRC, 'cache')):
            card_game_async = CardGameAsync()
            sheets = ['min', 'complet', 'monster', 'spell', 'trap']
            if card_game_async.async_save_run(sheets):
                print('Async operation success!!!')
            else:
                print('Async operation not success!!!')
        
        complet = os.path.join(self.SRC, 'cache', 'complet.csv')
        if os.path.exists(complet):
            df = pd.read_csv(complet, sep=';', encoding='utf-8', skipinitialspace=True)
            df = df[['cod', 'arquetype']].copy()
            df['cod'] = df['cod'].astype(int)
            return df

    def __remove_db(self) -> None:
        src = os.path.dirname(__file__)
        directory_data = os.path.join(src, 'data')
        base = os.path.join(directory_data, 'cardgame.db')
        if os.path.exists(base):
            os.remove(base)

    def __unique_data(self, cards_off: np.ndarray, cards_complet: pd.DataFrame) -> np.ndarray:
        card = []
        for i in cards_off:
            i = dict(i)
            id = i.get('id')
            name = i.get('name')
            desc = i.get('desc')
            race = i.get('race')
            type_ = i.get('type')
            frame_type = i.get('frameType')
            class_card = i.get('humanReadableCardType')
            attack = i.get('atk')
            defense = i.get('def')
            arquetype_official = i.get('archetype')
            arquetype_mc = cards_complet.loc[cards_complet['cod'].isin([id])]
            arquetype_mc = arquetype_mc['arquetype'].values.tolist()
            arquetype_mc = arquetype_mc[0] if arquetype_mc else ''
            attribute = i.get('attribute')
            level = i.get('level')
            type_set = i.get('typeline')
            url_target = i.get('ygoprodeck_url')
            name_ygopro = str(url_target).replace('https://ygoprodeck.com/card/', '')
            card_prices = i.get('card_prices')[0]
            if isinstance(card_prices, dict):
                cardmarket_price = card_prices.get('cardmarket_price')
                tcgplayer_price = card_prices.get('tcgplayer_price')
                ebay_price = card_prices.get('ebay_price')
                amazon_price = card_prices.get('amazon_price')
                coolstuffinc_price = card_prices.get('coolstuffinc_price')

            data = {
                'id': id,
                'name': name,
                'desc': desc,
                'race': race,
                'type': type_,
                'frame_type': frame_type,
                'class_card': class_card,
                'attack': attack,
                'defense': defense,
                'arquetype_official': arquetype_official,
                'arquetype_mc': arquetype_mc,
                'attribute': attribute,
                'level': level,
                'type_set': ' | '.join(type_set) if isinstance(type_set, list) else None,
                'url_target': url_target,
                'name_ygopro': name_ygopro,
                'cardmarket_price': cardmarket_price,
                'tcgplayer_price': tcgplayer_price,
                'ebay_price': ebay_price,
                'amazon_price': amazon_price,
                'coolstuffinc_price': coolstuffinc_price,
                'id_sets': None,
                'image_url': None,
                'image_url_small': None,
                'image_url_cropped': None
            }

            card_images = i.get('card_images')
            if card_images:
                if len(card_images) > 1:
                    ids = map(lambda x: str(x['id']), card_images)
                    id_sets = '|'.join(ids).strip()
                    data['id_sets'] = id_sets
                    for d in card_images:
                        new_data = data.copy()
                        new_data['id'] = d['id']
                        new_data['image_url'] = d['image_url']
                        new_data['image_url_small'] = d['image_url_small']
                        new_data['image_url_cropped'] = d['image_url_cropped']
                        card.append(new_data)
                else:
                    dicio = card_images[0]
                    data['id_sets'] = str(data['id'])
                    data['image_url'] = dicio['image_url']
                    data['image_url_small'] = dicio['image_url_small']
                    data['image_url_cropped'] = dicio['image_url_cropped']
                    card.append(data)
        return card

    def __update_db(self) -> None:
        data_cards = self.__load_api()
        frame_complet = self.__load_card_game_api()
        set_cards = self.__unique_data(data_cards, frame_complet)
        
        df = pd.DataFrame(set_cards, columns=set_cards[0].keys())

        src = os.path.dirname(__file__)
        directory_data = os.path.join(src, 'data')
        base = os.path.join(directory_data, 'cardgame.db')
        conx = sqlite3.connect(base)
        df.to_sql(
            'cards',
            conx,
            if_exists='replace',
            index=False,
            dtype={
                'id': 'INTEGER PRIMARY KEY',
                'attack': 'INTEGER',
                'defense': 'INTEGER',
                'level': 'INTEGER',
                'cardmarket_price': 'REAL',
                'tcgplayer_price': 'REAL',
                'ebay_price': 'REAL',
                'amazon_price': 'REAL',
                'coolstuffinc_price': 'REAL'
            }
        )
        conx.commit()
        conx.close()

if __name__ == '__main__':
    SRC = os.path.dirname(__file__)
    DATA = os.path.join(SRC, 'data')
    date_file = os.path.join(DATA, 'date.txt')
    
    with open(date_file, 'r', encoding='utf-8') as file:
        content = file.read().strip()
    
    data_fornecida = datetime.strptime(content, r'%d/%m/%Y')
    data_atual = datetime.now()
    diferenca = data_atual - data_fornecida
    dias_passados = diferenca.days
    
    # if dias_passados > 10:
    card = CardBaseInfo()

    card_info = CardInfoOfficial(60800381)
    print(card_info.info_card)
