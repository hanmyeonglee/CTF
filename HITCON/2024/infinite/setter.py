import socks
import socket
import requests
import json
from time import sleep
import os

token = '2544876c41de80488474ee6f64b3f25d'
url = 'http://10.102.100.20:8000'
config = {
    'available': ['earth', 'mountain', 'water', 'wind', 'thunder', 'fire', 'lake', 'sky']
}

recipes = json.loads(open('./recipe_backup.backup.json', encoding='utf-8').read()) \
          if os.path.exists('./recipe_backup.backup.json') else {}

recipe_keys = set(recipes.keys())

def proxy():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9000)
    socket.socket = socks.socksocket
    print('Proxy Connected')

def store_recipe():
    with open('./recipe_backup.json', 'w', encoding='utf-8') as recipe:
        recipe.write(json.dumps(recipes, indent=1, ensure_ascii=False))
        recipe.flush()

def store_path():
    with open('./set_recipe_chain.json', 'w', encoding='utf-8') as setting:
        setting.write(json.dumps(shortest_recipes, indent=1, ensure_ascii=False))
        setting.flush()

def get_candidates():
    res = requests.get(
        url + '/my_inventory',
        params={
            'team_token': token
        }
    ).json()

    return [resp[0] for resp in res]

def set_recipe(element: str):
    global recipes

    res = requests.get(
        url + '/get_recipe',
        params={
            'team_token': token,
            'element': element
        }
    ).json()

    if 'recipe' not in res:
        return False

    recipes[element] = [resp['materials'] for resp in res['recipe']]
    return True

def set_recipes(candidates: list[str]):
    global recipe_keys

    for cand in candidates:
        if cand in recipe_keys:
            continue
        
        set_recipe(cand)
        store_recipe()
        print(cand)
        sleep(2)

def choose_set_elements(candidates: list[str], available_elements: list[str]):
    ret = {}
    for cand in candidates:
        try:
            RECIPES = recipes[cand]
        except KeyError:
            continue
        
        for recipe in RECIPES:
            if not all(material in available_elements for material in recipe):
                continue
            
            ret[cand] = recipe
            break
            
    return ret


if __name__ == "__main__":
    proxy()
    shortest_recipes = {}

    try:
        candidates = get_candidates()
        set_recipes(candidates)
        print('get recipe cache')

        for initial_element in config['available']:
            candidates.remove(initial_element)

        for cand in candidates:
            if cand not in recipe_keys:
                candidates.remove(cand)

        while True:
            ret = choose_set_elements(candidates, config['available'])
            shortest_recipes.update(ret)
            for element, _ in ret.items():
                candidates.remove(element)
                config['available'].append(element)

            print(len(ret))
            
            store_path()
            if len(ret) == 0:
                break
    finally:
        store_recipe()
        store_path()