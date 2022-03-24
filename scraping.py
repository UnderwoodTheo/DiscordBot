import requests
import unidecode
import pymongo
import certifi

mongo_uri = 'mongodb+srv://tunderwood:JSmSGadJgeAlRW5n@cluster0.bzqiy.mongodb.net/chatbot?retryWrites=true&w=majority'
mongo_db = 'chatbot'
client = pymongo.MongoClient(mongo_uri, tlsCAFile=certifi.where())
database = client[mongo_db]
champions_col = database['champions']
items_col = database['items']


### scraping champions ###
list_of_champs = list()
championFull = requests.get('https://ddragon.leagueoflegends.com/cdn/12.5.1/data/en_US/championFull.json')
data = championFull.json()['data']
keys = ['name', 'description', 'cooldownBurn', 'costBurn']

website = requests.get('https://www.leagueoflegends.com/page-data/en-us/champions/page-data.json')
data2 = website.json()['result']['data']['allChampions']['edges']
links = {k['node']['champion_name']:'https://www.leagueoflegends.com/en-us'+k['node']['url'] for k in data2}

for c in data.values():
    champ = dict()
    champ['_id'] = int(c['key'])
    champ['name'] = c['name']
    champ['title'] = c['title']
    champ['role'] = c['tags']

    champ['spells'] = dict()
    champ['spells']['passive'] = {k:c['passive'][k] for k in c['passive'] if k in keys}
    champ['spells']['passive']['image'] = f'https://ddragon.leagueoflegends.com/cdn/12.5.1/img/passive/{c["passive"]["image"]["full"]}'
    
    champ['spells']['Q'] = {k:c['spells'][0][k] for s in c['spells'] for k in s if k in keys}
    champ['spells']['Q']['image'] = f'https://ddragon.leagueoflegends.com/cdn/12.5.1/img/spell/{c["spells"][0]["id"]}.png'

    champ['spells']['W'] = {k:c['spells'][1][k] for s in c['spells'] for k in s if k in keys}
    champ['spells']['W']['image'] = f'https://ddragon.leagueoflegends.com/cdn/12.5.1/img/spell/{c["spells"][1]["id"]}.png'

    champ['spells']['E'] = {k:c['spells'][2][k] for s in c['spells'] for k in s if k in keys}
    champ['spells']['E']['image'] = f'https://ddragon.leagueoflegends.com/cdn/12.5.1/img/spell/{c["spells"][2]["id"]}.png'

    champ['spells']['R'] = {k:c['spells'][3][k] for s in c['spells'] for k in s if k in keys}
    champ['spells']['R']['image'] = f'https://ddragon.leagueoflegends.com/cdn/12.5.1/img/spell/{c["spells"][3]["id"]}.png'

    champ['lore'] = c['lore']
    champ['image'] = f'http://ddragon.leagueoflegends.com/cdn/12.5.1/img/champion/{c["id"]}.png'
    
    new_str_champ = unidecode.unidecode(c['name'].replace(" ","").replace("'", "").lower())
    for k in links.keys():
        if unidecode.unidecode(k.replace(" ","").replace("'", "").lower()) == new_str_champ:
            champ['link'] = links[k]
    
    list_of_champs.append(champ)

'''with open('champions.json', 'w') as f:
    f.write(json.dumps(list_of_champs, indent = 4))

with open('champions.json', 'rb') as f:
    data = json.load(f)
    for line in data:
        champions_col.insert_one(line)'''


### scraping items ###
response = requests.get('https://ddragon.leagueoflegends.com/cdn/12.5.1/data/en_US/item.json')
data = response.json()['data']
keys = ['description', 'colloq', 'maps']
item = {k:data['1001'][k] for k in data['1001'].keys() if k not in keys}
item['image'] = item['image']['full']
all_items = list()

for k,v in data.items():
    item = dict()
    item['_id'] = int(k)
    item['name'] = v['name']
    item['description'] = v['plaintext']
    item['image'] = v['image']['full']
    if 'into' in v.keys():
        item['into'] = list(map(lambda x: int(x), v['into']))
    if 'from' in v.keys():
        item['from'] = list(map(lambda x: int(x), v['from']))
    item['gold'] = v['gold']
    item['tags'] = v['tags']
    item['stats'] = v['stats']
    
    all_items.append(item)

items_col.insert_many(all_items)