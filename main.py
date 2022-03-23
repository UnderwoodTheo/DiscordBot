from datetime import datetime
import string
from xmlrpc.client import ResponseError
from aiohttp import request
from matplotlib import projections
from matplotlib.style import available
import requests
import json
import io
import unidecode
import numpy as np
import datetime

apiKey = 'RGAPI-f87d589e-8753-48b9-a0ef-2e5d4866bb03'


def query(request):
    try:
        response = requests.get(f'https://euw1.api.riotgames.com{request}?api_key={apiKey}')
        # display as json format
        # text = json.dumps(response.json(), sort_keys=True, indent=4)
        return response.json()
    except:
        print(NameError)


def summonerByName(summonerName: string) -> dict:
    """
    Returns dict

    dict keys:
    id
    accountId
    puuid
    name
    profileIconId
    revisionDate
    summonerLevel
    """
    return query(f'/lol/summoner/v4/summoners/by-name/{summonerName}')

def rank(summonerId: string = '6LIB1nPoIKKuzIfAGrMrn8OgjNu_nEFnUyR2AHwMRsc3OsM') -> list:
    """
    Returns list of dicts

    first list: solo/duo
    second list: flex

    dict keys:
    leagueId, queueType, tier, rank, summonerId, summonerName, leaguePoints, wins,
    losses, veteran, inactive, freshBlood, hotStreak
    """
    return query(f'/lol/league/v4/entries/by-summoner/{summonerId}')

def masteryScore(summonerId: string = '6LIB1nPoIKKuzIfAGrMrn8OgjNu_nEFnUyR2AHwMRsc3OsM') -> int:
    """
    Returns total champion mastery score
    """         
    return query(f'/lol/champion-mastery/v4/scores/by-summoner/{summonerId}')

def championMasteries(summonerId: string = '6LIB1nPoIKKuzIfAGrMrn8OgjNu_nEFnUyR2AHwMRsc3OsM', championId: int = None) -> list:
    """
    Returns champion masteries by number of champion points in descending order
    """
    if(championId):
        resp = query(f'/lol/champion-mastery/v4/champion-masteries/by-summoner/{summonerId}/by-champion/{championId}')
    else:
        resp = query(f'/lol/champion-mastery/v4/champion-masteries/by-summoner/{summonerId}')
    return resp

def freeChampions(newPlayer: bool = False) -> list:
    """
    Returns weakly free champions rotation
    """
    resp = query(f'/lol/platform/v3/champion-rotations')
    if(newPlayer):
        return resp['freeChampionIdsForNewPlayers']
    return resp['freeChampionIds']
    
def status() -> dict:
    resp = query(f'/lol/status/v4/platform-data')

    maintenances = resp['maintenances']
    contents = []
    for m in maintenances:
        for t in m['updates'][0]['translations']:
            if(t['locale']=='en_GB'):
                contents.append(t['content'])
    maintenancesList = ''
    for c in contents:
        maintenancesList += f'\t{c}\n'
    maintenancesDisplay = f'Maintenances:\n{maintenancesList}'

    incidents = resp['incidents']
    contents2 = []
    for i in incidents:
        for t in i['updates'][0]['translations']:
            if(t['locale']=='en_GB' or t['locale']=='en_US'):
                contents2.append(t['content'])
    incidentsList = ''
    for c in contents2:
        incidentsList += f'\t{c}\n'
    incidentsDisplay = f'Incidents:\n{incidentsList}'

    return maintenancesDisplay + '\n\n' + incidentsDisplay

def currentVersion() -> string:
    """
    Returns the current version of LoL
    """
    try:
        response = requests.get(f'https://ddragon.leagueoflegends.com/api/versions.json')
        # display as json format
        # text = json.dumps(response.json(), sort_keys=True, indent=4)
        return response.json()[0]
    except:
        print(NameError)

import pymongo
import certifi

mongo_uri = 'mongodb+srv://tunderwood:JSmSGadJgeAlRW5n@cluster0.bzqiy.mongodb.net/chatbot?retryWrites=true&w=majority'
mongo_db = 'chatbot'
client = pymongo.MongoClient(mongo_uri, tlsCAFile=certifi.where())
database = client[mongo_db]
champions_col = database['champions']
items_col = database['items']

def getChampFromMongo(champ: str = "") -> dict:
    query = {}
    new_str_champ = unidecode.unidecode(champ.replace(" ","").replace("'", "").lower())
    names = champions_col.find({}, {'name':1, '_id':0})
    for n in names:
        if unidecode.unidecode(n['name'].replace(" ","").replace("'", "").lower()) == new_str_champ:
            query = {'name': n['name']}
    result = champions_col.find(query)
    return result[0]

def getChampByIdMongo(id: int):
    result = champions_col.find({'_id':id})
    return result[0]

def isChestGranted(summonerName, champName) -> bool:
    granted = False
    summoner_id = summonerByName(summonerName)['id']
    champ_info = getChampFromMongo(champName)
    champ_id = champ_info['_id']
    all_champs = championMasteries(summoner_id)
    for champ in all_champs:
        if champ['championId'] == champ_id:
            if champ['chestGranted'] == True:
                granted = True
    return granted

def emblemUrl(tier):
    emblems = dict()
    emblems['IRON'] = 'https://static.wikia.nocookie.net/leagueoflegends/images/f/fe/Season_2022_-_Iron.png/revision/latest/scale-to-width-down/130?cb=20220105213520'
    emblems['BRONZE'] = 'https://static.wikia.nocookie.net/leagueoflegends/images/e/e9/Season_2022_-_Bronze.png/revision/latest/scale-to-width-down/130?cb=20220105214224'
    emblems['SILVER'] = 'https://static.wikia.nocookie.net/leagueoflegends/images/4/44/Season_2022_-_Silver.png/revision/latest/scale-to-width-down/130?cb=20220105214225'
    emblems['GOLD'] = 'https://static.wikia.nocookie.net/leagueoflegends/images/8/8d/Season_2022_-_Gold.png/revision/latest/scale-to-width-down/130?cb=20220105214225'
    emblems['PLATINUM'] = 'https://static.wikia.nocookie.net/leagueoflegends/images/3/3b/Season_2022_-_Platinum.png/revision/latest/scale-to-width-down/130?cb=20220105214225'
    emblems['DIAMOND'] = 'https://static.wikia.nocookie.net/leagueoflegends/images/e/ee/Season_2022_-_Diamond.png/revision/latest/scale-to-width-down/130?cb=20220105214226'
    emblems['MASTER'] = 'https://static.wikia.nocookie.net/leagueoflegends/images/e/eb/Season_2022_-_Master.png/revision/latest/scale-to-width-down/130?cb=20220105214311'
    emblems['GRANDMASTER'] = 'https://static.wikia.nocookie.net/leagueoflegends/images/f/fc/Season_2022_-_Grandmaster.png/revision/latest/scale-to-width-down/130?cb=20220105214312'
    emblems['CHALLENGER'] = 'https://static.wikia.nocookie.net/leagueoflegends/images/0/02/Season_2022_-_Challenger.png/revision/latest/scale-to-width-down/130?cb=20220105214312'

    return emblems[tier]

def mostPlayed(summonerName: str) -> list:
    summoner_id = summonerByName(summonerName)['id']
    all_champs = championMasteries(summoner_id)
    ids = list(map(lambda x: x['championId'], all_champs[:3]))
    names = []
    for id in ids:
        name = champions_col.find({'_id':id}, {'name':1, '_id':0})
        names.append(name[0]['name'])
    points = list(map(lambda x: x['championPoints'], all_champs[:3]))
    top_played = list(zip(names, points))
    return top_played

def champsByRole() -> dict:
    result = champions_col.find({}, {'name':1, 'role':1, '_id':0})
    all_champs = []
    for r in result:
        all_champs.append(r)
    roles = np.unique(list(map(lambda x: x['role'][0], all_champs)))
    champs_by_role = {r:[] for r in roles}
    for c in all_champs:
        champs_by_role[c['role'][0]].append(c['name'])
    return champs_by_role

def summonerSpells() -> list:
    response = requests.get('https://ddragon.leagueoflegends.com/cdn/12.5.1/data/en_US/summoner.json')
    data = response.json()['data']
    classic_spells = dict()
    for k,v in data.items():
        if 'CLASSIC' in v['modes']:
            classic_spells[k] = v
    deleted_keys = ['maxrank', 'image', 'cooldown', 'cost', 'vars', 'summonerLevel', 'modes', 'costType', 'maxammo', 'range', 'rangeBurn', 'resource', 'tooltip', 'costBurn', 'datavalues', 'effect', 'effectBurn']
    for d in deleted_keys:
        for v in classic_spells.values():
            if d in v.keys():
                v.pop(d)
    '''for k,v in classic_spells.items():
        v['image'] = v['image']['full']'''
    list_spells = [v for v in classic_spells.values()]
    return list_spells

def getItemFromMongo(id: int) -> dict:
    item = items_col.find({'_id': id})
    return item[0]

def getItems() -> list:
    items = items_col.find(projection={'_id':1, 'name':1})
    all_items = [i for i in items]
    return all_items

# 1- recupere uuid avec nom invocateur
# 2- recupere 3 dernieres games avec uuid
# 3- 

# info game: 
# - durée
# - map id -> map

def history(summonerName: str) -> dict:
    summoner_puuid = summonerByName(summonerName)['puuid']
    games_id = requests.get(f'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner_puuid}/ids?api_key={apiKey}').json()[:3]
    games = [requests.get(f'https://europe.api.riotgames.com/lol/match/v5/matches/{game_id}?api_key={apiKey}').json() for game_id in games_id]
    indexes = [game['metadata']['participants'].index(summoner_puuid) for game in games]
    games_stats = [game['info']['participants'][index] for game, index in list(zip(games, indexes))]
    keys = ['assists', 'kills', 'lane', 'deaths', 'championName', 'summonerName', 'championId', 'summoner1Id', 'summoner2Id', 'teamId', 'totalDamageDealtToChampions', 'totalMinionsKilled', 'totalTimeSpentDead', 'win']
    new_games_stats = [{k:g[k] for k in g.keys() if k in keys} for g in games_stats]
    for a,b in zip(new_games_stats, games):
        a['mapId'] = b['info']['mapId']
        a['gameMode'] = b['info']['gameMode']
        a['gameType'] = b['info']['gameType']
        a['duration'] = str(datetime.timedelta(seconds=b['info']['gameDuration']))
    return new_games_stats

def getMap(mapId: int):
    response = requests.get('https://static.developer.riotgames.com/docs/lol/maps.json')
    for i in response.json():
        if i['mapId'] == mapId:
            return i['mapName']

def getSpell(idSpell: int):
    spells = summonerSpells()
    for s in spells:
        if s['key'] == str(idSpell):
            return s['name']