import json

def search(target):
    with open('./set_recipe_chain.json', 'r', encoding='utf-8') as data:
        recipes = json.loads(data.read())

    used = set(('', 'earth', 'mountain', 'water', 'wind', 'thunder', 'fire', 'lake', 'sky'))
    chain = []
    names = [target]
    while len(names) > 0:
        temp_names = []
        for name in names:
            recipe = recipes[name]
            chain.append({
                'product': name,
                'materials': tuple(recipe)
            })

            used.add(name)

            for material in set(recipe):
                if material in used or material in temp_names or material in names:
                    continue

                temp_names.append(material)
            
        names = temp_names

    result = {}
    result['team_token'] = "2544876c41de80488474ee6f64b3f25d"
    result['target_product'] = target
    result['recipes'] = chain[::-1]
    return json.dumps(result, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    print(search(target=input('set할 element명: ')))